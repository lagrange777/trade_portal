import sys

from bson import ObjectId
from flask import Blueprint, request
from app_config import mongo, dev_key
from routes.v2.trade_stage import TradeStage
from utils.response_helper import create_resp

orders_routes = Blueprint('orders_routes', __name__, url_prefix='/api/orders/')


class OrderModel:

    def __init__(
            self,
            id_db,
            id_1c,
            main_date_start,
            main_time_start,
            main_date_finish,
            main_time_finish,
            add_date_start,
            add_time_start,
            add_date_finish,
            add_time_finish,
            title,
            desc,
            status,
            sellers,
            items
    ):
        self.id_db = id_db
        self.id_1c = id_1c

        # yyyy-mm-dd
        self.main_date_start = main_date_start
        # hh-mm
        self.main_time_start = main_time_start
        # yyyy-mm-dd
        self.main_date_finish = main_date_finish
        # hh-mm
        self.main_time_finish = main_time_finish
        # yyyy-mm-dd
        self.add_date_start = add_date_start
        # hh-mm
        self.add_time_start = add_time_start
        # yyyy-mm-dd
        self.add_date_finish = add_date_finish
        # hh-mm
        self.add_time_finish = add_time_finish
        self.title = title
        self.desc = desc
        self.status = status
        self.sellers = sellers
        self.items = items

    @staticmethod
    def create_instance(json):
        json_id_db = json['id_db']
        json_id_1c = json['id_1c']
        json_main_date_start = json['main_date_start']
        json_main_time_start = json['main_time_start']
        json_main_date_finish = json['main_date_finish']
        json_main_time_finish = json['main_time_finish']
        json_add_date_start = json['add_date_start']
        json_add_time_start = json['add_time_start']
        json_add_date_finish = json['add_date_finish']
        json_add_time_finish = json['add_time_finish']
        json_title = json['title']
        json_desc = json['desc']
        json_status = json['status']
        json_sellers = json['sellers']

        raw_items = json['items']
        json_items = {}
        for raw_item in raw_items:
            json_items[raw_item['item_1c_id']] = raw_item

        order_instance = OrderModel(
            json_id_db,
            json_id_1c,
            json_main_date_start,
            json_main_time_start,
            json_main_date_finish,
            json_main_time_finish,
            json_add_date_start,
            json_add_time_start,
            json_add_date_finish,
            json_add_time_finish,
            json_title,
            json_desc,
            json_status,
            json_sellers,
            json_items
        )
        return order_instance

    @staticmethod
    def read_from_db(id_db):
        order = mongo.db['ORDERS'].find_one(
            {
                'id_1c': id_db
            },
            {
                '_id': 0
            }
        )

        if order is None:
            return None

        order['items'] = list(order['items'].values())
        return order

    def write_to_db(self, is_update=False):

        document = {
            '_id': ObjectId(self.id_db),
            'id_1c': self.id_1c,
            'main_date_start': self.main_date_start,
            'main_time_start': self.main_time_start,
            'main_date_finish': self.main_date_finish,
            'main_time_finish': self.main_time_finish,
            'add_date_start': self.add_date_start,
            'add_time_start': self.add_time_start,
            'add_date_finish': self.add_date_finish,
            'add_time_finish': self.add_time_finish,
            'title': self.title,
            'desc': self.desc,
            'status': self.status,
            'sellers': self.sellers,
            'items': self.items
        }
        if is_update:
            mongo.db['ORDERS'].update_one(
                {
                    '_id': ObjectId(self.id_db),
                },
                {
                    '$set': document
                }
            )
        else:
            mongo.db['ORDERS'].insert_one(document)


class ItemModel:
    def __init__(
            self,
            id_1c,
            item_name,
            qty,
            unit,
    ):
        self.id_1c = id_1c
        self.item_name = item_name
        self.qty = qty
        self.unit = unit

    @staticmethod
    def create_instance(json):
        json_id_1c = json['id_1c']
        json_item_name = json['item_name']
        json_qty = json['qty ']
        json_unit = json['unit']
        item_instance = ItemModel(
            json_id_1c,
            json_item_name,
            json_qty,
            json_unit
        )
        return item_instance


