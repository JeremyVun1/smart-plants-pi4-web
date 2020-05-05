from smartplant import db
from smartplant.models import SmartPlantDevice, PlantModel, PumpModel, LightingModel, MoistureModel

'''
a = SmartPlantDevice(mac="abcde", puid="plant1", isSmartPlant=True)
b = SmartPlantDevice(mac="defg", puid="plant2", isSmartPlant=True)
c = SmartPlantDevice(mac="zzzz", puid="plant3", isSmartPlant=True)
d = SmartPlantDevice(mac="oooo", puid=None, isSmartPlant=False)

db.session.add(a)
db.session.add(b)
db.session.add(c)
db.session.add(d)

db.session.commit()
'''

print(SmartPlantDevice.query.all())
print(PlantModel.query.all())
print(LightingModel.query.all())
print(PumpModel.query.all())
print(MoistureModel.query.all())
