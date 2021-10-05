from app_config import app
from routes.api.sellers import sellers_routes
from routes.api.orders import orders_routes
from routes.site.client_platform import client_platform_routes
from routes.api.trade_settings import settings_routes


@app.route('/api-map')
def hello_world():
    return 'API MAP'


if __name__ == '__main__':
    app.register_blueprint(sellers_routes)
    app.register_blueprint(orders_routes)
    app.register_blueprint(client_platform_routes)
    app.register_blueprint(settings_routes)
    app.run(host="127.0.0.1", port="8092", debug=True)
