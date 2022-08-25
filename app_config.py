from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['SECRET_KEY'] = '1483369abusa'
app.config['JSON_AS_ASCII'] = False
app.config[
    "MONGO_URI"] = "mongodb://vrtimmrtl:Asdqwerty123@3err0.ru:27017/globaltrade_appv2?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&ssl=false"
manager = LoginManager(app)
mongo = PyMongo(app)
