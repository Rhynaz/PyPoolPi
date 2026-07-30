from typing import override

from config import ConfigData, ConfigManager
from config.parts.controller_config import EndDetectionConfig
from controller.state_machine.state import Trigger
from core.hardware_interface import MotorCommand, SensorAccess, SensorValue
from utils.log import log
from utils.timer import Timer

from ..state_machine import Extension, State, StateMachine


class EndState(State):
    OPENED = State.of(MotorCommand.STOP, {"stop", "open"})
    CLOSED = State.of(MotorCommand.STOP, {"stop", "close"})


class EndDetectionExtension(Extension):
    def __init__(self, config_manager: ConfigManager, state_machine: StateMachine, sensor: SensorAccess) -> None:
        self._config_manager = config_manager
        self._state_machine = state_machine
        self._sensor = sensor

        self._config: EndDetectionConfig = config_manager.config.controller.end_detection
        self._trigger: Trigger = "stop"
        self._timer = Timer("end-detection-timer")
        self._timer.start()

        self._config_manager.add_config_changed_callback(self._config_changed)

    @override
    def on_open(self) -> None:
        self.on_stop()

        if self._config.enable:
            log("info", "Waiting for cover end detection.")
            self._trigger = "open"
            self._sensor.add_sensor_value_changed_callback(self._sensor_value_changed)

    @override
    def on_close(self) -> None:
        self.on_stop()

        if self._config.enable:
            log("info", "Waiting for cover end detection.")
            self._trigger = "close"
            self._sensor.add_sensor_value_changed_callback(self._sensor_value_changed)

    @override
    def on_stop(self) -> None:
        self._sensor.remove_sensor_value_changed_callback(self._sensor_value_changed)
        self._timer.reset()
        self._trigger = "stop"

    @override
    def deallocate(self) -> None:
        log("info", "Deallocating end detection extension.")
        self._config_manager.remove_config_changed_callback(self._config_changed)
        self._sensor.remove_sensor_value_changed_callback(self._sensor_value_changed)
        self._timer.stop()
        self._timer.join()

    def _config_changed(self, old_config: ConfigData, new_config: ConfigData) -> None:
        if old_config.controller.end_detection != new_config.controller.end_detection:
            with self._state_machine:
                self._config = new_config.controller.end_detection

    def _sensor_value_changed(self, old_value: SensorValue, new_value: SensorValue) -> None:
        if old_value != SensorValue.PRESENT or new_value != SensorValue.ABSENT:
            return

        log("info", "Cover end detected, preparing to stop.")
        with self._state_machine:
            self._sensor.remove_sensor_value_changed_callback(self._sensor_value_changed)

            if self._trigger == "open":
                self._timer.set(
                    self._config.opening_overrun_duration,
                    lambda: self._state_machine.stop_cover(EndState.OPENED),
                )

            if self._trigger == "close":
                self._timer.set(
                    self._config.closing_overrun_duration,
                    lambda: self._state_machine.stop_cover(EndState.CLOSED),
                )
