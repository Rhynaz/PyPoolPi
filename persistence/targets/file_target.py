from os import makedirs, path
from typing import override

from config import FilePersistenceTargetConfig
from utils.log import log

from ..factory import PersistenceTarget


class FilePersistenceTarget(PersistenceTarget):
    def __init__(self, data_name: str, config: FilePersistenceTargetConfig):
        self._data_name = data_name
        self._file_path = path.abspath(config.file_path)

    @override
    def load(self) -> str:
        log("info", f"Loading {self._data_name} from file: {self._file_path}")
        try:
            with open(self._file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:  # noqa: BLE001
            log("error", f"Failed to load {self._data_name}: {e}")
            return ""

    @override
    def store(self, data: str) -> None:
        log("info", f"Storing {self._data_name} into file: {self._file_path}")
        try:
            makedirs(path.dirname(self._file_path), exist_ok=True)
            with open(self._file_path, "w", encoding="utf-8") as file:
                file.write(data)
        except Exception as e:  # noqa: BLE001
            log("error", f"Failed to save {self._data_name}: {e}")

    @override
    def deallocate(self) -> None:
        log("info", "Deallocating file persistence target.")
