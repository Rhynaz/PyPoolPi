from abc import ABC, abstractmethod
from enum import Enum, auto

from utils.holder import ValueChangedCallback


class MotorCommand(Enum):
    OPEN = auto()
    CLOSE = auto()
    STOP = auto()


class SensorValue(Enum):
    ABSENT = auto()
    PRESENT = auto()


type SensorValueChangedCallback = ValueChangedCallback[SensorValue]


class MotorAccess(ABC):
    @abstractmethod
    def send_motor_command(self, command: MotorCommand) -> None:
        pass


class SensorAccess(ABC):
    @abstractmethod
    def retrieve_sensor_value(self) -> SensorValue:
        pass

    @abstractmethod
    def add_sensor_value_changed_callback(self, callback: SensorValueChangedCallback) -> None:
        pass

    @abstractmethod
    def remove_sensor_value_changed_callback(self, callback: SensorValueChangedCallback) -> None:
        pass
