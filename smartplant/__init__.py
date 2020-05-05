from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = "32018ddbe36292e8a6543bc5a54a6c42"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smartplant.db'
db = SQLAlchemy(app)

sockets = []

from smartplant import models
from smartplant import routes
from smartplant import scheduler