class BidModel:
    def __init__(
            self,
            id_db,
            item_id,
            order_id,
            seller_id,
            comment,
            stage,
            value,
            is_update
    ):
        self.id_db = id_db
        self.item_id = item_id
        self.order_id = order_id
        self.seller_id = seller_id
        self.comment = comment
        self.stage = stage
        self.value = value
        self.is_update = is_update

    @staticmethod
    def create_instance(json):
        json_id_db = json['id_db']
        json_item_id = json['item_id']
        json_order_id = json['order_id']
        json_seller_id = json['seller_id']
        json_comment = json['comment']
        json_stage = json['stage']
        json_value = json['value']
        json_is_update = json['is_update']

        bid_instance = BidModel(
            json_id_db,
            json_item_id,
            json_order_id,
            json_seller_id,
            json_comment,
            json_stage,
            json_value,
            json_is_update
        )
        return bid_instance

    @staticmethod
    def write_to_db(bids_list, stage):
        docs_for_insert = []
        result = {'inserted': [], 'updated': [], 'skipped': []}
        for bid in bids_list:
            if bid.value == 0:
                result['skipped'].append(bid.id_db)
                continue
            document = {
                '_id': ObjectId(bid.id_db),
                'item_id': bid.item_id,
                'order_id': bid.order_id,
                'seller_id': bid.seller_id,
                'comment': bid.comment,
                'stage': bid.stage,
                'value': bid.value
            }

            if bid.is_update:
                mongo.db[stage].update_one(
                    {
                        '_id': ObjectId(bid.id_db)
                    },
                    {
                        '$set': document
                    }
                )
                result['updated'].append(bid.id_db)
            else:
                docs_for_insert.append(document)
                result['inserted'].append(bid.id_db)

        if len(docs_for_insert) > 0:
            mongo.db[stage].insert_many(docs_for_insert)
        print(result)
        return result


class BidHelper:
    def __init__(self, order_id):
        self.order_id_1c = order_id
        self.order_id = str(mongo.db['ORDERS'].find_one({'id_1c': order_id}, {'_id': 1})['_id'])

    def get_all_main_bids(self):
        all_bids = mongo.db['MAIN_BIDS'].find(
            {
                'order_id': self.order_id_1c
            },
            {
                'stage': 0,
                'order_id': 0
            }
        )
        result = {}
        for bid in all_bids:
            norm_bid = {
                'bid_id': str(bid['_id']),
                'item_id': bid['item_id'],
                'seller_id': bid['seller_id'],
                'comment': bid['comment'],
                'value': bid['value']
            }
            k = bid['item_id']
            if k not in result.keys():
                result[k] = []
            result[k].append(norm_bid)

        return result

    def get_all_add_bids(self):
        all_bids = mongo.db['ADD_BIDS'].find(
            {
                'order_id': self.order_id_1c
            },
            {
                'stage': 0,
                'order_id': 0
            }
        )
        result = {}
        for bid in all_bids:
            norm_bid = {
                'bid_id': str(bid['_id']),
                'item_id': bid['item_id'],
                'seller_id': bid['seller_id'],
                'comment': bid['comment'],
                'value': bid['value']
            }
            k = bid['item_id']
            if k not in result.keys():
                result[k] = []
            result[k].append(norm_bid)

        return result

    def get_best_main_bids(self):
        all_bids = self.get_all_main_bids()
        result = {}
        for item_id, item_bids in all_bids.items():
            min_value = 'no data'
            best_bid = 'no data'
            for bid in item_bids:
                if bid['value'] != 0:
                    min_value = bid['value']
                    best_bid = bid
                    break
            if min_value != 'no data':
                for bid in item_bids:
                    if bid['value'] < min_value and bid['value'] != 0:
                        min_value = bid['value']
                        best_bid = bid
                    result[item_id] = best_bid
        return result

    def get_best_add_bids(self):
        all_bids = self.get_all_add_bids()
        result = {}
        for item_id, item_bids in all_bids.items():
            min_value = 'no data'
            best_bid = 'no data'
            for bid in item_bids:
                if bid['value'] != 0:
                    min_value = bid['value']
                    best_bid = bid
                    break
            if min_value != 'no data':
                for bid in item_bids:
                    if bid['value'] < min_value and bid['value'] != 0:
                        min_value = bid['value']
                        best_bid = bid
                    result[item_id] = best_bid
        return result

    def get_best_all_bids(self):
        best_main_bids = self.get_best_main_bids()
        best_add_bids = self.get_best_add_bids()

        unique_items = list(best_main_bids.keys())
        result = {}

        for each in best_add_bids.keys():
            if each not in unique_items:
                unique_items.append(each)

        for item_id in unique_items:
            max_value = sys.float_info.max
            max_bid = {}
            if item_id in best_main_bids.keys():
                max_value = best_main_bids[item_id]['value']
                max_bid = best_main_bids[item_id]
            if item_id in best_add_bids.keys():
                tmp = best_add_bids[item_id]['value']
                if tmp <= max_value:
                    max_bid = best_add_bids[item_id]
            result[item_id] = max_bid

        return result


