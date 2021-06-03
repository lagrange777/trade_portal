import json

from flask_pymongo import PyMongo
from bson import ObjectId
import werkzeug.security

from models.constants import OrderDBKeys, OrderStatus
from models.seller import Seller

dbk = OrderDBKeys()
o_s = OrderStatus()
wz = werkzeug.security


class OrderItem:
    def __init__(
            self,
            item_id_1c: str,
            item_name: str,
            qty: float,
            sellers: [Seller]
    ):
        self.item_id_1c = item_id_1c
        self.item_name = item_name
        self.qty = qty
        self.sellers = sellers


class Order:
    def __init__(
            self,
            id_db: str,
            date: int,
            status: int,
            items: [OrderItem]
    ):
        self.id_db = id_db
        self.date = date
        self.status = status
        self.items = items


class OrderDBHelper:
    def __init__(self, mongo: PyMongo):
        self.mongo = mongo

    def create_order(self, new_order: Order):
        items = []
        for item in new_order.items:
            sellers = []
            for seller in item.sellers:
                sellers.append(seller.id_1c)

            item_as_dict = {
                dbk.item_id_1c: item.item_id_1c,
                dbk.item_name: item.item_name,
                dbk.qty: item.qty,
                dbk.sellers: sellers
            }
            items.append(item_as_dict)

        self.mongo.db[dbk.db_name].insert_one(
            {
                dbk.date: new_order.date,
                dbk.status: o_s.ACTIVE,
                dbk.items: items
            }
        )

    @staticmethod
    def parse_order(dbo):  # return Order?
        if isinstance(dbo, dict):
            order = Order(
                id_db="",
                date=19710101,
                status=0,
                items=
            )
