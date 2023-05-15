import datetime

from flask import request
from flask_socketio import SocketIO, emit, disconnect
from threading import Lock

from app_config import app

async_mode = None
socketio = SocketIO(app, async_mode=async_mode)

thread = None
thread_lock = Lock()


def get_current_datetime():
    offset = datetime.timezone(datetime.timedelta(hours=3))
    now = datetime.datetime.now(offset)
    return now.strftime("%d/%m/%Y %H:%M:%S")


def background_thread():
    print("Generating random sensor values")
    while True:
        socketio.emit(
            'time update',
            {
                "date": get_current_datetime()
            }
        )
        socketio.sleep(1)


@socketio.on('connect')
def connect():
    global thread
    print('Client connected')

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)


@socketio.on('disconnect')
def disconnect():
    print(f'Client disconnected')