@orders_routes.route('create-order', methods=['POST'])
def create_order():
    _json = request.json
    try:
        int_key = _json['dev_key']
    except KeyError:
        int_key = ''
    if int_key != dev_key:
        msg_id = -1
        result = 'bad key'
        return create_resp(msg_id, result)
    order_id = ObjectId()
    _json['id_db'] = str(order_id)
    created_order = OrderModel.create_instance(_json)
    created_order.write_to_db()
    msg_id = 0
    result = {'order_id': str(order_id)}
    return create_resp(msg_id, result)


@orders_routes.route('update-order', methods=['POST'])
def update_order():
    _json = request.json
    try:
        int_key = _json['dev_key']
    except KeyError:
        int_key = ''
    if int_key != dev_key:
        msg_id = -1
        result = 'bad key'
        return create_resp(msg_id, result)
    _json['id_db'] = ObjectId(_json['id_db'])
    created_order = OrderModel.create_instance(_json)
    print(created_order.items)
    created_order.write_to_db(is_update=True)
    msg_id = 0
    result = {'order was updated': str(_json['id_db'])}
    return create_resp(msg_id, result)


@orders_routes.route('get-order-info', methods=['POST'])
def get_order_info():
    _json = request.json
    try:
        int_key = _json['dev_key']
    except KeyError:
        int_key = ''
    if int_key != dev_key:
        msg_id = -1
        result = 'bad key'
        return create_resp(msg_id, result)
    order_id = _json['id_1c']

    order_info = OrderModel.read_from_db(order_id)

    if order_info is None:
        msg_id = 1
        result = 'Wrong id_db'
        return create_resp(msg_id, result)

    msg_id = 0
    result = order_info

    return create_resp(msg_id, result)


@orders_routes.route('make-main-bid', methods=['POST'])
def make_main_bid():
    _json = request.json
    created_bids = []
    positions = _json['positions']
    seller_id = _json['seller_id']
    order_id = _json['order_id']
    for item_id in positions:
        try:
            bid_value = float(positions[item_id]['bid'])
        except:
            bid_value = 0
        b = {
            'stage': TradeStage.MAIN.value,
            'item_id': item_id,
            'order_id': order_id,
            'seller_id': seller_id,
            'comment': positions[item_id]['seller_comment'],
            'value': bid_value
        }

        bid_db = mongo.db['MAIN_BIDS'].find_one(
            {
                'item_id': item_id,
                'seller_id': seller_id,
                'order_id': order_id
            }
        )
        if isinstance(bid_db, dict):
            bid_id = str(bid_db['_id'])
        else:
            bid_id = 'first_bid'
        if bid_id == 'first_bid':
            bid_id = str(ObjectId())
            b['id_db'] = bid_id
            b['is_update'] = False
        else:
            b['id_db'] = bid_id
            b['is_update'] = True

        created_bid = BidModel.create_instance(b)
        created_bids.append(created_bid)

    result = BidModel.write_to_db(created_bids, 'MAIN_BIDS')
    msg_id = 0

    return create_resp(msg_id, result)


