from flask_wtf import FlaskForm
from wtforms import BooleanField, RadioField, SubmitField


class LightsControlForm(FlaskForm):
    # lights
    lightOn = BooleanField(label='On Off Switch')
    lightMode = RadioField(label='Brightness Level', choices=[('low_power','Low'), ('medium_power', 'Medium'), ('high_power', 'High')])
    submit = SubmitField('Submit')


class PumpControlForm(FlaskForm):
    # pump
    pumpOn = BooleanField(label='On Off Switch')
    pumpMode = RadioField(label='Pump Operation Mode', choices=[('auto', 'Automatic'), ('manual', 'Manual')])
    submit = SubmitField('Submit')