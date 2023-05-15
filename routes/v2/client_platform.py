import datetime
import re
from enum import Enum

import bson.errors
import werkzeug
from bson import ObjectId
from flask import request, Blueprint, render_template, redirect
from flask_login import login_required, login_user, current_user, logout_user
from markupsafe import Markup

from app_config import mongo, manager
from routes.v2.orders_routes import BidHelper
from routes.v2.trade_stage import TradeStage
from utils.response_helper import create_resp

client_platform_routes = Blueprint('client_platform_routes', __name__, url_prefix='/')

wz = werkzeug.security


class TimeHelper:
    @staticmethod
    def get_cur_date_and_time():
        offset = datetime.timezone(datetime.timedelta(hours=3))
        now = datetime.datetime.now(offset)
        cur_date = now.strftime('%Y-%m-%d')
        cur_time = str(now.hour) + '-' + str(now.minute)
        return cur_date, cur_time

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
            add_time_finish
    ):
        self.main_start_long = self.string_datetime_to_timestamp(main_date_start, main_time_start)
        self.main_finish_long = self.string_datetime_to_timestamp(main_date_finish, main_time_finish)
        self.add_start_long = self.string_datetime_to_timestamp(add_date_start, add_time_start)
        self.add_finish_long = self.string_datetime_to_timestamp(add_date_finish, add_time_finish)

    def get_current_stage(self, cur_time, cur_date):
        cur_date_long = self.string_datetime_to_timestamp(cur_date, cur_time)
        if cur_date_long < self.main_start_long:
            return TradeStage.NOT_STARTED
        if self.main_start_long <= cur_date_long <= self.main_finish_long:
            return TradeStage.MAIN
        if self.main_finish_long < cur_date_long < self.add_start_long:
            return TradeStage.BETWEEN_MAIN_AND_ADD
        if self.add_start_long <= cur_date_long <= self.add_finish_long:
            return TradeStage.ADD
        if cur_date_long > self.add_finish_long:
            return TradeStage.FINISHED


class TradeHelper:
    def __init__(self, seller_id_1c):
        self.seller_id_1c = seller_id_1c

    def get_grouped_orders_for_seller(self, cur_date, cur_time):
        all_orders = mongo.db['ORDERS'].find({'status': 'active'})

        seller_orders = []

        grouped_orders = {
            TradeStage.NOT_STARTED.value: [],
            TradeStage.MAIN.value: [],
            TradeStage.BETWEEN_MAIN_AND_ADD.value: [],
            TradeStage.ADD.value: [],
            TradeStage.FINISHED.value: []
        }

        for order in all_orders:
            if self.seller_id_1c in order['sellers'].keys():
                tmp_order = order
                tmp_order['_id'] = str(tmp_order['_id'])
                seller_orders.append(tmp_order)

        for order in seller_orders:
            time_helper = TimeHelper(
                main_date_start=order['main_date_start'],
                main_time_start=order['main_time_start'],
                main_date_finish=order['main_date_finish'],
                main_time_finish=order['main_time_finish'],
                add_date_start=order['add_date_start'],
                add_time_start=order['add_time_start'],
                add_date_finish=order['add_date_finish'],
                add_time_finish=order['add_time_finish']
            )
            stage = time_helper.get_current_stage(cur_time, cur_date)
            grouped_orders[stage.value].append(order)
        return grouped_orders


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
    u = mongo.db['SELLERS'].find_one(
        {
            '_id': obj_id
        }
    )
    if not u:
        return None
    return User(u['id_1c'], str(u['_id']))


