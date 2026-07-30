from os import path
from typing import override

from mashumaro.codecs.toml import TOMLDecoder, TOMLEncoder
from watchdog.events import (
    EVENT_TYPE_CREATED,
    EVENT_TYPE_MODIFIED,
    EVENT_TYPE_MOVED,
    FileSystemEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

from config import ConfigData, ConfigManager, FilePersistenceTargetConfig
from persistence.targets.file_target import FilePersistenceTarget
from utils.log import log

_ENCODER = TOMLEncoder(ConfigData)
_DECODER = TOMLDecoder(ConfigData)


class ConfigFile(FileSystemEventHandler):
    def __init__(self, config_manager: ConfigManager, file_path: str):
        self._config_manager = config_manager
        self._file_path = path.abspath(file_path)

        self._target = FilePersistenceTarget("config", FilePersistenceTargetConfig(file_path=file_path))
        self._load_config()
        self._store_config()

        self._observer = Observer()
        self._observer.schedule(self, path.dirname(self._file_path))
        self._observer.start()

        self._config_manager.add_config_changed_callback(self._config_changed)

    def shutdown(self) -> None:
        log("info", "Shutting down.")
        self._config_manager.remove_config_changed_callback(self._config_changed)
        self._observer.stop()
        self._observer.join()
        del self._observer

    @override
    def on_any_event(self, event: FileSystemEvent) -> None:
        log("debug", f"Event in watched folder: {event}")
        if event.is_directory or event.event_type not in (
            EVENT_TYPE_MODIFIED,
            EVENT_TYPE_CREATED,
            EVENT_TYPE_MOVED,
        ):
            return

        if event.src_path != self._file_path and event.dest_path != self._file_path:
            return

        self._load_config()

    def _config_changed(self, _old_config: ConfigData, _new_config: ConfigData) -> None:
        self._store_config()

    def _load_config(self) -> None:
        try:
            data = self._target.load()
            if data == "":
                return

            self._config_manager.config = _DECODER.decode(data)
        except Exception as e:  # noqa: BLE001
            log("error", f"Failed to decode config: {e}")

    def _store_config(self) -> None:
        try:
            data: str = _ENCODER.encode(self._config_manager.config)  # pyright: ignore[reportAssignmentType] because of https://github.com/Fatal1ty/mashumaro/issues/328
            if data == "":
                return

            self._target.store(data)
        except Exception as e:  # noqa: BLE001
            log("error", f"Failed to encode config: {e}")
