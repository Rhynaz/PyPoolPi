from queue import Queue, ShutDown
from threading import Thread
from time import sleep
from typing import override

from gpiozero import OutputDevice

from config import GpiozeroMotorConfig
from utils.log import log

from ..factory import Motor, MotorCommand


class GpiozeroMotor(Motor):
    def __init__(self, config: GpiozeroMotorConfig) -> None:
        self._config = config
        self._pin1 = OutputDevice(config.motor_pin1, active_high=not config.active_low)
        self._pin2 = OutputDevice(config.motor_pin2, active_high=not config.active_low)

        self._queue = Queue[MotorCommand]()
        self._thread = Thread(name="motor-thread", target=self._process_commands)
        self._thread.start()

    @override
    def receive_command(self, command: MotorCommand) -> None:
        log("info", f"Received motor command: {command.name}")
        try:
            self._queue.put(command)
        except ShutDown:
            log("warning", f"Ignored motor command: {command.name}")

    @override
    def deallocate(self) -> None:
        log("info", "Deallocating gpiozero motor.")
        self._queue.shutdown()
        self._thread.join()
        self._pin1.close()
        self._pin2.close()

    def _process_commands(self) -> None:
        log("info", "Starting to process motor commands.")
        current_command = MotorCommand.STOP
        self._set_pins(current_command)

        while True:
            try:
                command = self._queue.get()
                if current_command == command:
                    continue

                if current_command != MotorCommand.STOP and command != MotorCommand.STOP:
                    log("info", "Reversing motor.")
                    self._set_pins(MotorCommand.STOP)
                    sleep(self._config.reversing_delay)

                current_command = command
                self._set_pins(command)

            except ShutDown:
                log("info", "Stopping to process motor commands.")
                self._set_pins(MotorCommand.STOP)
                return

    def _set_pins(self, command: MotorCommand) -> None:
        if command == MotorCommand.STOP:
            log("info", "Setting motor pins: (OFF, OFF)")
            self._pin1.off()
            self._pin2.off()
            return

        polarity = command == MotorCommand.OPEN

        if polarity != self._config.invert_polarity:
            log("info", "Setting motor pins: (ON, OFF)")
            self._pin1.on()
            self._pin2.off()
        else:
            log("info", "Setting motor pins: (OFF, ON)")
            self._pin1.off()
            self._pin2.on()
