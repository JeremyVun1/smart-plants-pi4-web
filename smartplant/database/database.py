from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

db = SQLAlchemy(None)

def init_db(app):
    global db
    db = SQLAlchemy(app)
    if not os.path.isfile('/smartplant.db'):
        db.create_all()