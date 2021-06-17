from flask import request, Blueprint

from app_config import mongo
from models.constants import OrderDBKeys
from models.order import OrderDBHelper
from utils.response_helper import create_resp

orders_routes = Blueprint('orders_routes', __name__, url_prefix='/api/orders/')
db = OrderDBHelper(mongo)
dbk = OrderDBKeys()


@orders_routes.route('create_order', methods=['POST'])
def create_order():
    _json = request.json
    order = db.parse_order(_json)
    order_id = db.create_order(order)
    msg_id = 0
    result = {'ORDER_ID': order_id}
    return create_resp(msg_id, result)


@orders_routes.route('make_main_bid', methods=['POST'])
def make_main_bid():
    _json = request.json
    seller_id = _json['seller_id']
    order_id = _json['order_id']
    positions = _json['positions']
    result = False
    for key in positions:
        bid = db.parse_bid(
            {
                dbk.seller_id: seller_id,
                dbk.bid: positions[key],
                dbk.item_id_1c: key,
                dbk.order_id: order_id
            }
        )
        result = db.make_main_bid(bid)
    if result:
        msg_id = 0
        result = 'success'
    else:
        msg_id = 1
        result = 'fail'

    return create_resp(msg_id, result)


@orders_routes.route('make_add_bid', methods=['POST'])
def make_add_bid():
    _json = request.json
    seller_id = _json['seller_id']
    order_id = _json['order_id']
    positions = _json['positions']
    result = False
    for key in positions:
        bid = db.parse_bid(
            {
                dbk.seller_id: seller_id,
                dbk.bid: positions[key],
                dbk.item_id_1c: key,
                dbk.order_id: order_id
            }
        )
        result = db.make_add_bid(bid)

    if result:
        msg_id = 0
        result = 'success'
    else:
        msg_id = 1
        result = 'fail'

    return create_resp(msg_id, result)


@orders_routes.route('get_best_offers_by_main_bid', methods=['POST'])
def get_best_offers_by_main_bid():
    _json = request.json
    order_id = _json[dbk.order_id]
    best_offers = db.get_best_offers_by_main_bid(order_id)
    msg_id = 0
    result = best_offers
    return create_resp(msg_id, result)


@orders_routes.route('get_all_offers_by_main_bid', methods=['POST'])
def get_all_offers_by_main_bid():
    _json = request.json
    order_id = _json[dbk.order_id]
    all_offers = db.get_all_offers_by_main_bid(order_id)
    msg_id = 0
    result = all_offers
    return create_resp(msg_id, result)


@orders_routes.route('get_best_offers_by_add_bid', methods=['POST'])
def get_best_offers_by_add_bid():
    _json = request.json
    order_id = _json[dbk.order_id]
    best_offers = db.get_best_offers_by_add_bid(order_id)
    msg_id = 0
    result = best_offers
    return create_resp(msg_id, result)


@orders_routes.route('get_all_offers_by_add_bid', methods=['POST'])
def get_all_offers_by_add_bid():
    _json = request.json
    order_id = _json[dbk.order_id]
    all_offers = db.get_all_offers_by_add_bid(order_id)
    msg_id = 0
    result = all_offers
    return create_resp(msg_id, result)


@orders_routes.route('get_best_offers_by_all_bid', methods=['POST'])
def get_best_offers_by_all_bid():
    _json = request.json
    order_id = _json[dbk.order_id]
    best_offers = db.get_best_offers_by_all_bid(order_id)
    msg_id = 0
    result = best_offers
    return create_resp(msg_id, result)


@orders_routes.route('get_all_offers_by_all_bid', methods=['POST'])
def get_all_offers_by_all_bid():
    _json = request.json
    order_id = _json[dbk.order_id]
    all_offers = db.get_all_offers_by_all_bid(order_id)
    msg_id = 0
    result = all_offers
    return create_resp(msg_id, result)
