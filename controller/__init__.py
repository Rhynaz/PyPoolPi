from typing import override

from config import ConfigData, ConfigManager
from core.controller_interface import CoverController, CoverState, CoverStateChangedCallback
from core.hardware_interface import MotorAccess, SensorAccess
from core.persistence_interface import CoverStatePersistence
from utils.caller_name import get_caller_module_name
from utils.log import log

from .extensions.dive_sequence import DiveSequenceExtension
from .extensions.end_detection import EndDetectionExtension
from .extensions.safety_timeout import SafetyTimeoutExtension
from .state_machine import State, StateMachine


class ExtensibleCoverController(CoverController):
    def __init__(
        self,
        config_manager: ConfigManager,
        motor: MotorAccess,
        sensor: SensorAccess,
        persistence: CoverStatePersistence,
    ) -> None:
        self._config_manager = config_manager
        self._persistence = persistence

        self._state_machine = StateMachine(
            motor,
            persistence.load_cover_state(State.decode),
            lambda state_machine: {
                EndDetectionExtension(config_manager, state_machine, sensor),
                DiveSequenceExtension(config_manager, state_machine, sensor),
                SafetyTimeoutExtension(config_manager, state_machine),
            },
        )

        self._state_machine.add_state_changed_callback(self._state_changed)
        self._config_manager.add_config_changed_callback(self._config_changed)

    @override
    def trigger_cover_open(self) -> None:
        log("info", "Triggering pool cover open.")
        if not self._state_machine.open_cover():
            log("info", "Ignored trigger (already opening/opened).")

    @override
    def trigger_cover_close(self) -> None:
        log("info", "Triggering pool cover close.")
        if not self._state_machine.close_cover():
            log("info", "Ignoring trigger (already closing/closed).")

    @override
    def trigger_cover_stop(self) -> None:
        log("info", "Triggering pool cover stop.")
        if not self._state_machine.stop_cover():
            log("info", "Ignoring trigger (already stopped).")

    @override
    def retrieve_cover_state(self) -> CoverState:
        state = self._state_machine.get_state()
        log("info", f"Retrieved pool cover state: {state.name}")
        return state

    @override
    def add_cover_state_changed_callback(self, callback: CoverStateChangedCallback) -> None:
        log("info", f"Adding cover state callback for: {get_caller_module_name()}")
        self._state_machine.add_state_changed_callback(callback)

    @override
    def remove_cover_state_changed_callback(self, callback: CoverStateChangedCallback) -> None:
        log("info", f"Removing cover state callback for: {get_caller_module_name()}")
        self._state_machine.remove_state_changed_callback(callback)

    def shutdown(self) -> None:
        log("info", "Shutting down.")
        self._config_manager.remove_config_changed_callback(self._config_changed)
        self._state_machine.remove_state_changed_callback(self._state_changed)
        self._state_machine.deallocate()

    def _state_changed(self, _old_state: State, new_state: State) -> None:
        self._persistence.store_cover_state(State.encode, new_state)

    def _config_changed(self, old_config: ConfigData, new_config: ConfigData):
        if old_config.hardware != new_config.hardware:
            self.trigger_cover_stop()


__all__ = ["ExtensibleeCoverController"]
