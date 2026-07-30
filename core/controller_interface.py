from abc import ABC, abstractmethod

from utils.holder import ValueChangedCallback


class CoverState(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass


type CoverStateChangedCallback = ValueChangedCallback[CoverState]


class CoverController(ABC):
    @abstractmethod
    def trigger_cover_open(self) -> None:
        pass

    @abstractmethod
    def trigger_cover_close(self) -> None:
        pass

    @abstractmethod
    def trigger_cover_stop(self) -> None:
        pass

    @abstractmethod
    def retrieve_cover_state(self) -> CoverState:
        pass

    @abstractmethod
    def add_cover_state_changed_callback(self, callback: CoverStateChangedCallback) -> None:
        pass

    @abstractmethod
    def remove_cover_state_changed_callback(self, callback: CoverStateChangedCallback) -> None:
        pass
