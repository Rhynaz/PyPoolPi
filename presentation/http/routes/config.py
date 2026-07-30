from flask import Blueprint, request
from mashumaro.codecs.json import JSONDecoder, JSONEncoder

from config import ConfigData

from ..flask_app import get_flask_app

CONFIG = Blueprint("config", __name__, url_prefix="/config")

_ENCODER = JSONEncoder(ConfigData)
_DECODER = JSONDecoder(ConfigData)


@CONFIG.get("/")
def view_config():
    json = _ENCODER.encode(get_flask_app().config_manager.config)
    return json, {"Content-Type": "application/json"}


@CONFIG.put("/")
def change_config():
    json = request.get_data(as_text=True)

    try:
        get_flask_app().config_manager.config = _DECODER.decode(json)
        return "", 204  # No Content
    except Exception:  # noqa: BLE001
        return {"error": "could not decode config value"}, 400  # Bad Request
