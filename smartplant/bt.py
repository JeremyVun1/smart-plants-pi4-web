import json
import bluetooth
from bluetooth import *
from select import select
import time
from smartplant import db
from .models import SmartPlantDevice
from .util import readLine


def createBtSocket(addr, port=1):
    print(f'Creating bt socket with addr: {addr} port: {port}')
    socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    socket.connect((addr, port))
    return socket


def fetchDeviceQueryResponse(addr):
    socket = createBtSocket(addr)

    socket.send(int(8).to_bytes(1, "little")) # concert int code into byte
    time.sleep(1)
    response = readLine(socket)
    print(response)
    response = json.loads(response)
    socket.close()
    return response


def find_new_smartplant_devices():
    print("finding new smartplant devices...")
    found_smartplants = []

    nearby_devices = bluetooth.discover_devices()
    print(f"nearby devices: {nearby_devices}")
    for addr in nearby_devices:
        device_record = SmartPlantDevice.query.get(addr)

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


def connect_smartplant_devices():
    time.sleep(2)
    smartPlants = SmartPlantDevice.query.filter_by(isSmartPlant=True).all()

    sockets = {}
    for sp in smartPlants:
        sockets[sp.mac] = createBtSocket(sp.mac, 1)

    print(f"connected sockets: {sockets}")
    return sockets


def close_sockets(sockets):
    try:
        for mac in sockets:
            sockets[mac].close()
    except Exception:
        print("could not close socket")


def request_plant_state(socket):
    socket.send(int())


def request_full_state(sockets):
    responses = []

    # send all the requests
    for mac in sockets:
        sockets[mac].send(int(0).to_bytes(1, "little"))
        time.sleep(1.5)
        response = json.loads(readLine(sockets[mac]))
        print(response)
        responses.append(response)

    return responses


def send_pump_commands(socket, curr_state, form_state):
    print("sending pump commands")
    print(curr_state)
    print(form_state)
    # pump toggle mode between auto/manual
    if form_state['pumpMode'] != curr_state.pumpmode:
        socket.send(int(1).to_bytes(1, "little"))

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
    print(curr_state)
    print(form_state)
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