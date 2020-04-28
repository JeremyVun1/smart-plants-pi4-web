from peewee import *
from data import db

class BaseModel(Model):
    class Meta:
        database = db


class Person(BaseModel):
    firstname = CharField()
    lastname = CharField()
    phone = CharField()