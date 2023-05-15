from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo

from utils.config_manager import ConfigManager

app = Flask(__name__)
db_address = ConfigManager.get_db_address()
db_login = ConfigManager.get_db_login()
db_password = ConfigManager.get_db_password()
db_name = ConfigManager.get_db_name()
dev_key = ConfigManager.get_integration_key()
secret_key = ConfigManager.get_secret_key()
app.config['SECRET_KEY'] = secret_key
app.config["MONGO_URI"] = "mongodb://" + \
                          db_login + ":" + db_password + "@" + \
                          db_address + \
                          "/" + \
                          db_name + \
                          "?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&ssl=false"

manager = LoginManager(app)
mongo = PyMongo(app)
