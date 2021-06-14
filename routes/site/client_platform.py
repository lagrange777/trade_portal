import datetime
import time

import werkzeug
from bson import ObjectId
from flask import request, Blueprint, render_template, redirect, flash
from flask_login import login_required, login_user, current_user, logout_user

from app_config import mongo, manager
from models.constants import OrderDBKeys
from models.order import OrderDBHelper
from utils.response_helper import create_resp

client_platform_routes = Blueprint('client_platform_routes', __name__, url_prefix='/')

db = OrderDBHelper(mongo)
dbk = OrderDBKeys()
wz = werkzeug.security


class User:
    def __init__(self, seller_id_1c, seller_id_db):
        self.seller_id_1c = seller_id_1c
        self.seller_id_db = seller_id_db

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
        return self.seller_id_db


@manager.user_loader
def load_user(id_db):
    u = mongo.db['SELLERS'].find_one(
        {
            '_id': ObjectId(id_db)
        }
    )
    if not u:
        return None
    return User(u['ID_1C'], str(u['_id']))


@client_platform_routes.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        _json = request.json
        login = _json['login']
        password = _json['password']
        check_user = mongo.db['SELLERS'].find_one(
            {
                'EMAIL': login
            }
        )
        if isinstance(check_user, dict):
            check_password = wz.check_password_hash(check_user['PASSWORD_HASH'], password)
            if check_password:
                user = User(
                    seller_id_1c=check_user['ID_1C'],
                    seller_id_db=str(check_user['_id'])
                )
                login_user(user)
                return redirect('/trade')
            else:
                msg_id = 1
                result = 'wrong password'
                return create_resp(msg_id, result)
        else:
            msg_id = 2
            result = 'wrong login'
            return create_resp(msg_id, result)
    else:
        if current_user.is_authenticated:
            return redirect('/trade')
        return render_template('login.html')


@client_platform_routes.route('logout')
def logout():
    logout_user()
    return redirect('/login')


@client_platform_routes.route('trade')
@login_required
def main_page():
    seller_id = current_user.get_id()
    now = datetime.datetime.now()
    cur_date = now.strftime('%d.%m.%Y')
    cur_time_hour = now.hour
    cur_time_min = now.minute
    step = 'Торги неактивны'
    is_step_available = False
    if cur_time_hour == 10 and (0 <= cur_time_min <= 59):
        step = 'Основные торги'
        is_step_available = True
    if cur_time_hour == 11 and (0 <= cur_time_min <= 29):
        step = 'Дополнительные торги'
        is_step_available = True

    order = db.get_order_for_seller(cur_date, seller_id)
    order_id = order['ORDER_ID']
    order = order['ITEMS']
    return render_template(
        'form-basic.html',
        seller_id=seller_id,
        date=cur_date,
        order=order,
        order_id=order_id,
        step=step,
        is_step_available=is_step_available)


@client_platform_routes.errorhandler(401)
def not_auth(error=None):
    return redirect('/login')
