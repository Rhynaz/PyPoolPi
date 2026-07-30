from __future__ import annotations

from collections.abc import Callable, Iterable
from threading import RLock

from core.hardware_interface import MotorAccess
from utils.holder import HolderProperty, ValueChangedCallback
from utils.log import log

from .extension import Extension
from .state import GeneralState, State

type StateChangedCallback = ValueChangedCallback[State]


class StateMachine:
    _state = HolderProperty(GeneralState.STOPPED)

    def __init__(
        self,
        motor: MotorAccess,
        initial_state: State,
        extensions: Callable[[StateMachine], Iterable[Extension]],
    ) -> None:
        self._motor = motor
        self._state = initial_state

        self._lock = RLock()
        self._extensions = set(extensions(self))

    def open_cover(self) -> bool:
        with self._lock:
            if not self._state.can_trigger("open"):
                return False

            log("info", "Opening pool cover.")
            for extension in self._extensions:
                extension.on_open()

            self.transition_to(GeneralState.OPENING)
            return True

    def close_cover(self) -> bool:
        with self._lock:
            if not self._state.can_trigger("close"):
                return False

            log("info", "Closing pool cover.")
            for extension in self._extensions:
                extension.on_close()

            self.transition_to(GeneralState.CLOSING)
            return True

    def stop_cover(self, target: State = GeneralState.STOPPED) -> bool:
        with self._lock:
            if not self._state.can_trigger("stop"):
                return False

            log("info", "Stopping pool cover.")
            for extension in self._extensions:
                extension.on_stop()

            self.transition_to(target)
            return True

    def transition_to(self, target: State) -> None:
        log("info", f"Transitioning states: {self._state.name} -> {target.name}")
        with self._lock:
            self._state = target
            self._state.activate(self._motor)

    def get_state(self) -> State:
        with self._lock:
            return self._state

    def add_state_changed_callback(self, callback: StateChangedCallback) -> None:
        HolderProperty.add_value_changed_callback(self, StateMachine._state, callback)  # pyright: ignore[reportArgumentType]

    def remove_state_changed_callback(self, callback: StateChangedCallback) -> None:
        HolderProperty.remove_value_changed_callback(self, StateMachine._state, callback)  # pyright: ignore[reportArgumentType]

    def deallocate(self) -> None:
        log("info", "Deallocating state machine.")
        with self._lock:
            while len(self._extensions) > 0:
                self._extensions.pop().deallocate()

            HolderProperty.deallocate(self, StateMachine._state)  # pyright: ignore[reportArgumentType]

    def __enter__(self) -> None:
        self._lock.acquire()

    def __exit__(self, *_) -> None:
        self._lock.release()
