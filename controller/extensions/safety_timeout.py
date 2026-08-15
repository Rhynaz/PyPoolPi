from typing import override

from config import ConfigData, ConfigManager
from config.parts.controller_config import SafetyTimeoutConfig
from utils.log import log
from utils.timer import Timer

from ..state_machine import Extension, StateMachine


class SafetyTimeoutExtension(Extension):
    def __init__(self, config_manager: ConfigManager, state_machine: StateMachine) -> None:
        self._config_manager = config_manager
        self._state_machine = state_machine

        self._config: SafetyTimeoutConfig = config_manager.config.controller.safety_timeout
        self._timer = Timer("safety-timeout-timer")
        self._timer.start()

        self._config_manager.add_config_changed_callback(self._config_changed)

    @override
    def on_open(self) -> None:
        if not self._config.enable:
            self.on_stop()
            return

        log("info", "Starting opening timeout.")
        self._timer.set(self._config.max_opening_duration, self._on_timeout)

    @override
    def on_close(self) -> None:
        if not self._config.enable:
            self.on_stop()
            return

        log("info", "Starting closing timeout.")
        self._timer.set(self._config.max_closing_duration, self._on_timeout)

    @override
    def on_stop(self) -> None:
        self._timer.reset()

    @override
    def deallocate(self) -> None:
        log("info", "Deallocating safety timeout extension.")
        self._config_manager.remove_config_changed_callback(self._config_changed)
        self._timer.stop()
        self._timer.join()

    def _config_changed(self, old_config: ConfigData, new_config: ConfigData) -> None:
        if old_config.controller.safety_timeout != new_config.controller.safety_timeout:
            with self._state_machine:
                self._config = new_config.controller.safety_timeout

    def _on_timeout(self) -> None:
        log("info", "Safety timeout has elapsed.")
        _ = self._state_machine.stop_cover()
