from typing import cast

from flask import Flask, Response, current_app, request

from config import ConfigManager
from core.controller_interface import CoverController
from utils.log import log


class FlaskApp(Flask):
    config_manager: ConfigManager
    controller: CoverController


def create_flask_app(config_manager: ConfigManager, controller: CoverController) -> FlaskApp:
    log("info", "Creating Flask app.")
    app = FlaskApp(__name__)

    app.url_map.strict_slashes = False

    app.config_manager = config_manager
    app.controller = controller

    app.before_request(_log_request)
    app.after_request(_log_response)

    from .routes.command import COMMAND
    from .routes.config import CONFIG
    from .routes.events import EVENTS
    from .routes.index import INDEX
    from .routes.log import LOG
    from .routes.status import STATUS

    app.register_blueprint(INDEX)
    app.register_blueprint(COMMAND)
    app.register_blueprint(STATUS)
    app.register_blueprint(CONFIG)
    app.register_blueprint(LOG)
    app.register_blueprint(EVENTS)

    return app


def get_flask_app() -> FlaskApp:
    return cast(FlaskApp, current_app)


def _log_request() -> None:
    if _should_log():
        log("info", f"{request.method} request received for: {request.path}")


def _log_response(response: Response) -> Response:
    if _should_log():
        log("info", f"{response.status} response sent for: {request.path}")
    return response


def _should_log() -> bool:
    excluded_http_paths = get_flask_app().config_manager.config.log.excluded_http_paths

    for path in excluded_http_paths:
        if request.path == path or request.path.startswith(path + "/"):
            return False

    return True
