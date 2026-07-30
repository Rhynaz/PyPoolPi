from typing import override

from core.hardware_interface import SensorValue
from utils.holder import Holder
from utils.log import log

from ..factory import Sensor


class MockSensor(Sensor):
    def __init__(self, value: Holder[SensorValue]) -> None:
        super().__init__(value)

    @override
    def deallocate(self) -> None:
        log("info", "Deallocating mock sensor.")
