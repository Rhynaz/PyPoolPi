from typing import override

from utils.log import log

from ..factory import Motor, MotorCommand


class MockMotor(Motor):
    @override
    def receive_command(self, command: MotorCommand) -> None:
        log("info", f"Received motor command: {command.name}")

    @override
    def deallocate(self) -> None:
        log("info", "Deallocating mock motor.")
