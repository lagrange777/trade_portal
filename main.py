from app_config import app
from routes.api.sellers import sellers_routes


@app.route('/api-map')
def hello_world():
    return 'API MAP'


if __name__ == '__main__':
    app.register_blueprint(sellers_routes)
    app.run(host="127.0.0.1", port="8092", debug=True)
