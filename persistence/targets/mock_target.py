from typing import override

from utils.log import log

from ..factory import PersistenceTarget


class MockPersistenceTarget(PersistenceTarget):
    def __init__(self, data_name: str):
        self._data_name = data_name
        self._data = ""

    @override
    def load(self) -> str:
        log("info", f"Loading {self._data_name} from mock.")
        return self._data

    @override
    def store(self, data: str) -> None:
        log("info", f"Storing {self._data_name} into mock.")
        self._data = data

    @override
    def deallocate(self) -> None:
        log("info", "Deallocating mock persistence target.")
