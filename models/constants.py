class SellerDBKeys:
    def __init__(self):
        self.db_name = 'sellers'
        self.id_1c = 'id_1c'
        self.id_db = '_id'
        self.full_name = 'full_name'
        self.short_name = 'short_name'
        self.email = 'email'
        self.password_hash = 'password_hash'
        self.discount = 'discount'
        self.delay = 'delay'
        self.manager = 'manager'
        self.inn = 'inn'
        self.rating = 'rating'
        self.add_info = 'add_info'


class OrderDBKeys:
    def __init__(self):
        self.db_name = 'ORDERS'
        self.id_db = '_id'
        self.item_id_1c = 'ITEM_1C_ID'
        self.item_name = 'ITEM_NAME'
        self.qty = 'QTY'
        self.unit = 'UNIT'
        self.sellers = 'SELLERS'
        self.date = 'DATE'
        self.status = 'STATUS'
        self.items = 'ITEMS'
        self.seller_id = 'SELLER_ID'
        self.main_bid = 'MAIN_BID'
        self.add_bid = 'ADD_BID'
        self.final_bid = 'FINAL_BID'
        self.bid = 'BID'
        self.order_id = 'ORDER_ID'
        self.seller_id_1c = 'SELLER_1C_ID'
        self.seller_comment = 'SELLER_COMMENT'


class OrderStatus:
    def __init__(self):
        self.CLOSED = 0
        self.ACTIVE = 1