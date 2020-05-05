from flask_wtf import FlaskForm
from wtforms import BooleanField, RadioField, SubmitField, IntegerField, StringField, validators


class LightsControlForm(FlaskForm):
    # lights
    isLightForm = BooleanField(default=True)
    lightOn = BooleanField(label='On Off Switch')
    lightMode = RadioField(label='Brightness Level', choices=[('l','Low'), ('m', 'Medium'), ('h', 'High')])
    submit = SubmitField('Submit')


class PumpControlForm(FlaskForm):
    # pump
    isPumpForm = BooleanField(default=True)
    pumpOn = BooleanField('On Off Switch')
    pumpMode = RadioField('Pump Operation Mode', choices=[('a', 'Automatic'), ('m', 'Manual')])
    pumpSpeed = IntegerField('Pump Speed(0-255)', [validators.NumberRange(min=0, max=256)])
    submit = SubmitField('Submit')


class LightsControlModel():
    def __init__(self, isLightForm, on, mode):
        self.isLightForm = isLightForm
        self.lightOn = bool(on)
        self.lightMode = str(mode)


class PumpControlModel():
    def __init__(self, isPumpForm, on, mode, speed):
        self.isPumpForm = isPumpForm
        self.pumpOn = bool(on)
        self.pumpMode = str(mode)
        self.pumpSpeed = int(speed)