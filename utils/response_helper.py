from flask import jsonify


def create_resp(msg_id, result):
    resp = jsonify({'msgid': str(msg_id), 'result': result})
    resp.status_code = 200
    return resp
