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
    print(addr)
    socket = createBtSocket(addr)

    code = int(8)
    socket.send(code.to_bytes(1, "little")) # concert int code into byte
    response = readLine(socket)
    print(response)
    response = json.loads(response)
    socket.close()
    return response


def find_new_smartplant_devices():
    print("finding new smartplant devices...")
    found_smartplants = []

    nearby_devices = bluetooth.discover_devices()
    print(nearby_devices)
    for addr in nearby_devices:
        device_record = SmartPlantDevice.query.get(addr)

        # device is not known
        if device_record is None:
            response = fetchDeviceQueryResponse(addr)
            print("HELLO HELLO HELLO")
            print(response)
            print(response['d'])
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
    print("connecting smart plant devices")
    smartPlants = SmartPlantDevice.query.filter_by(isSmartPlant=True).all()

    sockets = []
    for sp in smartPlants:
        sockets.append(createBtSocket(sp.mac, 1))

    print(f"connected sockets: {sockets}")
    return sockets


def close_sockets(sockets):
    try:
        for socket in sockets:
            socket.close()
    except Exception:
        print("could not close socket")


def request_plant_state(socket):
    socket.send(int())


def request_full_state(sockets):
    print("requesting full states")
    print(sockets)
    responses = []

    # send all the requests
    for socket in sockets:
        socket.send(int(0).to_bytes(1, "little"))
        response = readLine(socket)
        print(response)
        response = json.loads(response)
        print(response)
        responses.append(response)

    return responses
