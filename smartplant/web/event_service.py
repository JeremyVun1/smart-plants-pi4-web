from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import bluetooth
from datetime import datetime
import time
import json

from smartplant.database import db
from smartplant.models import MoistureModel, PumpModel, PlantModel, LightingModel
from smartplant.strategies import day_night_lighting_strategy, moisture_pump_strategy

from .bt import connect_smartplant_devices
from .util import read_line

sp_app = None


def parse_event(json_str, app):
    try:
        with app.app_context():
            obj = json.loads(json_str)
            guid = obj['g']
            data = obj['d']

            # moisture event
            if data['m'] == 'm':
                data = data['d']
                val = int(data['v'])
                model = MoistureModel(guid=guid, moisture=val)
                db.session.add(model)
                db.session.commit()

            # pump event
            elif data['m'] == 'w':
                data = data['d']
                speed = int(data['v'])
                state = 0 if data['s'] == '0' else 1
                mode = data['e']
                model = PumpModel(guid=guid, state=state, mode=mode, speed=speed)
                db.session.add(model)
                db.session.commit()

            # plant event
            elif data['m'] == 'p':
                data = data['d']
                model = PlantModel.query.filter(PlantModel.guid == guid).one_or_none()
                if model:
                    model.guid = 'null'
                else:
                    model = PlantModel(guid=guid, puid=data['u'], pid=int(data['i']), name=data['n'], description=data['c'])
                db.session.add(model)
                db.session.commit()

            # light event
            elif data['m'] == 'l':
                data = data['d']
                state = 0 if data['s'] == "0" else 1
                model = LightingModel(guid=guid, mode=data['e'], state=state)
                db.session.add(model)
                db.session.commit()

    except Exception:
        return False


def parse_events(sockets, app):
    for mac in sockets:
        socket = sockets[mac]
        
        buffer = read_line(socket)
        print(buffer)
        while buffer:
            print(buffer)
            parse_event(buffer, app)
            buffer = read_line(socket)


def run_strategy(sockets, app, strategy_func):
    for mac in sockets:
        strategy_func(app, mac, sockets[mac])


def close_sockets(sockets):
    for mac in sockets:
        sockets[mac].close()


def handle_device_events():
    global sp_app
    print("Running Event Handler Service")
    sockets = connect_smartplant_devices(sp_app)

    parse_events(sockets, sp_app)

    # run edge computing strategies
    run_strategy(sockets, sp_app, day_night_lighting_strategy)
    run_strategy(sockets, sp_app, moisture_pump_strategy)

    close_sockets(sockets)


def schedule_event_handling(app):
    global sp_app
    sp_app = app

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=handle_device_events, trigger="interval", seconds=10)
    scheduler.start()

    atexit.register(lambda: scheduler.shutdown())
