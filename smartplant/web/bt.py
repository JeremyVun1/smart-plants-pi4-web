import bluetooth
import json
import time

from .util import read_line, is_query_response
from smartplant.models import SmartPlantDevice
from smartplant.database import db


def createBtSocket(addr, port=1):
    print(f'Creating bt socket with addr: {addr} port: {port}')
    socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    socket.connect((addr, port))
    return socket


def fetchDeviceQueryResponse(addr):
    time.sleep(0.5)
    socket = createBtSocket(addr)

    timeout_counter = 0
    socket.send(int(8).to_bytes(1, "little"))  # concert int code into byte

    buffer = read_line(socket)
    while (not is_query_response(buffer) and timeout_counter < 50):
        buffer = read_line(socket)
        timeout_counter = timeout_counter + 1

    response = json.loads(buffer)
    socket.close()
    return response


def find_new_smartplant_devices():
    print("finding new smartplant devices...")
    found_smartplants = []

    
    nearby_devices = bluetooth.discover_devices(duration=4)
    print(f"nearby devices: {nearby_devices}")
    for addr in nearby_devices:
        device_record = SmartPlantDevice.query.get(addr)
        print(device_record)

        # device is not known
        if device_record is None:
            response = fetchDeviceQueryResponse(addr)
            isSmartPlant = response['d'] == "y"

            device = SmartPlantDevice(mac=addr, guid=response['g'], isConnected=True, isSmartPlant=isSmartPlant)
            db.session.add(device)
            db.session.commit()

            if isSmartPlant:
                print(f"{addr} Smart Plant found")
                found_smartplants.append(addr)

    return found_smartplants


# try to connect to all known smart plants and return bt sockets
def connect_smartplant_devices(app=None):
    if app:
        with app.app_context():
            time.sleep(2)
            smartplants = SmartPlantDevice.query.filter(SmartPlantDevice.isSmartPlant == True).all()

            sockets = {}
            for sp in smartplants:
                sockets[sp.mac] = createBtSocket(sp.mac, 1)

            print(f"connected sockets: {sockets}")
            return sockets
    else:
        time.sleep(2)
        smartplants = SmartPlantDevice.query.filter(SmartPlantDevice.isSmartPlant == True).all()

        sockets = {}
        for sp in smartplants:
            sockets[sp.mac] = createBtSocket(sp.mac, 1)

        print(f"connected sockets: {sockets}")
        return sockets


def request_plant_state(socket):
    socket.send(int())


def request_full_state(sockets):
    try:
        responses = []

        # send all the requests
        for mac in sockets:
            # clear the buffer
            buffer = read_line(sockets[mac])
            while (read_line(sockets[mac])):
                buffer = read_line(sockets[mac])
                continue

            sockets[mac].send(int(0).to_bytes(1, "little"))
            time.sleep(1)
            response = json.loads(read_line(sockets[mac]))
            print(response)
            responses.append(response)

        return responses
    except Exception:
        return None


def send_pump_commands(socket, curr_state, form_state):
    print("sending pump commands")
    # pump toggle mode between auto/manual
    if 'pumpMode' in form_state and form_state['pumpMode'] != curr_state.pumpmode:
        if form_state['pumpMode'] == 'a':
            mode_code = int(1).to_bytes(1, "little")
        else:
            mode_code = int(0).to_bytes(1, "little")
        socket.send(int(1).to_bytes(1, "little"))
        socket.send(mode_code)


    # pump on/off
    if curr_state.pumpstate and 'pumpOn' not in form_state:
        socket.send(int(3).to_bytes(1, "little"))
    elif 'pumpOn' in form_state and not curr_state.pumpstate and form_state['pumpOn']:
        socket.send(int(2).to_bytes(1, "little"))

    # pump speed
    if curr_state.pumpspeed != form_state['pumpSpeed']:
        socket.send(int(4).to_bytes(1, "little"))
        socket.send(int(form_state['pumpSpeed']).to_bytes(1, "little"))


def send_light_commands(socket, curr_state, form_state):
    print("sending light commands")
    # light on/off
    if curr_state.lightstate and 'lightOn' not in form_state:
        socket.send(int(6).to_bytes(1, "little"))
    elif 'lightOn' in form_state and not curr_state.lightstate and form_state['lightOn']:
        socket.send(int(5).to_bytes(1, "little"))
    
    # light mode
    if curr_state.lightmode != form_state['lightMode']:
        socket.send(int(7).to_bytes(1, "little"))
        if form_state['lightMode'] == 'l':
            socket.send(int(0).to_bytes(1, "little"))
        elif form_state['lightMode'] == 'm':
            socket.send(int(1).to_bytes(1, "little"))
        else:
            socket.send(int(2).to_bytes(1, "little"))
