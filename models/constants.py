class SellerDBKeys:
    db_name = 'SELLERS'
    id_db = '_id'
    id_1c = 'id_1c'
    full_name = 'full_name'
    short_name = 'short_name'
    email = 'email'
    password_hash = 'password_hash'
    discount = 'discount'
    delay = 'delay'
    manager = 'manager'
    inn = 'inn'
    rating = 'rating'
    add_info = 'add_info'


class OrderDBKeys:
    db_name = 'ORDERS'
    id_db = '_id'
    item_id_1c = 'item_1c_id'
    item_name = 'item_name'
    qty = 'qty'
    unit = 'unit'
    sellers = 'sellers'
    date = 'date'
    status = 'status'
    items = 'items'
    seller_id = 'seller_id'
    main_bid = 'main_bid'
    add_bid = 'add_bid'
    final_bid = 'final_bid'
    bid = 'bid'
    order_id = 'order_id'
    seller_id_1c = 'seller_1c_id'
    seller_comment = 'seller_comment'


class OrderStatus:
    def __init__(self):
        self.CLOSED = 0
        self.ACTIVE = 1
