from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo
from yandex_checkout import Configuration

app = Flask(__name__)
app.config['SECRET_KEY'] = '1483369abusa'
Configuration.account_id = '706814'
Configuration.secret_key = 'live_yGwjsz7e4-gurjx0sbduIHZjy0OsJyjKeW6HRJTh5Cc'
app.config['JSON_AS_ASCII'] = False
app.config[
    "MONGO_URI"] = "mongodb://vrtimmrtl:Asdqwerty123@3err0.ru:27017/globaltrade_appv2?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&ssl=false"
manager = LoginManager(app)
mongo = PyMongo(app)
