from flask import request, Blueprint

from app_config import mongo
from models.seller import SellerDBHelper
from utils.response_helper import create_resp

sellers_routes = Blueprint('sellers_routes', __name__, url_prefix='/api/sellers/')
db = SellerDBHelper(mongo)


@sellers_routes.route('add_seller', methods=['POST'])
def add_seller():
    _json = request.json
    seller = db.parse_seller(_json)
    check = db.create_seller(seller)
    if check:
        msg_id = 0
        result = 'seller was created'
    else:
        msg_id = 1
        result = 'such seller already exists'

    return create_resp(msg_id, result)

# @sellers_routes.route('get_all_sellers', methods=['POST'])
# def get_all_sellers():
#     _json = request.json
