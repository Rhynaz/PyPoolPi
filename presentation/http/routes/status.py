from json import dumps

from flask import Blueprint

from ..flask_app import get_flask_app

STATUS = Blueprint("status", __name__, url_prefix="/status")


@STATUS.get("/")
def view_status():
    status = {
        "state": get_flask_app().controller.retrieve_cover_state().name,
    }

    return dumps(status), {"Content-Type": "application/json"}
