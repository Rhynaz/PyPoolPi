from abc import ABC, abstractmethod

from config import MotorConfig, SensorConfig
from core.hardware_interface import MotorCommand, SensorValue
from utils.holder import Holder, HolderProperty
from utils.log import log


class Motor(ABC):
    @abstractmethod
    def receive_command(self, command: MotorCommand) -> None:
        pass

    @abstractmethod
    def deallocate(self) -> None:
        pass


class Sensor(ABC):
    _value = HolderProperty(SensorValue.ABSENT)

    def __init__(self, value: Holder[SensorValue]) -> None:
        HolderProperty.change_holder(self, Sensor._value, value)

    @abstractmethod
    def deallocate(self) -> None:
        pass


def create_motor(config: MotorConfig) -> Motor:
    log("info", f"Instantiating motor implementation: {config.implementation}")
    match config.implementation:
        case "gpiozero_motor":
            from .motor.gpiozero_motor import GpiozeroMotor

            return GpiozeroMotor(config)

        case "mock_motor":
            pass

        case _:
            log(
                "error",
                f"Unknown motor implementation (falling back to mock): {config.implementation}",
            )

    from .motor.mock_motor import MockMotor

    return MockMotor()


def create_sensor(config: SensorConfig, value: Holder[SensorValue]) -> Sensor:
    log("info", f"Instantiating sensor implementation: {config.implementation}")
    match config.implementation:
        case "gpiozero_sensor":
            from .sensor.gpiozero_sensor import GpiozeroSensor

            return GpiozeroSensor(value, config)

        case "mock_sensor":
            pass

        case _:
            log(
                "error",
                f"Unknown sensor implementation (falling back to mock): {config.implementation}",
            )

    from .sensor.mock_sensor import MockSensor

    return MockSensor(value)
