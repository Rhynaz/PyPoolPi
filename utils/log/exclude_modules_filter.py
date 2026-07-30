from logging import Filter, LogRecord
from typing import override


class ExcludeModulesFilter(Filter):
    excludes = property()

    def __init__(self):
        super().__init__()
        self._excludes = set[str]()

    @excludes.getter
    def excludes(self):
        return self._excludes

    @excludes.setter
    def excludes(self, excludes: set[str]):
        self._excludes = set(excludes)

    @override
    def filter(self, record: LogRecord) -> bool:
        for module in self._excludes:
            if record.name == module or record.name.startswith(module + "."):
                return False

        return True
