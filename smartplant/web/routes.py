from flask import Blueprint, render_template, request, flash, redirect, url_for

from .bt import *
from .data import *
from .charts import fetch_chart_data
from smartplant.forms import *


web = Blueprint('web', __name__)

@web.route('/', methods=['GET', 'POST'])
def index():
    smartplants = []

    if request.method == 'POST':
        find_new_smartplant_devices()

    sockets = connect_smartplant_devices()
    responses = request_full_state(sockets)
    save_smartplants(responses)
    smartplants = load_smartplants()

    # socket check
    for smartplant in smartplants:
        smartplant.socketExists = smartplant.mac in sockets

    print(smartplants)
    for mac in sockets:
        sockets[mac].close()

    # return render_template('index.html')
    return render_template('index.html', smartplants=smartplants, title="index")


@web.route("/control/<guid>", methods=['GET', 'POST'])
def control(guid):
    try:
        sockets = connect_smartplant_devices()

        # build flower status info
        device = load_device(guid)
        smartplant = load_smartplant(device)
        smartplant.socketExists = device.mac in sockets  # see if we have sockets or not
        
        if request.method == 'POST':
            form_dict = request.form.to_dict()

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
        lights_control_form = LightsControlForm(obj=LightsControlModel(isLightForm=True, on=smartplant.lightstate, mode=smartplant.lightmode))
        pumpControlForm = PumpControlForm(obj=PumpControlModel(isPumpForm=True, on=smartplant.pumpstate, mode=smartplant.pumpmode, speed=smartplant.pumpspeed))
        
        chart_data = fetch_chart_data(hours=48)

        for mac in sockets:
            sockets[mac].close()

    except Exception:
        for mac in sockets:
            sockets[mac].close()

    return render_template(
        'control.html',
        title='Control Plant',
        smartplant=smartplant,
        guid=guid,
        lights_control_form=lights_control_form,
        pump_control_form=pumpControlForm,
        chart_data=chart_data
    )
