from flask import render_template, request, flash
from smartplant.forms import LightsControlForm, PumpControlForm
from smartplant import app, sockets
from .bt import find_new_smartplant_devices, connect_smartplant_devices, request_full_state
from .data import save_smartplants, load_smartplants


@app.route("/", methods=['GET', 'POST'])
def index():
    global sockets
    smartplants = []

    if request.method == 'POST':
        find_new_smartplant_devices()
        sockets = connect_smartplant_devices()

    try:
        print("GET INDEX")
        print(sockets)
        responses = request_full_state(sockets)
        save_smartplants(responses)
        smartplants = load_smartplants()
        print(smartplants)
    except Exception:
        pass

    return render_template('index.html', smartplants=smartplants, title="index")


@app.route("/control", methods=['GET', 'POST'])
def control():
    lightsControlForm = LightsControlForm()
    pumpControlForm = PumpControlForm()
    
    if request.method == 'POST':
        if lightsControlForm.validate_on_submit():
            flash('light control sent', 'success')
        if pumpControlForm.validate_on_submit():
            flash('pump control sent', 'success')
        # populate the forms with state data

    return render_template('control.html', title='Control Plant', lightsControlForm=lightsControlForm, pumpControlForm=pumpControlForm)