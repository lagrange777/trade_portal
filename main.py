from app_config import app
# from routes.api.sellers import sellers_routes
# from routes.api.orders import orders_routes
# from routes.site.client_platform import client_platform_routes
# from routes.api.trade_settings import settings_routes
from routes.v2.client_platform import client_platform_routes_v2
from routes.v2.orders_routes import orders_routes_v2
from routes.v2.sellers import sellers_routes_v2


@app.route('/api-map')
def hello_world():
    return 'API MAP'


if __name__ == '__main__':
    # app.register_blueprint(sellers_routes)
    # app.register_blueprint(orders_routes)
    # app.register_blueprint(client_platform_routes)
    # app.register_blueprint(settings_routes)
    app.register_blueprint(orders_routes_v2)
    app.register_blueprint(client_platform_routes_v2)
    app.register_blueprint(sellers_routes_v2)
    app.run(host="127.0.0.1", port="8092", debug=True)
