from typing import override

from config import ConfigData, ConfigManager
from config.parts.controller_config import DiveSequenceConfig
from core.hardware_interface import MotorCommand, SensorAccess, SensorValue
from utils.log import log
from utils.timer import Timer

from ..state_machine import Extension, GeneralState, State, StateMachine
from .end_detection import EndState


class DiveState(State):
    HANGING = State.of(MotorCommand.STOP, {"close"})
    DIVING = State.of(MotorCommand.CLOSE, {"close"})
    SURFACING = State.of(MotorCommand.STOP, {"close"})


class DiveSequenceExtension(Extension):
    def __init__(self, config_manager: ConfigManager, state_machine: StateMachine, sensor: SensorAccess) -> None:
        self._config_manager = config_manager
        self._state_machine = state_machine
        self._sensor = sensor

        self._config: DiveSequenceConfig = config_manager.config.controller.dive_sequence
        self._timer = Timer("dive-sequence-timer")
        self._timer.start()

        self._config_manager.add_config_changed_callback(self._config_changed)

    @override
    def on_open(self) -> None:
        self.on_stop()

    @override
    def on_close(self) -> None:
        self.on_stop()

        if not self._config.enable or self._state_machine.get_state() != EndState.OPENED:
            return

        if self._config.use_sensor:
            log("info", "Waiting for cover start detection.")
            self._sensor.add_sensor_value_changed_callback(self._sensor_value_changed)
        else:
            self._prepare_dive()

    @override
    def on_stop(self) -> None:
        self._sensor.remove_sensor_value_changed_callback(self._sensor_value_changed)
        self._timer.reset()

    @override
    def deallocate(self) -> None:
        log("info", "Deallocating dive sequence extension.")
        self._config_manager.remove_config_changed_callback(self._config_changed)
        self._sensor.remove_sensor_value_changed_callback(self._sensor_value_changed)
        self._timer.stop()
        self._timer.join()

    def _config_changed(self, old_config: ConfigData, new_config: ConfigData) -> None:
        if old_config.controller.dive_sequence != new_config.controller.dive_sequence:
            with self._state_machine:
                self._config = new_config.controller.dive_sequence

    def _sensor_value_changed(self, old_value: SensorValue, new_value: SensorValue) -> None:
        if old_value != SensorValue.ABSENT or new_value != SensorValue.PRESENT:
            return

        log("info", "Cover start detected.")
        with self._state_machine:
            self._sensor.remove_sensor_value_changed_callback(self._sensor_value_changed)
            self._prepare_dive()

    def _prepare_dive(self) -> None:
        log("info", "Preparing to dive pool cover.")
        self._timer.set(self._config.activation_delay, self._goto_hanging)

    def _goto_hanging(self) -> None:
        log("info", "Stopping pool cover for hanging.")
        with self._state_machine:
            self._state_machine.transition_to(DiveState.HANGING)
            self._timer.set(self._config.hanging_duration, self._goto_diving)

    def _goto_diving(self) -> None:
        log("info", "Diving pool cover.")
        with self._state_machine:
            self._state_machine.transition_to(DiveState.DIVING)
            self._timer.set(self._config.diving_duration, self._goto_surfacing)

    def _goto_surfacing(self) -> None:
        log("info", "Stopping pool cover for surfacing.")
        with self._state_machine:
            self._state_machine.transition_to(DiveState.SURFACING)
            self._timer.set(self._config.surfacing_duration, self._finish_closing)

    def _finish_closing(self) -> None:
        log("info", "Finish closing pool cover.")
        self._state_machine.transition_to(GeneralState.CLOSING)
