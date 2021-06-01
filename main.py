from app_config import app, manager
from flask_pymongo import PyMongo
from routes.api.sellers_routes import sellers_routes

mongo = PyMongo(app)


@app.route('/api-map')
def hello_world():
    return 'API MAP'


if __name__ == '__main__':
    app.register_blueprint(sellers_routes)
    app.run(host="127.0.0.1", port="8092", debug=True)