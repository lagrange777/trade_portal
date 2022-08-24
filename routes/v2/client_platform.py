import datetime
from enum import Enum

import bson.errors
import werkzeug
from bson import ObjectId
from flask import request, Blueprint, render_template, redirect
from flask_login import login_required, login_user, current_user, logout_user

from app_config import mongo, manager
from utils.response_helper import create_resp

client_platform_routes_v2 = Blueprint('client_platform_routes_v2', __name__, url_prefix='/v2/')

wz = werkzeug.security


class TradeStage(Enum):
    NOT_STARTED = 1
    MAIN = 2
    BETWEEN_MAIN_AND_ADD = 3
    ADD = 4
    FINISHED = 5


class TimeHelper:

    @staticmethod
    def string_datetime_to_timestamp(date_string, time_string):
        date_components = date_string.split('-')
        time_components = time_string.split('-')
        timestamp = datetime.datetime(
            int(date_components[0]),
            int(date_components[1]),
            int(date_components[2]),
            int(time_components[0]),
            int(time_components[1]),
            0,
            0
        )
        return timestamp
    def __init__(
            self,
            main_date_start,
            main_time_start,
            main_date_finish,
            main_time_finish,
            add_date_start,
            add_time_start,
            add_date_finish,
            add_time_finish,
    ):
        self.main_start_long = self.string_datetime_to_timestamp(main_date_start, main_time_start)
        self.main_finish_long = self.string_datetime_to_timestamp(main_date_finish, main_time_finish)
        self.add_start_long = self.string_datetime_to_timestamp(add_date_start, add_time_start)
        self.add_finish_long = self.string_datetime_to_timestamp(add_date_finish, add_time_finish)



    def get_current_stage(self, cur_time, cur_date):
        cur_date_long = int(cur_date.replace('-', ''))
        cur_time_tmp = cur_time.split('-')
        cur_time_long = int(cur_time_tmp[0]) * 60 + int(cur_time_tmp[1])

        if (
            cur_date_long < self.main_date_start_long
            or (
                self.main_date_start_long <= cur_date_long <= self.main_date_finish_long
                and
                cur_time_long < self.main_time_start_long
            )
        ):
            return TradeStage.NOT_STARTED

        if (
            self.main_date_start_long <= cur_date_long <= self.main_date_finish_long
            and
                self.main_time_start_long <= cur_time_long <= self.main_time_finish_long
        ):
            return TradeStage.MAIN

        if (
            self.add_date_start_long <= cur_date_long <= self.main_date_finish_long
        ):

    class TradeHelper:
        def __init__(self, seller_id_1c):
            self.seller_id_1c = seller_id_1c

        def get_orders_ids_for_seller(self):
            all_orders = mongo.db['orders'].find({'status': 'active'})

            seller_orders = []

            for order in all_orders:
                if self.seller_id_1c in order['sellers'].keys():
                    tmp_order = order
                    tmp_order['_id'] = str(tmp_order['_id'])
                    seller_orders.append(tmp_order)

            return seller_orders

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

        def get_1c_id(self):
            return self.seller_id_1c

    @manager.user_loader
    def load_user(id_db):
        try:
            obj_id = ObjectId(id_db)
        except bson.errors.InvalidId:
            return None
        u = mongo.db['sellers'].find_one(
            {
                '_id': obj_id
            }
        )
        if not u:
            return None
        return User(u['id_1c'], str(u['_id']))

    @client_platform_routes_v2.route('/login', methods=['GET', 'POST'])
    def login_page():
        if request.method == 'POST':
            _json = request.json
            login = _json['login']
            password = _json['password']
            check_user = mongo.db['sellers'].find_one(
                {
                    'email': login
                }
            )
            if isinstance(check_user, dict):
                check_password = wz.check_password_hash(check_user['password_hash'], password)
                if check_password:
                    user = User(
                        seller_id_1c=check_user['id_1c'],
                        seller_id_db=str(check_user['_id'])
                    )
                    login_user(user)
                    return redirect('/v2/trades-desk')
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
                return redirect('/v2/trades-desk')
            return render_template('login.html')

    @client_platform_routes_v2.route('logout')
    def logout():
        logout_user()
        return redirect('/login')

    @client_platform_routes_v2.route('trades-desk')
    def trades_desk():
        seller_id = current_user.get_1c_id()
        offset = datetime.timezone(datetime.timedelta(hours=3))
        now = datetime.datetime.now(offset)
        cur_date = now.strftime('%d.%m.%Y')
        cur_time_hour = now.hour
        cur_time_min = now.minute

        return render_template('trades_desk.html')

    @client_platform_routes_v2.route('/trade')
    @login_required
    def main_page():
        seller_id = current_user.get_1c_id()
        offset = datetime.timezone(datetime.timedelta(hours=3))
        now = datetime.datetime.now(offset)
        cur_date = now.strftime('%d.%m.%Y')
        cur_time_hour = now.hour
        cur_time_min = now.minute
        step = 'Торги неактивны'
        schedule_db = mongo.db['SETTINGS'].find_one()
        is_trade_available = False
        current_step = 0
        main_range_start = schedule_db['MAIN_HOUR_START'] * 60 + schedule_db['MAIN_MINUTE_START']
        main_range_finish = schedule_db['MAIN_HOUR_FINISH'] * 60 + schedule_db['MAIN_MINUTE_FINISH']
        add_range_start = schedule_db['ADD_HOUR_START'] * 60 + schedule_db['ADD_MINUTE_START']
        add_range_finish = schedule_db['ADD_HOUR_FINISH'] * 60 + schedule_db['ADD_MINUTE_FINISH']
        cur_time = cur_time_hour * 60 + cur_time_min

        if isinstance(schedule_db, dict):
            if main_range_start <= cur_time <= main_range_finish:
                step = 'Основные торги'
                is_trade_available = True
                current_step = 1
            if add_range_start <= cur_time <= add_range_finish:
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

    @client_platform_routes_v2.route('/seller_settings')
    @login_required
    def seller_settings_page():
        seller_id = current_user.get_id()
        seller_info = db_seller.find_by_db_id(seller_id)
        return render_template('seller_settings.html')

    @client_platform_routes_v2.route('/')
    def redirect_1():
        return redirect('/v2/trades-desk')

    @client_platform_routes_v2.errorhandler(401)
    def not_auth(error=None):
        return redirect('/v2/login')