@client_platform_routes.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        _json = request.json
        login = _json['login']
        password = _json['password']
        check_user = mongo.db['SELLERS'].find_one(
            {
                'email': re.compile(login, re.IGNORECASE)
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
                return redirect('/trades-desk')
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
            return redirect('/trades-desk')
        return render_template('login.html')


@client_platform_routes.route('logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@client_platform_routes.route('trades-desk')
@login_required
def trades_desk():
    seller_id = current_user.get_1c_id()
    offset = datetime.timezone(datetime.timedelta(hours=3))
    now = datetime.datetime.now(offset)
    cur_date = now.strftime('%Y-%m-%d')
    cur_time = str(now.hour) + '-' + str(now.minute)
    grouped_orders = TradeHelper(seller_id).get_grouped_orders_for_seller(cur_date, cur_time)
    print(grouped_orders)
    templates_not_started = []
    templates_main = []
    templates_between = []
    templates_add = []
    templates_finished = []

    for key in grouped_orders.keys():
        for each in grouped_orders[key]:
            each['items_count'] = each['sellers'][seller_id]
            if key == TradeStage.NOT_STARTED.value:
                templates_not_started.append(
                    Markup(render_template('trades_desc_cards/trades_desk_card_soon.html', order=each)))
            if key == TradeStage.MAIN.value:
                templates_main.append(
                    Markup(render_template('trades_desc_cards/trades_desk_card_main.html', order=each)))
            if key == TradeStage.BETWEEN_MAIN_AND_ADD.value:
                templates_between.append(
                    Markup(render_template('trades_desc_cards/trades_desk_card_soon.html', order=each)))
            if key == TradeStage.ADD.value:
                templates_add.append(Markup(render_template('trades_desc_cards/trades_desk_card_add.html', order=each)))
            if key == TradeStage.FINISHED.value:
                templates_finished.append(
                    Markup(render_template('trades_desc_cards/trades_desk_card_soon.html', order=each)))
    return render_template(
        'trades_desk.html',
        order=
        {
            1: templates_not_started,
            2: templates_main,
            3: templates_between,
            4: templates_add,
            5: templates_finished
        }
    )


@client_platform_routes.route('/trade')
@login_required
def main_page():
    seller_id = current_user.get_1c_id()
    _args = request.args
    order_id = _args.get('orderid')

    bid_helper = BidHelper(order_id)
    # all_mains = bid_helper.get_all_main_bids()
    # all_adds = bid_helper.get_all_add_bids()
    # best_mains = bid_helper.get_best_main_bids()
    # best_adds = bid_helper.get_best_add_bids()

    order_info = mongo.db['ORDERS'].find_one(
        {
            'id_1c': order_id
        }
    )
    time_helper = TimeHelper(
        main_date_start=order_info['main_date_start'],
        main_time_start=order_info['main_time_start'],
        main_date_finish=order_info['main_date_finish'],
        main_time_finish=order_info['main_time_finish'],
        add_date_start=order_info['add_date_start'],
        add_time_start=order_info['add_time_start'],
        add_date_finish=order_info['add_date_finish'],
        add_time_finish=order_info['add_time_finish']
    )

    cur_date_and_time = TimeHelper.get_cur_date_and_time()
    cur_stage = time_helper.get_current_stage(cur_date_and_time[1], cur_date_and_time[0])

    seller_items_ids = order_info['sellers'][seller_id]

    seller_items = []

    for item_id in seller_items_ids:
        i = order_info['items'][item_id]
        if cur_stage == TradeStage.MAIN:
            all_mains = bid_helper.get_all_main_bids()
            best_mains = bid_helper.get_best_main_bids()
            try:
                best_last_bid = best_mains[item_id]['value']
            except KeyError:
                best_last_bid = 0.0

            seller_last_bid = 0.0
            if item_id in all_mains.keys():
                for bid in all_mains[item_id]:
                    if seller_id == bid['seller_id']:
                        seller_last_bid = bid['value']
                        break
            if best_last_bid != 0.0:
                i['best_last_bid'] = best_last_bid
            else:
                i['best_last_bid'] = 'нет ставок'
            if seller_last_bid != 0.0:
                i['seller_last_bid'] = seller_last_bid
            else:
                i['seller_last_bid'] = 'нет ставок'
            seller_items.append(i)

        if cur_stage == TradeStage.ADD:
            all_adds = bid_helper.get_all_add_bids()
            best_adds = bid_helper.get_best_add_bids()
            try:
                best_last_bid = best_adds[item_id]['value']
            except KeyError:
                best_last_bid = 0.0
            seller_last_bid = 0.0
            if item_id in all_adds.keys():
                for bid in all_adds[item_id]:
                    if seller_id == bid['seller_id']:
                        seller_last_bid = bid['value']
                        break
            if best_last_bid != 0.0:
                i['best_last_bid'] = best_last_bid
            else:
                i['best_last_bid'] = 'нет ставок'

            if seller_last_bid != 0.0:
                i['seller_last_bid'] = best_last_bid
            else:
                i['seller_last_bid'] = 'нет ставок'
            seller_items.append(i)

    return render_template(
        'trade.html',
        cur_stage=cur_stage.value,
        seller_id=seller_id,
        order_id=order_id,
        order=seller_items)


@client_platform_routes.route('/seller_settings')
@login_required
def seller_settings_page():
    seller_id = current_user.get_id()
    # seller_info = db_seller.find_by_db_id(seller_id)
    return render_template('seller_settings.html')


@client_platform_routes.route('/')
@login_required
def redirect_1():
    return redirect('/trades-desk')


@client_platform_routes.errorhandler(401)
def not_auth(error=None):
    return redirect('/login')
