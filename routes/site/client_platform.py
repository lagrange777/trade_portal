from flask import request, Blueprint, render_template

from app_config import mongo, manager
from flask_login import login_user, login_required, current_user
from models.constants import OrderDBKeys
from models.order import OrderDBHelper
from utils.response_helper import create_resp

client_platform_routes = Blueprint('client_platform_routes', __name__, url_prefix='/')
# db = OrderDBHelper(mongo)
# dbk = OrderDBKeys()


class User:
    def __init__(self, username):
        self.username = username

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username


@manager.user_loader
def load_user(login):
    u = mongo.db.adminusers.find_one({'login': login})
    if not u:
        return None
    return User(username=u['login'])


@client_platform_routes.route('main')
@login_required
def main_page():
    return render_template('order.html')