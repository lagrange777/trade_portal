from flask import request, Blueprint

from app_config import mongo
from utils.response_helper import create_resp

settings_routes = Blueprint('settings_routes', __name__, url_prefix='/api/settings/')


@settings_routes.route('set-schedule', methods=['POST'])
def set_schedule():
    _json = request.json
    main_hour_start = _json['MAIN_HOUR_START']
    main_hour_finish = _json['MAIN_HOUR_FINISH']
    main_minute_start = _json['MAIN_MINUTE_START']
    main_minute_finish = _json['MAIN_MINUTE_FINISH']

    add_hour_start = _json['ADD_HOUR_START']
    add_hour_finish = _json['ADD_HOUR_FINISH']
    add_minute_start = _json['ADD_MINUTE_START']
    add_minute_finish = _json['ADD_MINUTE_FINISH']

    mongo.db['SETTINGS'].drop()

    mongo.db['SETTINGS'].insert_one(
        {
            'MAIN_HOUR_START': int(main_hour_start),
            'MAIN_HOUR_FINISH': int(main_hour_finish),
            'MAIN_MINUTE_START': int(main_minute_start),
            'MAIN_MINUTE_FINISH': int(main_minute_finish),
            'ADD_HOUR_START': int(add_hour_start),
            'ADD_HOUR_FINISH': int(add_hour_finish),
            'ADD_MINUTE_START': int(add_minute_start),
            'ADD_MINUTE_FINISH': int(add_minute_finish)
        }
    )

    msg_id = 0
    result = 'success'

    return create_resp(msg_id, result)


@settings_routes.route('get_schedule', methods=['POST'])
def get_schedule():
    _json = request.json
    schedule_db = mongo.db['SETTINGS'].find()

    schedule = {
            'MAIN_HOUR_START': schedule_db['MAIN_HOUR_START'],
            'MAIN_HOUR_FINISH': schedule_db['MAIN_HOUR_FINISH'],
            'MAIN_MINUTE_START': schedule_db['MAIN_MINUTE_START'],
            'MAIN_MINUTE_FINISH': schedule_db['MAIN_MINUTE_FINISH'],
            'ADD_HOUR_START': schedule_db['ADD_HOUR_START'],
            'ADD_HOUR_FINISH': schedule_db['ADD_HOUR_FINISH'],
            'ADD_MINUTE_START': schedule_db['ADD_MINUTE_START'],
            'ADD_MINUTE_FINISH': schedule_db['ADD_MINUTE_FINISH']
        }

    msg_id = 0
    result = schedule

    return create_resp(msg_id, result)
