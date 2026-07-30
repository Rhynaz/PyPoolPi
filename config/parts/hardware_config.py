from dataclasses import dataclass, field
from typing import Literal

from ..base_config import BaseConfig


@dataclass
class MockMotorConfig(BaseConfig):
    implementation: Literal["mock_motor"] = "mock_motor"


@dataclass
class GpiozeroMotorConfig(BaseConfig):
    implementation: Literal["gpiozero_motor"] = "gpiozero_motor"

    motor_pin1: int = 22
    motor_pin2: int = 23

    active_low: bool = False
    invert_polarity: bool = False
    reversing_delay: float = 1.5  # seconds


type MotorConfig = MockMotorConfig | GpiozeroMotorConfig


@dataclass
class MockSensorConfig(BaseConfig):
    implementation: Literal["mock_sensor"] = "mock_sensor"


@dataclass
class GpiozeroSensorConfig(BaseConfig):
    implementation: Literal["gpiozero_sensor"] = "gpiozero_sensor"

    power_pin: int = 27
    power_active_low: bool = False

    sense_pin: int = 17
    sense_active_low: bool = False
    sense_floating: bool = False
    sense_debounce_duration: float = 0.5  # seconds


type SensorConfig = MockSensorConfig | GpiozeroSensorConfig


@dataclass
class HardwareConfig(BaseConfig):
    motor: MotorConfig = field(default_factory=MockMotorConfig)
    sensor: SensorConfig = field(default_factory=MockSensorConfig)
