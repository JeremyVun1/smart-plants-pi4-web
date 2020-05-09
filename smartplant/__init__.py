from flask import Flask
import os.path

from smartplant.web.routes import web
from smartplant.web import schedule_event_handling
from smartplant.database import *
from smartplant.models import *

sp_app: Flask

def create_app():
    app = Flask(__name__)

    # configs
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = "32018ddbe36292e8a6543bc5a54a6c42"
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database/smartplant.db"

    # register blueprints
    app.register_blueprint(web, url_prefix='')

    # set up db
    db.init_app(app)

    # start event handling service
    schedule_event_handling(app)

    sp_app = app
    return sp_app


def setup_database(app):
    if not os.path.isfile('smartplant/database/smartplant.db'):
        with app.app_context():
            print("db created")
            db.create_all()