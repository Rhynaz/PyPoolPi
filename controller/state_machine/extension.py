from abc import ABC, abstractmethod


class Extension(ABC):
    @abstractmethod
    def on_open(self) -> None:
        pass

    @abstractmethod
    def on_close(self) -> None:
        pass

    @abstractmethod
    def on_stop(self) -> None:
        pass

    @abstractmethod
    def deallocate(self) -> None:
        pass
