class SellerDBKeys:
    def __init__(self):
        self.db_name = 'SELLERS'
        self.id_1c = 'ID_1C'
        self.id_db = '_id'
        self.full_name = 'FULL_NAME'
        self.short_name = 'SHORT_NAME'
        self.email = 'EMAIL'
        self.password_hash = 'PASSWORD_HASH'
        self.discount = 'DISCOUNT'
        self.delay = 'DELAY'
        self.manager = 'MANAGER'
        self.inn = 'INN'
        self.add_info = 'ADD_INFO'


class OrderDBKeys:
    def __init__(self):
        self.db_name = 'ORDERS'
        self.id_db = '_id'
        self.item_id_1c = 'ITEM_1C_ID'
        self.item_name = 'ITEM_NAME'
        self.qty = 'QTY'
        self.sellers = 'SELLERS'
        self.date = 'DATE'
        self.status = 'STATUS'
        self.items = 'ITEMS'


class OrderStatus:
    def __init__(self):
        self.CLOSED = 0
        self.ACTIVE = 1