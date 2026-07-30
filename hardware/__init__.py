from threading import Lock
from typing import override

from config import ConfigData, ConfigManager
from core.hardware_interface import MotorAccess, MotorCommand, SensorAccess, SensorValue, SensorValueChangedCallback
from utils.caller_name import get_caller_module_name
from utils.holder import Holder
from utils.log import log

from .factory import create_motor, create_sensor


class ConfigBasedHardwareAccess(MotorAccess, SensorAccess):
    def __init__(self, config_manager: ConfigManager) -> None:
        self._config_manager = config_manager

        self._lock = Lock()
        self._value = Holder(SensorValue.ABSENT)
        self._value.add_value_changed_callback(self._value_changed)

        self._motor = create_motor(config_manager.config.hardware.motor)
        self._sensor = create_sensor(config_manager.config.hardware.sensor, self._value)

        self._config_manager.add_config_changed_callback(self._config_changed)

    @override
    def send_motor_command(self, command: MotorCommand) -> None:
        log("info", f"Sending motor command: {command.name}")
        with self._lock:
            self._motor.receive_command(command)

    @override
    def retrieve_sensor_value(self) -> SensorValue:
        value = self._value.get()
        log("info", f"Retrieved sensor value: {value}")
        return value

    @override
    def add_sensor_value_changed_callback(self, callback: SensorValueChangedCallback) -> None:
        log("info", f"Adding sensor value callback for: {get_caller_module_name()}")
        self._value.add_value_changed_callback(callback)

    @override
    def remove_sensor_value_changed_callback(self, callback: SensorValueChangedCallback) -> None:
        log("info", f"Removing sensor value callback for: {get_caller_module_name()}")
        self._value.remove_value_changed_callback(callback)

    def shutdown(self) -> None:
        log("info", "Shutting down.")
        self._config_manager.remove_config_changed_callback(self._config_changed)

        with self._lock:
            self._motor.deallocate()
            self._sensor.deallocate()

        self._value.remove_value_changed_callback(self._value_changed)
        self._value.deallocate()

    def _config_changed(self, old_config: ConfigData, new_config: ConfigData):
        if old_config.hardware == new_config.hardware:
            return

        with self._lock:
            self._motor.deallocate()
            self._motor = create_motor(new_config.hardware.motor)

            self._sensor.deallocate()
            self._sensor = create_sensor(new_config.hardware.sensor, self._value)

    def _value_changed(self, old_value: SensorValue, new_value: SensorValue) -> None:
        log("info", f"Sensor value changed: {old_value.name} -> {new_value.name}")


__all__ = ["ConfigBasedHardwareAccess"]
