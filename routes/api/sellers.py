from flask import request, Blueprint

from app_config import mongo
from models.constants import SellerDBKeys
from models.seller import SellerDBHelper
from utils.response_helper import create_resp

sellers_routes = Blueprint('sellers_routes', __name__, url_prefix='/api/sellers/')
db = SellerDBHelper(mongo)
dbk = SellerDBKeys()


@sellers_routes.route('add_seller', methods=['POST'])
def add_seller():
    _json = request.json
    slrs = _json['sellers']
    created = []
    updated = []

    for slr in slrs:
        seller = db.parse_seller(slr)
        check = db.create_seller(seller)
        if check:
            created.append(seller.id_1c)
        else:
            db.full_update_seller(seller.id_1c, seller)
            updated.append(seller.id_1c)

    msg_id = 0
    result = {'created': created, 'updated': updated}

    return create_resp(msg_id, result)


@sellers_routes.route('get_all_sellers', methods=['GET'])
def get_all_sellers():
    _json = request.json
    sellers = db.get_all_sellers()
    msg_id = 0
    result = sellers
    return create_resp(msg_id, result)


@sellers_routes.route('get_seller_by_1c_id', methods=['POST'])
def get_seller_by_1c_id():
    _json = request.json
    id_ic = _json[dbk.id_1c]
    seller = db.find_by_1c_id(id_ic)
    seller_as_dict = db.seller_to_dict(seller)
    msg_id = 0
    result = seller_as_dict
    return create_resp(msg_id, result)


@sellers_routes.route('get_seller_by_db_id', methods=['POST'])
def get_seller_by_db_id():
    _json = request.json
    id_db = _json[dbk.id_db]
    seller = db.find_by_db_id(id_db)
    seller_as_dict = db.seller_to_dict(seller)
    msg_id = 0
    result = seller_as_dict
    return create_resp(msg_id, result)