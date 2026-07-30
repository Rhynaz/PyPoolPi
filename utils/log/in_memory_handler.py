from collections import deque
from logging import Handler, LogRecord
from threading import Lock
from typing import Callable, override

type LogEmittedCallback = Callable[[LogRecord, str], None]


class InMemoryHandler(Handler):
    size = property()
    records = property()
    lines = property()

    def __init__(self) -> None:
        super().__init__()
        self._records = deque[LogRecord]()
        self._callbacks = set[LogEmittedCallback]()
        self._lock = Lock()

    @size.getter
    def size(self) -> int:
        with self._lock:
            return self._records.maxlen if self._records.maxlen is not None else 0

    @size.setter
    def size(self, max_records: int) -> None:
        with self._lock:
            self._records = deque(self._records, max_records)

    @records.getter
    def records(self) -> list[LogRecord]:
        with self._lock:
            return list(self._records)

    @lines.getter
    def lines(self) -> list[str]:
        with self._lock:
            return [self._to_line(record) for record in self._records]

    def add_log_emitted_callback(self, callback: LogEmittedCallback):
        with self._lock:
            self._callbacks.add(callback)

    def remove_log_emitted_callback(self, callback: LogEmittedCallback):
        with self._lock:
            self._callbacks.discard(callback)

    @override
    def emit(self, record: LogRecord) -> None:
        with self._lock:
            self._records.append(record)
            callbacks = list(self._callbacks)

        for callback in callbacks:
            callback(record, self._to_line(record))

    def _to_line(self, record: LogRecord) -> str:
        return self.format(record).splitlines()[0]
