# Database access
from smartplant.models import *
from smartplant.database import db
import json


def parse_light_state(guid, json_obj):
    print(f"parsing light state for guid: {guid}")
    return LightingModel(guid=guid, state=(json_obj['s'] != '0'), mode=json_obj['e'])


def parse_waterpump_state(guid, json_obj):
    print(f"parsing waterpump state for guid: {guid}")
    return PumpModel(guid=guid, state=(json_obj['s'] != "0"), mode=json_obj['e'], speed=int(json_obj['v']))


def parse_moisture_state(guid, json_obj):
    print(f"parsing moisture state for guid: {guid}")
    return MoistureModel(guid=guid, moisture=int(json_obj['v']))


def parse_plant_state(guid, json_obj):
    print(f"parsing plant state for guid: {guid}")
    model = PlantModel.query.filter_by(guid=guid).one_or_none()
    if model:
        model.guid = guid

        try:
            model.puid = json_obj['u']
            model.pid = int(json_obj['i'])
        except Exception:
            model.puid = -1
            model.pid = -1

        model.name = json_obj['n']
        model.description = json_obj['c']
        return model
    else:
        try:
            puid = json_obj['u']
            pid = int(json_obj['i'])
        except Exception:
            puid = -1
            pid = -1

        return PlantModel(guid=guid, puid=puid, pid=pid, name=json_obj['n'], description=json_obj['c'])


parse_module_func_map = {
    "l": parse_light_state,
    "w": parse_waterpump_state,
    "m": parse_moisture_state,
    "p": parse_plant_state
}


def save_smartplants(smartplant_devices):
    if not smartplant_devices:
        return

    print("saving smartplants to db")

    for smartplant in smartplant_devices:
        # unpack the data packet from the arduino
        guid = smartplant['g']
        data = smartplant['d']

        # check that the data packet is an update packet
        if (data['m'] == 'u'):
            data = data['d']

            # parse the state models and store them in the database
            for module in data:
                model = parse_module_func_map[module['m']](guid, module['d'])
                db.session.add(model)
                db.session.commit()


# build smart plant data structures for front end
def load_smartplants():
    print("load smartplants from the db")
    smartplant_states = []

    devices = SmartPlantDevice.query.filter(SmartPlantDevice.isSmartPlant == True).all()
    print(devices)
    for device in devices:
        smartplant = load_smartplant(device)
        if smartplant:
            smartplant_states.append(smartplant)

    return smartplant_states


def load_smartplant(device):
    plant = PlantModel.query.filter_by(guid=device.guid).order_by(PlantModel.timestamp.desc()).limit(1).one_or_none()
    pump = PumpModel.query.filter_by(guid=device.guid).order_by(PumpModel.timestamp.desc()).limit(1).one_or_none()
    light = LightingModel.query.filter_by(guid=device.guid).order_by(LightingModel.timestamp.desc()).limit(1).one_or_none()
    moist = MoistureModel.query.filter_by(guid=device.guid).order_by(MoistureModel.timestamp.desc()).limit(1).one_or_none()

    if plant.pid > 0:
        result = SmartPlantState(
            mac=device.mac,
            guid=device.guid,
            puid=plant.puid,
            pid=plant.pid,
            pname=plant.name,
            pdesc=plant.description,
            pdate=plant.timestamp,
            pumpstate=pump.state,
            pumpmode=pump.mode,
            pumpspeed=pump.speed,
            lightstate=light.state,
            lightmode=light.mode,
            moistval=moist.moisture,
            socketExists=True
        )
    else:
        result = None

    return result


def load_device(guid):
    return SmartPlantDevice.query.filter_by(guid=guid).one_or_none()


def update_light_db_with_commands(guid, form_dict):
    model = LightingModel(guid=guid, mode=form_dict['lightMode'], state=('lightOn' in form_dict and form_dict['lightOn'] == 'y'))
    db.session.add(model)
    db.session.commit()


def update_pump_db_with_commands(guid, form_dict):
    model = PumpModel(guid=guid, mode=form_dict['pumpMode'], state=('pumpOn' in form_dict and form_dict['pumpOn'] == 'y'), speed=form_dict['pumpSpeed'])
    db.session.add(model)
    db.session.commit()
