import json

from flask_pymongo import PyMongo
from bson import ObjectId
import werkzeug.security

from models.constants import SellerDBKeys

dbk = SellerDBKeys
wz = werkzeug.security


class Seller:
    def __init__(
            self,
            id_1c: str,
            id_db: str,
            full_name: str,
            short_name: str,
            email: str,
            password_hash: str,
            discount: float,
            delay: int,
            manager: str,
            inn: str,
            rating: float,
            add_info: []

    ):
        self.id_1c = id_1c
        self.id_db = id_db
        self.full_name = full_name
        self.short_name = short_name
        self.email = email
        self.password_hash = password_hash
        self.discount = discount
        self.delay = delay
        self.manager = manager
        self.inn = inn
        self.rating = rating
        self.add_info = add_info


class SellerEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Seller):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)


class SellerDBHelper:
    def __init__(self, mongo: PyMongo):
        self.mongo = mongo

    def get_all_sellers(self):
        sellers = self.mongo.db[dbk.db_name].find()
        parsed_sellers = []
        for seller in sellers:
            s = self.parse_seller(seller)
            seller_as_dict = {
                dbk.id_db: str(s.id_db),
                dbk.id_1c: s.id_1c,
                dbk.full_name: s.full_name,
                dbk.short_name: s.short_name,
                dbk.email: s.email,
                dbk.discount: s.discount,
                dbk.delay: s.delay,
                dbk.manager: s.manager,
                dbk.inn: s.inn,
                dbk.rating: s.rating,
                dbk.add_info: s.add_info
            }
            parsed_sellers.append(seller_as_dict)
        return parsed_sellers

    def find_by_1c_id(self, id_1c):  # return Seller
        db_seller = self.mongo.db[dbk.db_name].find_one(
            {
                dbk.id_1c: id_1c
            }
        )
        return self.parse_seller(db_seller)

    def find_by_db_id(self, id_db):  # return Seller?
        db_seller = self.mongo.db[dbk.db_name].find_one(
            {
                dbk.id_db: ObjectId(id_db)
            }
        )
        return self.parse_seller(db_seller)

    def create_seller(self, new_seller: Seller):  # return Boolean
        check = self.find_by_1c_id(new_seller.id_1c)
        if check is None:
            self.mongo.db[dbk.db_name].insert_one(
                {
                    dbk.id_1c: new_seller.id_1c,
                    dbk.full_name: new_seller.full_name,
                    dbk.short_name: new_seller.short_name,
                    dbk.email: new_seller.email,
                    dbk.password_hash: wz.generate_password_hash(new_seller.password_hash),
                    dbk.discount: new_seller.discount,
                    dbk.delay: new_seller.delay,
                    dbk.manager: new_seller.manager,
                    dbk.inn: new_seller.inn,
                    dbk.rating: new_seller.rating,
                    dbk.add_info: new_seller.add_info
                }
            )
            return True
        else:
            return False

    def full_update_seller(self, id_1c, seller_info: Seller):
        self.mongo.db[dbk.db_name].update_one(
            {
                dbk.id_1c: id_1c
            },
            {
                '$set': {
                    dbk.full_name: seller_info.full_name,
                    dbk.short_name: seller_info.short_name,
                    dbk.email: seller_info.email,
                    dbk.password_hash: wz.generate_password_hash(seller_info.password_hash),
                    dbk.discount: seller_info.discount,
                    dbk.delay: seller_info.delay,
                    dbk.manager: seller_info.manager,
                    dbk.inn: seller_info.inn,
                    dbk.rating: seller_info.rating,
                    dbk.add_info: seller_info.add_info
                }
            }
        )

    def change_seller_password(self, id_db: str, src: int, old_password: str, new_password: str):  # return Boolean
        """
        :param id_db: db id
        :param src: 0 - request by owner, 1 - request by admin
        :param old_password: as is
        :param new_password: as is
        :return:
        """
        db_seller = self.find_by_db_id(id_db)
        if db_seller is not None:
            if src == 0:
                if wz.check_password_hash(db_seller.password_hash, old_password):
                    db_seller.password_hash = wz.generate_password_hash(new_password)
                    self.__update_seller(
                        db_seller.id_db,
                        [
                            {
                                'key': dbk.password_hash,
                                'value': db_seller.password_hash
                            }
                        ]
                    )
                    return True
                else:
                    return False
            elif src == 1:
                db_seller.password_hash = wz.generate_password_hash(new_password)
                self.__update_seller(
                    db_seller.id_db,
                    [
                        {
                            'key': dbk.password_hash,
                            'value': db_seller.password_hash
                        }
                    ]
                )
                return True
        return False

    def __update_seller(self, id_db, params_for_update: []):
        params = {}
        for param in params_for_update:
            params[param['key']] = param['value']

        self.mongo.db[dbk.db_name].update_one(
            {
                '_id': ObjectId(id_db)
            },
            {
                '$set': params
            }
        )

    @staticmethod
    def parse_seller(dbs):  # return Seller?
        if isinstance(dbs, dict):
            seller = Seller(
                id_1c=dbs[dbk.id_1c],
                id_db=str(dbs[dbk.id_db]),
                full_name=dbs[dbk.full_name],
                short_name=dbs[dbk.short_name],
                email=dbs[dbk.email],
                password_hash=dbs[dbk.password_hash],
                discount=dbs[dbk.discount],
                delay=dbs[dbk.delay],
                manager=dbs[dbk.manager],
                inn=dbs[dbk.inn],
                rating=dbs[dbk.rating],
                add_info=dbs[dbk.add_info]
            )
            return seller
        else:
            return None

    @staticmethod
    def seller_to_dict(seller: Seller):
        seller_as_dict = {
            dbk.id_db: str(seller.id_db),
            dbk.id_1c: seller.id_1c,
            dbk.full_name: seller.full_name,
            dbk.short_name: seller.short_name,
            dbk.email: seller.email,
            dbk.discount: seller.discount,
            dbk.delay: seller.delay,
            dbk.manager: seller.manager,
            dbk.inn: seller.inn,
            dbk.rating: seller.rating,
            dbk.add_info: seller.add_info
        }
        return seller_as_dict
