from flask import request, Blueprint

from app_config import mongo
from models.constants import SellerDBKeys
from models.seller import SellerDBHelper
from utils.response_helper import create_resp

orders_routes = Blueprint('orders_routes', __name__, url_prefix='/api/orders/')
db = SellerDBHelper(mongo)
dbk = SellerDBKeys()


@orders_routes.route('create_orders', methods=['POST'])
def create_orders():
