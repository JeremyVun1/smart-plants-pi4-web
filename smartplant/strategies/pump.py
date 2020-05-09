from smartplant.models import MoistureModel, SmartPlantDevice


def moisture_pump_strategy(app, mac, socket):
    threshold_moisture = 500

    with app.app_context():
        # check if device exists
        device = SmartPlantDevice.query.get(mac)
        if not device:
            return
        
        guid = device.guid

        # get latest moisture reading
        model = MoistureModel.query.filter(MoistureModel.guid == guid).order_by(MoistureModel.timestamp.desc()).limit(1).all()
        print(model)
        if model and len(model):
            model = model[0]

        if model.moisture < threshold_moisture:
            # set pump to manual override mode
            socket.send(int(1).to_bytes(1, "little"))
            socket.send(int(0).to_bytes(1, "little"))

            # turn pump on
            socket.send(int(2).to_bytes(1, "little"))
        else:
            # set pump to auto mode
            socket.send(int(1).to_bytes(1, "little"))
            socket.send(int(1).to_bytes(1, "little"))

            # turn pump off
            socket.send(int(2).to_bytes(1, "little"))
