import sys

import bson.errors
import werkzeug.security
from bson import ObjectId
from flask_pymongo import PyMongo

from models.constants import OrderDBKeys, OrderStatus, SellerDBKeys

dbk_order = OrderDBKeys()
dbk_seller = SellerDBKeys()
o_s = OrderStatus()
wz = werkzeug.security


class Bid:
    def __init__(
            self,
            seller: str,
            item: str,
            bid: float,
            order: str
    ):
        self.seller = seller
        self.item = item
        self.bid = bid
        self.order = order


class OrderItem:
    def __init__(
            self,
            item_id_1c: str,
            item_name: str,
            qty: float,
            sellers: [{}]
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

    def get_order_for_seller(self, date: str, seller_id: str):
        order = self.mongo.db[dbk_order.db_name].find_one(
            {
                dbk_order.date: date
            }
        )
        order_info = {}
        order_items = []
        if isinstance(order, dict):
            order_info[dbk_order.order_id] = str(order[dbk_order.id_db])
            for item in order[dbk_order.items]:
                for seller in item[dbk_order.sellers]:
                    if seller[dbk_order.seller_id] == seller_id:
                        order_item = {
                            dbk_order.item_id_1c: item[dbk_order.item_id_1c],
                            dbk_order.item_name: item[dbk_order.item_name],
                            dbk_order.qty: item[dbk_order.qty]
                        }
                        order_items.append(order_item)
            order_info[dbk_order.items] = order_items
        return order_info

    def create_order(self, new_order: Order):
        items = []
        for item in new_order.items:
            sellers = []
            for seller in item.sellers:
                sellers.append(
                    {
                        dbk_order.seller_id: seller[dbk_order.seller_id],
                        dbk_order.main_bid: seller[dbk_order.main_bid],
                        dbk_order.add_bid: seller[dbk_order.add_bid]
                    }
                )

            item_as_dict = {
                dbk_order.item_id_1c: item.item_id_1c,
                dbk_order.item_name: item.item_name,
                dbk_order.qty: item.qty,
                dbk_order.sellers: sellers
            }
            items.append(item_as_dict)

        self.mongo.db[dbk_order.db_name].insert_one(
            {
                dbk_order.date: new_order.date,
                dbk_order.status: o_s.ACTIVE,
                dbk_order.items: items
            }
        )

    def make_main_bid(self, bid):
        bid_order = self.mongo.db[dbk_order.db_name].find_one(
            {
                dbk_order.id_db: ObjectId(bid.order)
            }
        )
        result = False

        if isinstance(bid_order, dict):
            # все позиции в заказе
            all_items = bid_order[dbk_order.items]
            for item in all_items:
                # позиция по которой делается ставка
                if item[dbk_order.item_id_1c] == bid.item:
                    for seller in item[dbk_order.sellers]:
                        # текущая ставка продавца
                        if seller[dbk_order.seller_id] == bid.seller:
                            # создаем новую ставку
                            new_seller_bid = seller
                            new_seller_bid[dbk_order.main_bid] = bid.bid
                            old_items = all_items
                            old_items.remove(item)
                            new_item = item
                            old_sellers_bids = item[dbk_order.sellers]
                            old_sellers_bids.remove(seller)
                            old_sellers_bids.append(new_seller_bid)
                            new_sellers_bids = old_sellers_bids
                            new_all_items = old_items
                            new_item['SELLERS'] = new_sellers_bids
                            new_all_items.append(new_item)
                            self.mongo.db[dbk_order.db_name].update_one(
                                {
                                    dbk_order.id_db: ObjectId(bid.order)
                                },
                                {
                                    '$set': {
                                        dbk_order.items: new_all_items
                                    }
                                }
                            )
                            result = True
                            break
        return result

    def make_add_bid(self, bid):
        bid_order = self.mongo.db[dbk_order.db_name].find_one(
            {
                dbk_order.id_db: ObjectId(bid.order)
            }
        )
        result = False

        if isinstance(bid_order, dict):
            # все позиции в заказе
            all_items = bid_order[dbk_order.items]
            for item in all_items:
                # позиция по которой делается ставка
                if item[dbk_order.item_id_1c] == bid.item:
                    for seller in item[dbk_order.sellers]:
                        # текущая ставка продавца
                        if seller[dbk_order.seller_id] == bid.seller:
                            # создаем новую ставку
                            new_seller_bid = seller
                            new_seller_bid[dbk_order.add_bid] = bid.bid
                            old_items = all_items
                            old_items.remove(item)
                            new_item = item
                            old_sellers_bids = item[dbk_order.sellers]
                            old_sellers_bids.remove(seller)
                            old_sellers_bids.append(new_seller_bid)
                            new_sellers_bids = old_sellers_bids
                            new_all_items = old_items
                            new_item['SELLERS'] = new_sellers_bids
                            new_all_items.append(new_item)
                            self.mongo.db[dbk_order.db_name].update_one(
                                {
                                    dbk_order.id_db: ObjectId(bid.order)
                                },
                                {
                                    '$set': {
                                        dbk_order.items: new_all_items
                                    }
                                }
                            )
                            result = True
                            break
        return result

    def get_best_offers_by_main_bid(self, order_id):

        order = self.mongo.db[dbk_order.db_name].find_one(
            {
                dbk_order.id_db: ObjectId(order_id)
            }
        )
        best_offers = {}
        all_items = order[dbk_order.items]
        for item in all_items:
            best_bid = {
                dbk_order.seller_id: 'NO SELLER',
                dbk_order.main_bid: sys.float_info.max,
                dbk_order.add_bid: sys.float_info.max
            }

            for bid in item[dbk_order.sellers]:
                if bid[dbk_order.main_bid] != 0 and bid[dbk_order.main_bid] < best_bid[dbk_order.main_bid]:
                    best_bid = bid
            if best_bid[dbk_order.main_bid] == sys.float_info.max:
                best_bid[dbk_order.main_bid] = 0
            if best_bid[dbk_order.add_bid] == sys.float_info.max:
                best_bid[dbk_order.add_bid] = 0

            try:
                seller_info = self.mongo.db[dbk_seller.db_name].find_one(
                    {
                        dbk_seller.id_db: ObjectId(best_bid[dbk_order.seller_id])
                    }
                )
                if isinstance(seller_info, dict):
                    best_bid[dbk_order.seller_id_1c] = str(seller_info[dbk_seller.id_1c])
            except bson.errors.InvalidId:
                best_bid[dbk_order.seller_id_1c] = 'NO SELLER'

            best_offers[item[dbk_order.item_id_1c]] = best_bid

        return best_offers

    def get_all_offers_by_main_bid(self, order_id):

        order = self.mongo.db[dbk_order.db_name].find_one(
            {
                dbk_order.id_db: ObjectId(order_id)
            }
        )
        all_offers = {}
        all_items = order[dbk_order.items]
        for item in all_items:
            sellers_offers = item[dbk_order.sellers]
            sellers_more = []
            for seller_offer in sellers_offers:
                seller_more = seller_offer
                seller_info = self.mongo.db[dbk_seller.db_name].find_one(
                    {
                        dbk_order.id_db: ObjectId(seller_offer[dbk_order.seller_id])
                    }
                )
                seller_more[dbk_seller.discount] = seller_info[dbk_seller.discount]
                seller_more[dbk_seller.delay] = seller_info[dbk_seller.delay]
                seller_more[dbk_seller.rating] = seller_info[dbk_seller.rating]
                seller_more[dbk_order.seller_id_1c] = seller_info[dbk_seller.id_1c]
                sellers_more.append(seller_more)

            sorted_offers = sorted(sellers_more,
                                   key=lambda x: (
                                       x[dbk_order.main_bid],
                                       x[dbk_seller.discount],
                                       x[dbk_seller.delay],
                                       x[dbk_seller.rating]
                                   ))
            sorted_offers.reverse()
            all_offers[item[dbk_order.item_id_1c]] = sorted_offers
        return all_offers

    def get_best_offers_by_add_bid(self, order_id):

        order = self.mongo.db[dbk_order.db_name].find_one(
            {
                dbk_order.id_db: ObjectId(order_id)
            }
        )
        best_offers = {}
        all_items = order[dbk_order.items]
        for item in all_items:
            best_bid = {
                dbk_order.seller_id: 'NO SELLER',
                dbk_order.add_bid: sys.float_info.max,
                dbk_order.main_bid: sys.float_info.max
            }
            for bid in item[dbk_order.sellers]:
                if bid[dbk_order.add_bid] != 0 and bid[dbk_order.add_bid] < best_bid[dbk_order.add_bid]:
                    best_bid = bid
            if best_bid[dbk_order.add_bid] == sys.float_info.max:
                best_bid[dbk_order.add_bid] = 0
            if best_bid[dbk_order.main_bid] == sys.float_info.max:
                best_bid[dbk_order.main_bid] = 0
            try:
                seller_info = self.mongo.db[dbk_seller.db_name].find_one(
                    {
                        dbk_seller.id_db: ObjectId(best_bid[dbk_order.seller_id])
                    }
                )
                if isinstance(seller_info, dict):
                    best_bid[dbk_order.seller_id_1c] = str(seller_info[dbk_seller.id_1c])
            except bson.errors.InvalidId:
                best_bid[dbk_order.seller_id_1c] = 'NO SELLER'

            best_offers[item[dbk_order.item_id_1c]] = best_bid

        return best_offers

    def get_all_offers_by_add_bid(self, order_id):

        order = self.mongo.db[dbk_order.db_name].find_one(
            {
                dbk_order.id_db: ObjectId(order_id)
            }
        )
        all_offers = {}
        all_items = order[dbk_order.items]
        for item in all_items:
            sellers_offers = item[dbk_order.sellers]
            sellers_more = []
            for seller_offer in sellers_offers:
                seller_more = seller_offer
                seller_info = self.mongo.db[dbk_seller.db_name].find_one(
                    {
                        dbk_order.id_db: ObjectId(seller_offer[dbk_order.seller_id])
                    }
                )
                seller_more[dbk_seller.discount] = seller_info[dbk_seller.discount]
                seller_more[dbk_seller.delay] = seller_info[dbk_seller.delay]
                seller_more[dbk_seller.rating] = seller_info[dbk_seller.rating]
                seller_more[dbk_order.seller_id_1c] = seller_info[dbk_seller.id_1c]
                sellers_more.append(seller_more)

            sorted_offers = sorted(sellers_more,
                                   key=lambda x: (
                                       x[dbk_order.add_bid],
                                       x[dbk_seller.discount],
                                       x[dbk_seller.delay],
                                       x[dbk_seller.rating]
                                   ))
            sorted_offers.reverse()
            all_offers[item[dbk_order.item_id_1c]] = sorted_offers
        return all_offers

    def get_best_offers_by_all_bid(self, order_id):

        order = self.mongo.db[dbk_order.db_name].find_one(
            {
                dbk_order.id_db: ObjectId(order_id)
            }
        )
        best_offers = {}
        all_items = order[dbk_order.items]
        for item in all_items:
            best_bid = {
                dbk_order.seller_id: 'NO SELLER',
                dbk_order.final_bid: sys.float_info.max,
            }
            for bid in item[dbk_order.sellers]:
                if bid[dbk_order.main_bid] != 0 and bid[dbk_order.main_bid] < best_bid[dbk_order.final_bid]:
                    best_bid = bid
                    best_bid[dbk_order.final_bid] = best_bid[dbk_order.main_bid]
                if bid[dbk_order.add_bid] != 0 and bid[dbk_order.add_bid] < best_bid[dbk_order.final_bid]:
                    best_bid[dbk_order.final_bid] = best_bid[dbk_order.add_bid]

            if best_bid[dbk_order.final_bid] == sys.float_info.max:
                best_bid[dbk_order.final_bid] = 0

            try:
                seller_info = self.mongo.db[dbk_seller.db_name].find_one(
                    {
                        dbk_seller.id_db: ObjectId(best_bid[dbk_order.seller_id])
                    }
                )
                if isinstance(seller_info, dict):
                    best_bid[dbk_order.seller_id_1c] = str(seller_info[dbk_seller.id_1c])
            except bson.errors.InvalidId:
                best_bid[dbk_order.seller_id_1c] = 'NO SELLER'

            best_offers[item[dbk_order.item_id_1c]] = best_bid

        return best_offers

    def get_all_offers_by_all_bid(self, order_id):

        order = self.mongo.db[dbk_order.db_name].find_one(
            {
                dbk_order.id_db: ObjectId(order_id)
            }
        )
        all_offers = {}
        all_items = order[dbk_order.items]
        for item in all_items:
            sellers_offers = item[dbk_order.sellers]
            sellers_more = []
            for seller_offer in sellers_offers:
                seller_more = seller_offer
                seller_info = self.mongo.db[dbk_seller.db_name].find_one(
                    {
                        dbk_order.id_db: ObjectId(seller_offer[dbk_order.seller_id])
                    }
                )
                seller_more[dbk_seller.discount] = seller_info[dbk_seller.discount]
                seller_more[dbk_seller.delay] = seller_info[dbk_seller.delay]
                seller_more[dbk_seller.rating] = seller_info[dbk_seller.rating]
                seller_more[dbk_order.seller_id_1c] = seller_info[dbk_seller.id_1c]
                seller_more[dbk_order.final_bid] = sys.float_info.max
                print(seller_more)
                if (seller_more[dbk_order.main_bid] != 0 and
                        seller_more[dbk_order.main_bid] < seller_more[dbk_order.add_bid]):
                    seller_more[dbk_order.final_bid] = seller_more[dbk_order.main_bid]
                elif (seller_more[dbk_order.add_bid] != 0 and
                      seller_more[dbk_order.add_bid] < seller_more[dbk_order.main_bid]):
                    seller_more[dbk_order.final_bid] = seller_more[dbk_order.add_bid]

                if seller_more[dbk_order.final_bid] == sys.float_info.max:
                    seller_more[dbk_order.final_bid] = 0

                sellers_more.append(seller_more)

            sorted_offers = sorted(sellers_more,
                                   key=lambda x: (
                                       x[dbk_order.final_bid],
                                       x[dbk_seller.discount],
                                       x[dbk_seller.delay],
                                       x[dbk_seller.rating]
                                   ))
            sorted_offers.reverse()
            all_offers[item[dbk_order.item_id_1c]] = sorted_offers
        return all_offers

    @staticmethod
    def parse_order(dbo):  # return Order?
        if isinstance(dbo, dict):
            items_list = []
            for item in dbo[dbk_order.items]:
                new_item = OrderItem(
                    item_id_1c=item[dbk_order.item_id_1c],
                    item_name=item[dbk_order.item_name],
                    qty=item[dbk_order.qty],
                    sellers=item[dbk_order.sellers]
                )
                items_list.append(new_item)
            order = Order(
                id_db=dbo[dbk_order.id_db],
                date=dbo[dbk_order.date],
                status=dbo[dbk_order.status],
                items=items_list
            )
            return order
        else:
            return None

    @staticmethod
    def parse_bid(dbb):  # return Bid?
        if isinstance(dbb, dict):
            bid = Bid(
                seller=dbb[dbk_order.seller_id],
                bid=dbb[dbk_order.bid],
                item=dbb[dbk_order.item_id_1c],
                order=dbb[dbk_order.order_id]
            )
            return bid
        else:
            return None
