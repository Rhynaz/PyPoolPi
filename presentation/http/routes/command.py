from flask import Blueprint

from ..flask_app import get_flask_app

COMMAND = Blueprint("command", __name__, url_prefix="/command")


@COMMAND.post("/open")
def send_open():
    get_flask_app().controller.trigger_cover_open()
    return "", 204  # No Content


@COMMAND.post("/close")
def send_close():
    get_flask_app().controller.trigger_cover_close()
    return "", 204  # No Content


@COMMAND.post("/stop")
def send_stop():
    get_flask_app().controller.trigger_cover_stop()
    return "", 204  # No Content
