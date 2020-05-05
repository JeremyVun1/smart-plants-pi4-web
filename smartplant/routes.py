from flask import render_template, request, flash, redirect
from smartplant.forms import LightsControlForm, PumpControlForm, PumpControlModel, LightsControlModel
from smartplant import app, sockets
from .bt import find_new_smartplant_devices, connect_smartplant_devices, request_full_state, send_light_commands, send_pump_commands
from .data import save_smartplants, load_smartplants, load_smartplant, load_device, update_light_db_with_commands, update_pump_db_with_commands


@app.route("/", methods=['GET', 'POST'])
def index():
    global sockets
    smartplants = []

    if request.method == 'POST':
        for mac in sockets:
            socket = sockets[mac]
            socket.close()
        
        find_new_smartplant_devices()
        sockets = connect_smartplant_devices()

    print(f"open sockets {sockets}")
    responses = request_full_state(sockets)
    save_smartplants(responses)
    smartplants = load_smartplants()

    # socket check
    for smartplant in smartplants:
        smartplant.socketExists = smartplant.mac in sockets

    print(smartplants)

    return render_template('index.html', smartplants=smartplants, title="index")


@app.route("/control/<guid>", methods=['GET', 'POST'])
def control(guid):
    global sockets

    # build flower status info
    device = load_device(guid)
    smartplant = load_smartplant(device)
    smartplant.socketExists = device.mac in sockets  # see if we have sockets or not
    
    if request.method == 'POST':
        form_dict = request.form.to_dict()
        print("RECEIVED POST")
        print(form_dict)

        # validate, send commands, and prefill the form
        if 'isLightForm' in form_dict:
            form = LightsControlForm(request.form)
            if form.validate():
                flash('light control sent', 'success')
                send_light_commands(sockets[device.mac], smartplant, form_dict)
                update_light_db_with_commands(guid, form_dict)
                return redirect(f"/control/{guid}", code=302)

        elif 'isPumpForm' in form_dict:
            form = PumpControlForm(request.form)
            if form.validate():
                flash('pump control sent', 'success')
                send_pump_commands(sockets[device.mac], smartplant, form_dict)
                update_pump_db_with_commands(guid, form_dict)
            else:
                flash('pump speed must be between 0-255', 'danger')
            return redirect(f"/control/{guid}", code=302)

    # build control forms
    print(smartplant)
    lightsControlForm = LightsControlForm(obj=LightsControlModel(isLightForm=True, on=smartplant.lightstate, mode=smartplant.lightmode))
    pumpControlForm = PumpControlForm(obj=PumpControlModel(isPumpForm=True, on=smartplant.pumpstate, mode=smartplant.pumpmode, speed=smartplant.pumpspeed))
            

    return render_template(
        'control.html',
        title='Control Plant',
        smartplant=smartplant,
        guid=guid,
        lightsControlForm=lightsControlForm,
        pumpControlForm=pumpControlForm
    )
