from logging import LogRecord
from typing import Any

from paho.mqtt.client import Client, MQTTMessage

from config import MqttTopicConfig
from core.controller_interface import CoverController, CoverState
from utils.log import add_log_emitted_callback, log, remove_log_emitted_callback


class MqttApp:
    def __init__(self, controller: CoverController) -> None:
        self._connect_failed = False
        self._controller = controller

    def change_client(self, client: Client):
        self._client = client

    def change_topics(self, topics: MqttTopicConfig):
        self._topics = topics

    def on_connect(self) -> None:
        log("info", "Connected to MQTT broker.")
        self._controller.add_cover_state_changed_callback(self._state_changed)
        add_log_emitted_callback(self._log_emitted)

        self._client.message_callback_add(self._topics.command, self._command_message)
        self._client.subscribe(self._topics.command, 2)
        self._connect_failed = False

    def on_connect_fail(self) -> None:
        if not self._connect_failed:
            log("info", "Failed to connect MQTT broker.")

        self._connect_failed = True

    def on_disconnect(self) -> None:
        log("info", "Disconnected from MQTT broker.")
        self._client.unsubscribe(self._topics.command)
        self._client.message_callback_remove(self._topics.command)

        remove_log_emitted_callback(self._log_emitted)
        self._controller.remove_cover_state_changed_callback(self._state_changed)

    def _state_changed(self, _old_state: CoverState, new_state: CoverState) -> None:
        log("info", f"Publishing cover state to: {self._topics.cover_state}")
        self._client.publish(self._topics.cover_state, new_state.name, 1, True)

    def _log_emitted(self, _record: LogRecord, line: str) -> None:
        self._client.publish(self._topics.log, line, 1)

    def _command_message(self, _client: Client, _userdata: Any, message: MQTTMessage) -> None:
        log("info", f"Received message on: {self._topics.command}")
        command = message.payload.decode().lower().strip()

        match command:
            case "open":
                self._controller.trigger_cover_open()

            case "close":
                self._controller.trigger_cover_close()

            case "stop":
                self._controller.trigger_cover_stop()
