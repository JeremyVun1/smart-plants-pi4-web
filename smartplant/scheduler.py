from datetime import datetime
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import bluetooth

from .util import readLine
from smartplant import sockets
'''
from smartplant import db
from smartplant import model
'''


def handle_device_events():

    '''
    # check if our devices have disconnnected
    nearby_devices = bluetooth.discover_devices()
    devices = model.SmartPlantDevice.query.all()
    for device in devices:
        if not (device.mac in nearby_devices):
            device.isConnected = False
    
    db.session.commit()
    '''

    # read from all sockets
    for socket in sockets:
        response = readLine(socket)
        print(response)


scheduler = BackgroundScheduler()
scheduler.add_job(func=handle_device_events, trigger="interval", seconds=10)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())
