from contextlib import contextmanager
from copy import deepcopy
from threading import RLock

from utils.caller_name import get_caller_module_name
from utils.holder import Holder, ValueChangedCallback
from utils.log import log

from .data import ConfigData

type ConfigChangedCallback = ValueChangedCallback[ConfigData]


class ConfigManager:
    config = property()

    def __init__(self) -> None:
        self._config = Holder(ConfigData())
        self._lock = RLock()
        self._config.get()._bind(self, [])

    @config.getter
    def config(self) -> ConfigData:
        with self._lock:
            return self._config.get()

    @config.setter
    def config(self, new_config: ConfigData) -> None:
        log("info", f"Setting config from: {get_caller_module_name()}")
        with self._lock:
            old_config = self._config.get()

            old_config._unbind()
            new_config._bind(self, [])

            self._config.set(new_config)

    @contextmanager
    def change_config(self):
        with self._lock:
            old_config = self._config.get()
            new_config = deepcopy(old_config)

            yield new_config

            old_config._unbind()
            new_config._bind(self, [])

            self._config.set(new_config)

    def add_config_changed_callback(self, callback: ConfigChangedCallback) -> None:
        log("info", f"Adding config callback for: {get_caller_module_name()}")
        self._config.add_value_changed_callback(callback)

    def remove_config_changed_callback(self, callback: ConfigChangedCallback) -> None:
        log("info", f"Removing config callback for: {get_caller_module_name()}")
        self._config.remove_value_changed_callback(callback)

    def shutdown(self) -> None:
        log("info", "Shutting down.")
        with self._lock:
            self._config.get()._unbind()
            self._config.deallocate()
