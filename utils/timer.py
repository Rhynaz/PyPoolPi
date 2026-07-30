from collections.abc import Callable
from threading import Event, Thread
from typing import Any


class Timer(Thread):
    def __init__(self, name: str) -> None:
        super().__init__(name=name)
        self._reset = Event()
        self._duration = None
        self._callback = None
        self._stop = False

    def set(self, duration: float, callback: Callable[[], Any]) -> None:
        self._duration = duration
        self._callback = callback
        self._reset.set()

    def reset(self) -> None:
        self._duration = None
        self._callback = None
        self._reset.set()

    def stop(self) -> None:
        self._stop = True
        self._reset.set()

    def run(self):
        while True:
            self._reset.wait(self._duration)

            if not self._reset.is_set() and self._callback is not None:
                callback = self._callback
                self._duration = None
                self._callback = None
                callback()

            self._reset.clear()

            if self._stop:
                break
