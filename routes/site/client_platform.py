import datetime

import werkzeug
from bson import ObjectId
from flask import request, Blueprint, render_template, redirect
from flask_login import login_required, login_user, current_user, logout_user

from app_config import mongo, manager
from models.constants import OrderDBKeys, SellerDBKeys
from models.order import OrderDBHelper
from models.seller import SellerDBHelper
from utils.response_helper import create_resp

client_platform_routes = Blueprint('client_platform_routes', __name__, url_prefix='/')

db_order = OrderDBHelper(mongo)
dbk_order = OrderDBKeys()
db_seller = SellerDBHelper(mongo)
dbk_seller = SellerDBKeys()
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


@client_platform_routes.route('/trade')
@login_required
def main_page():
    seller_id = current_user.get_id()
    now = datetime.datetime.now()
    cur_date = now.strftime('%d.%m.%Y')
    cur_time_hour = now.hour
    cur_time_min = now.minute
    step = 'Торги неактивны'
    schedule_db = mongo.db['SETTINGS'].find_one()
    is_trade_available = False
    current_step = 0
    if isinstance(schedule_db, dict):
        if (schedule_db['MAIN_HOUR_START'] <= cur_time_hour <= schedule_db['MAIN_HOUR_FINISH']
                and schedule_db['MAIN_MINUTE_START'] <= cur_time_min <= schedule_db['MAIN_MINUTE_FINISH']):
            step = 'Основные торги'
            is_trade_available = True
            current_step = 1
        if (schedule_db['ADD_HOUR_START'] <= cur_time_hour <= schedule_db['ADD_HOUR_FINISH']
                and schedule_db['ADD_MINUTE_START'] <= cur_time_min <= schedule_db['ADD_MINUTE_FINISH']):
            step = 'Дополнительные торги'
            is_trade_available = True
            current_step = 2

    order = db_order.get_order_for_seller(cur_date, seller_id)

    best_add_offers = []

    if len(order) != 0:
        order_id = order['ORDER_ID']
        if current_step == 2:
            best_add_offers = db_order.get_best_offers_by_main_bid(order_id)
        order = order['ITEMS']
    else:
        order_id = 'NO ORDER'
        order = []
    return render_template(
        'trade.html',
        seller_id=seller_id,
        date=cur_date,
        order=order,
        order_id=order_id,
        step=step,
        is_trade_available=is_trade_available,
        current_step=current_step,
        best_add_offers=best_add_offers)


@client_platform_routes.route('/seller_settings')
@login_required
def seller_settings_page():
    seller_id = current_user.get_id()
    seller_info = db_seller.find_by_db_id(seller_id)
    return render_template('seller_settings.html')

@client_platform_routes.route('/')
def redirect_1():
    return redirect('/trade')


@client_platform_routes.errorhandler(401)
def not_auth(error=None):
    return redirect('/login')
