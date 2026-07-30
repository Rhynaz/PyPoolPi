from __future__ import annotations

from abc import ABCMeta
from enum import Enum, EnumMeta, nonmember
from itertools import count
from typing import Literal

from core.controller_interface import CoverState
from core.hardware_interface import MotorAccess, MotorCommand

type Trigger = Literal["open", "close", "stop"]


class AbstractEnumMeta(EnumMeta, ABCMeta):
    pass


class State(CoverState, Enum, metaclass=AbstractEnumMeta):
    _id = nonmember(count())
    _name_to_state = nonmember(dict[str, "State"]())
    _state_to_name = nonmember(dict["State", str]())

    def __init__(self, id: int, command: MotorCommand, invalid_triggers: set[Trigger]) -> None:
        self._command = command
        self._invalid_triggers = invalid_triggers

        State._name_to_state[self.name] = self
        State._state_to_name[self] = self.name

    @property
    def name(self) -> str:
        return self._name_

    def can_trigger(self, trigger: Trigger) -> bool:
        return trigger not in self._invalid_triggers

    def activate(self, motor: MotorAccess) -> None:
        motor.send_motor_command(self._command)

    @staticmethod
    def encode(state: State) -> str:
        return State._state_to_name.get(state, "")

    @staticmethod
    def decode(name: str) -> State:
        return State._name_to_state.get(name, GeneralState.STOPPED)

    @staticmethod
    def of(command: MotorCommand, invalid_triggers: set[Trigger]) -> tuple[int, MotorCommand, set[Trigger]]:
        return next(State._id), command, invalid_triggers


class GeneralState(State):
    STOPPED = State.of(MotorCommand.STOP, {"stop"})
    OPENING = State.of(MotorCommand.OPEN, {"open"})
    CLOSING = State.of(MotorCommand.CLOSE, {"close"})
