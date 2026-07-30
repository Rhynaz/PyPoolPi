from threading import Lock, Thread

from config import ConfigData, ConfigManager
from core.controller_interface import CoverController
from utils.log import log

from .mqtt_app import MqttApp
from .paho_client import create_paho_client


class PahoMqttFrontend:
    def __init__(self, config_manager: ConfigManager, controller: CoverController) -> None:
        self._config_manager = config_manager

        self._lock = Lock()
        self._app = MqttApp(controller)
        self._client = None
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
        config = self._config_manager.config.mqtt
        if not config.enable:
            return

        log("info", f"Connecting MQTT client to: mqtt://{config.host}:{config.port}/")
        self._client = create_paho_client(config, self._app)
        self._thread = Thread(name="mqtt-thread", target=self._client.loop_forever)
        self._thread.start()

    def _stop(self) -> None:
        if self._client is not None and self._thread is not None:
            log("info", "Disconnecting MQTT client.")
            self._client.disconnect()
            self._thread.join()

        self._client = None
        self._thread = None

    def _config_changed(self, old_config: ConfigData, new_config: ConfigData):
        if old_config.mqtt == new_config.mqtt:
            return

        with self._lock:
            self._stop()
            self._start()
