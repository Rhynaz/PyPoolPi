from threading import Lock, Thread

from waitress.server import create_server

from config import ConfigData, ConfigManager
from core.controller_interface import CoverController
from utils.log import log

from .flask_app import create_flask_app


class FlaskHttpFrontend:
    def __init__(self, config_manager: ConfigManager, controller: CoverController) -> None:
        self._config_manager = config_manager

        self._lock = Lock()
        self._app = create_flask_app(config_manager, controller)
        self._server = None
        self._thread = None

        with self._lock:
            self._start()

        self._config_manager.add_config_changed_callback(self._config_changed)

    def shutdown(self) -> None:
        log("info", "Shutting down.")
        self._config_manager.remove_config_changed_callback(self._config_changed)

        with self._lock:
            self._stop()

    def _start(self) -> None:
        config = self._config_manager.config.http
        if not config.enable:
            return

        log("info", f"Starting HTTP server on: http://{config.interface}:{config.port}/")
        self._server = create_server(self._app, host=config.interface, port=config.port, threads=config.thread_count)
        self._thread = Thread(name="http-thread", target=self._server.run, daemon=True)
        self._thread.start()

    def _stop(self) -> None:
        if self._server is not None and self._thread is not None:
            log("info", "Stopping HTTP server.")
            self._server.close()
            self._thread.join(5)  # workaround for waitress not stopping sometimes

        self._server = None
        self._thread = None

    def _config_changed(self, old_config: ConfigData, new_config: ConfigData):
        if old_config.http == new_config.http:
            return

        with self._lock:
            self._stop()
            self._start()
