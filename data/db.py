from peewee import SqliteDatabase
from models import Person

db = SqliteDatabase('my_database.db')

db.connect()
db.create_tables([Person])