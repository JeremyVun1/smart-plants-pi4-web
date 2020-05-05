# Database access
from .models import SmartPlantState, SmartPlantDevice, PumpModel, LightingModel, PlantModel, MoistureModel
from smartplant import db


def parse_light_state(guid, json_obj):
    print(f"parsing light state for guid: {guid}")
    model = LightingModel.query.filter_by(guid=guid).one_or_none()
    if model:
        model.replaceWith(LightingModel(guid=guid, state=(json_obj['s'] != '0'), mode=json_obj['e']))
        return model
    else:
        return LightingModel(guid=guid, state=(json_obj['s'] != '0'), mode=json_obj['e'])


def parse_waterpump_state(guid, json_obj):
    print(f"parsing waterpump state for guid: {guid}")
    model = PumpModel.query.filter_by(guid=guid).one_or_none()
    if model:
        model.replaceWith(PumpModel(guid=guid, state=(json_obj['s'] != "0"), mode=json_obj['e'], speed=int(json_obj['v'])))
        return model
    else:
        return PumpModel(guid=guid, state=(json_obj['s'] != "0"), mode=json_obj['e'], speed=int(json_obj['v']))


def parse_moisture_state(guid, json_obj):
    print(f"parsing moisture state for guid: {guid}")
    model = MoistureModel.query.filter_by(guid=guid).one_or_none()
    if model:
        model.replaceWith(MoistureModel(guid=guid, moisture=int(json_obj['v'])))
        return model
    else:
        return MoistureModel(guid=guid, moisture=int(json_obj['v']))


def parse_plant_state(guid, json_obj):
    print(f"parsing plant state for guid: {guid}")
    model = PlantModel.query.filter_by(guid=guid).one_or_none()
    if model:
        model.replaceWith(PlantModel(guid=guid, puid=json_obj['u'], pid=int(json_obj['i']), name=json_obj['n'], description=json_obj['c']))
        return model
    else:
        return PlantModel(guid=guid, puid=json_obj['u'], pid=int(json_obj['i']), name=json_obj['n'], description=json_obj['c'])


parse_module_func_map = {
    "l": parse_light_state,
    "w": parse_waterpump_state,
    "m": parse_moisture_state,
    "p": parse_plant_state
}


def save_smartplants(smartplant_devices):
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

    devices = SmartPlantDevice.query.filter_by(isSmartPlant=True).all()
    print(devices)
    for device in devices:
        smartplant_states.append(load_smartplant(device))

    return smartplant_states


def load_smartplant(device):
    plant = PlantModel.query.filter_by(guid=device.guid).order_by(PlantModel.timestamp.desc()).limit(1).one_or_none()
    pump = PumpModel.query.filter_by(guid=device.guid).order_by(PumpModel.timestamp.desc()).limit(1).one_or_none()
    light = LightingModel.query.filter_by(guid=device.guid).order_by(LightingModel.timestamp.desc()).limit(1).one_or_none()
    moist = MoistureModel.query.filter_by(guid=device.guid).order_by(MoistureModel.timestamp.desc()).limit(1).one_or_none()

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
        moistval=moist.moisture
    )
    return result
