from app_config import app

from routes.v2.client_platform import client_platform_routes
from routes.v2.orders_routes import orders_routes
from routes.v2.sellers import sellers_routes
from routes.v2.ws_updater import socketio
from utils.config_manager import ConfigManager


@app.route('/api-map')
def hello_world():
    return 'API MAP'


if __name__ == '__main__':
    app.register_blueprint(orders_routes)
    app.register_blueprint(client_platform_routes)
    app.register_blueprint(sellers_routes)
    host = ConfigManager.get_host()
    port = ConfigManager.get_port()
    debug = ConfigManager.get_debug()

    socketio.run(
        app,
        host=host,
        port=port,
        allow_unsafe_werkzeug=True
    )

    # app.run(
    #     host=host,
    #     port=port,
    #     debug=debug
    # )
