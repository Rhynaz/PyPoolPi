from typing import override

from gpiozero import DigitalInputDevice, OutputDevice

from config import GpiozeroSensorConfig
from core.hardware_interface import SensorValue
from utils.holder import Holder
from utils.log import log

from ..factory import Sensor


class GpiozeroSensor(Sensor):
    def __init__(self, value: Holder[SensorValue], config: GpiozeroSensorConfig) -> None:
        super().__init__(value)
        self._power_pin = OutputDevice(config.power_pin, active_high=not config.power_active_low)
        self._sense_pin = DigitalInputDevice(
            config.sense_pin,
            pull_up=config.sense_active_low if not config.sense_floating else None,  # pyright: ignore[reportArgumentType]
            active_state=not config.sense_active_low if config.sense_floating else None,
            bounce_time=config.sense_debounce_duration,
        )

        self._sense_pin.when_activated = self._value_changed
        self._sense_pin.when_deactivated = self._value_changed
        self.set_enabled(False)

    @override
    def set_enabled(self, enable: bool) -> None:
        if enable:
            log("info", "Setting sensor power pin: ON")
            self._power_pin.on()
        else:
            log("info", "Setting sensor power pin: OFF")
            self._power_pin.off()

    @override
    def deallocate(self) -> None:
        log("info", "Deallocating mock sensor.")
        self.set_enabled(False)
        self._power_pin.close()
        self._sense_pin.close()

    def _value_changed(self) -> None:
        if self._sense_pin.is_active:
            log("info", f"Rising edge detected: {self._value.name} -> {SensorValue.PRESENT.name}")
            self._value = SensorValue.PRESENT
        else:
            log("info", f"Falling edge detected: {self._value.name} -> {SensorValue.ABSENT.name}")
            self._value = SensorValue.ABSENT
