from threading import Lock
from typing import override

from config import ConfigData, ConfigManager
from core.controller_interface import CoverState
from core.persistence_interface import CoverStatePersistence, Decoder, Encoder
from utils.log import log

from .factory import create_persistence_target


class ConfigBasedPersistenceProvider(CoverStatePersistence):
    def __init__(self, config_manager: ConfigManager):
        self._config_manager = config_manager

        self._lock = Lock()
        self._state_target = create_persistence_target("cover state", config_manager.config.persistence.cover_state)

        self._config_manager.add_config_changed_callback(self._config_changed)

    @override
    def load_cover_state[S: CoverState](self, decode: Decoder[S]) -> S:
        with self._lock:
            state = decode(self._state_target.load())
            log("info", f"Loaded state: {state.name}")
            return state

    @override
    def store_cover_state[S: CoverState](self, encode: Encoder[S], state: S) -> None:
        with self._lock:
            self._state_target.store(encode(state))
            log("info", f"Stored state: {state.name}")

    def shutdown(self) -> None:
        log("info", "Shutting down.")
        self._config_manager.remove_config_changed_callback(self._config_changed)

        with self._lock:
            self._state_target.deallocate()

    def _config_changed(self, old_config: ConfigData, new_config: ConfigData):
        if old_config.persistence.cover_state == new_config.persistence.cover_state:
            return

        with self._lock:
            self._state_target.deallocate()
            self._state_target = create_persistence_target("cover state", new_config.persistence.cover_state)


__all__ = ["ConfigBasedPersistenceProvider"]