@orders_routes.route('make-add-bid', methods=['POST'])
def make_add_bid():
    created_bids = []
    _json = request.json
    positions = _json['positions']
    seller_id = _json['seller_id']
    order_id = _json['order_id']
    for item_id in positions:
        try:
            bid_value = float(positions[item_id]['bid'])
        except:
            bid_value = 0
        b = {
            'stage': TradeStage.ADD.value,
            'item_id': item_id,
            'order_id': order_id,
            'seller_id': seller_id,
            'comment': positions[item_id]['seller_comment'],
            'value': bid_value
        }

        bid_db = mongo.db['ADD_BIDS'].find_one(
            {
                'item_id': item_id,
                'seller_id': seller_id,
                'order_id': order_id
            }
        )
        if isinstance(bid_db, dict):
            bid_id = str(bid_db['_id'])
        else:
            bid_id = 'first_bid'
        if bid_id == 'first_bid':
            bid_id = str(ObjectId())
            b['id_db'] = bid_id
            b['is_update'] = False
        else:
            b['id_db'] = bid_id
            b['is_update'] = True

        created_bid = BidModel.create_instance(b)
        created_bids.append(created_bid)

    result = BidModel.write_to_db(created_bids, 'ADD_BIDS')
    msg_id = 0

    return create_resp(msg_id, result)


@orders_routes.route('get-best-by-main-bid', methods=['POST'])
def get_best_by_main_bid():
    _json = request.json
    try:
        int_key = _json['dev_key']
    except KeyError:
        int_key = ''
    if int_key != dev_key:
        msg_id = -1
        result = 'bad key'
        return create_resp(msg_id, result)
    order_id = _json['order_id']
    result = BidHelper(order_id).get_best_main_bids()
    msg_id = 0
    return create_resp(msg_id, result)


@orders_routes.route('get-all-by-main-bid', methods=['POST'])
def get_all_by_main_bid():
    _json = request.json
    try:
        int_key = _json['dev_key']
    except KeyError:
        int_key = ''
    if int_key != dev_key:
        msg_id = -1
        result = 'bad key'
        return create_resp(msg_id, result)
    order_id = _json['order_id']
    result = BidHelper(order_id).get_all_main_bids()
    msg_id = 0
    return create_resp(msg_id, result)


@orders_routes.route('get-best-by-add-bid', methods=['POST'])
def get_best_by_add_bid():
    _json = request.json
    try:
        int_key = _json['dev_key']
    except KeyError:
        int_key = ''
    if int_key != dev_key:
        msg_id = -1
        result = 'bad key'
        return create_resp(msg_id, result)
    order_id = _json['order_id']
    result = BidHelper(order_id).get_best_add_bids()
    msg_id = 0
    return create_resp(msg_id, result)


@orders_routes.route('get-all-by-add-bid', methods=['POST'])
def get_all_by_add_bid():
    _json = request.json
    try:
        int_key = _json['dev_key']
    except KeyError:
        int_key = ''
    if int_key != dev_key:
        msg_id = -1
        result = 'bad key'
        return create_resp(msg_id, result)
    order_id = _json['order_id']
    result = BidHelper(order_id).get_all_add_bids()
    msg_id = 0
    return create_resp(msg_id, result)


@orders_routes.route('get-best-by-all-bids', methods=['POST'])
def get_best_by_all_bids():
    _json = request.json
    try:
        int_key = _json['dev_key']
    except KeyError:
        int_key = ''

    if int_key != dev_key:
        msg_id = -1
        result = 'bad key'
        return create_resp(msg_id, result)
    order_id = _json['order_id']
    result = BidHelper(order_id).get_best_all_bids()
    msg_id = 0
    return create_resp(msg_id, result)
