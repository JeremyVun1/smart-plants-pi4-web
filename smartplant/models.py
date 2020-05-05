from datetime import datetime
from smartplant import db
from dataclasses import dataclass


class LightingModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    puid = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    mode = db.Column(db.String(10), nullable=False)
    state = db.Column(db.Boolean)

    def __repr__(self):
        return f"LightingModel('{self.puid}', '{self.timestamp}', '{self.mode}', '{self.state}')"


class MoistureModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    puid = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    moisture = db.Column(db.Integer)

    def __repr__(self):
        return f"MoistureModel('{self.puid}', '{self.timestamp}', '{self.moisture}')"


class PumpModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    puid = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    mode = db.Column(db.String(10), nullable=False)
    state = db.Column(db.Boolean)
    speed = db.Column(db.Integer)

    def __repr__(self):
        return f"PumpModel('{self.puid}', '{self.timestamp}', '{self.mode}', '{self.state}', '{self.speed}')"


class PlantModel(db.Model):
    puid = db.Column(db.String, primary_key=True)
    pid = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    name = db.Column(db.String(30), unique=True, nullable=False)
    description = db.Column(db.String(100))

    def __repr__(self):
        return f"PlantModel('{self.puid}', '{self.pid}', {self.timestamp}', {self.name}', '{self.description}')"


class SmartPlantDevice(db.Model):
    mac = db.Column(db.String, primary_key=True)
    isSmartPlant = db.Column(db.Boolean)
    isConnected = db.Column(db.Boolean)
    puid = db.Column(db.String, unique=True, nullable=True)
    guid = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f"SmartPlantDevice('{self.mac}', sp: '{self.isSmartPlant}', connected: '{self.isConnected}', '{self.guid}', '{self.puid}')"


@dataclass
class SmartPlantState:
    mac: str
    puid: str
    p_name: str
    p_desc: str
    p_date: datetime
    pump_state: bool
    pump_Mode: str
    pump_speed: int
    light_state: bool
    light_mode: str
    moist_val: int
