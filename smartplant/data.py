# Data access
from .models import SmartPlantState, SmartPlantDevice, PumpModel, LightingModel, PlantModel, MoistureModel
from smartplant import db


def parse_light_state(puid, json_obj):
    print("parsing light state")
    return LightingModel(puid=puid, state=json_obj['s'], mode=json_obj['e'])


def parse_waterpump_state(puid, json_obj):
    print("parsing waterpump state")
    return PumpModel(puid=puid, state=(json_obj['s'] != "0"), mode=json_obj['e'], speed=int(json_obj['v']))


def parse_moisture_state(puid, json_obj):
    print("parsing moisture state")
    return MoistureModel(puid=puid, moisture=json_obj['v'])


def parse_plant_state(puid, json_obj):
    print("parsing plant state")
    print(json_obj)
    result =  PlantModel(puid=json_obj['u'], pid=int(json_obj['i']), name=json_obj['n'], description=json_obj['c'])
    print(result)
    return result


module_parse_map = {
    "l": parse_light_state,
    "w": parse_waterpump_state,
    "m": parse_moisture_state,
    "p": parse_plant_state
}


def save_smartplants(smartplant_states):
    print("saving smartplants to db")
    print(smartplant_states)
    for state in smartplant_states:
        print(state)
        # unpack the data packet from the arduino
        guid = state['g']
        print(f"guid: {guid}")
        data = state['d']
        print(f"data: {data}")
        puid = data['d'][3]['d']['u'] # get the plant uid to link together our state models
        print(f"puid: {puid}")

        # check that the data packet is an update state packet
        if (data['m'] == 'u'):
            print("saving the update state to db")
            data = data['d']
            print(f"data: {data}")

            # parse the state models and store them in the database
            for module in data:
                print(f"module: {module}")
                model = module_parse_map[module['m']](puid, module['d'])
                print(f"model: {model}")
                db.session.add(model)
            db.commit()


# build smart plant data structures for front end
def load_smartplants():
    print("load smartplants from the db")
    smartplant_states = []

    devices = SmartPlantDevice.query.filter_by(isSmartPlant=True).all()
    print(devices)
    for device in devices:
        smartplant_states.append(load_smartplant(device))

    print("returning smartplant_states")
    print(smartplant_states)
    return smartplant_states


def load_smartplant(device):
    print("loading a single smartplant")
    plant = PlantModel.query.get(device.puid)
    pump = PumpModel.query.filter_by(puid=device.puid).orderby('timestamp desc').limit(1)
    light = LightingModel.query.filter_by(puid=device.puid).orderby('timestamp desc').limit(1)
    moist = MoistureModel.query.filter_by(puid=device.puid).orderby('timestamp desc').limit(1)
    print("gotten the models")
    print(plant)
    print(pump)
    print(light)
    print(moist)

    return SmartPlantState(
        mac=device.mac,
        puid=device.puid,
        p_name=plant.name,
        p_desc=plant.description,
        p_date=plant.timestamp,
        pump_state=pump.state,
        pump_mode=pump.mode,
        light_state=light.state,
        light_mode=light.mode,
        mois_val=moist.moisture
    )
