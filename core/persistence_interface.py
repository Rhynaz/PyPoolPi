from abc import ABC, abstractmethod
from collections.abc import Callable

from core.controller_interface import CoverState

type Encoder[T] = Callable[[T], str]
type Decoder[T] = Callable[[str], T]


class CoverStatePersistence(ABC):
    @abstractmethod
    def load_cover_state[S: CoverState](self, decode: Decoder[S]) -> S:
        pass

    @abstractmethod
    def store_cover_state[S: CoverState](self, encode: Encoder[S], state: S) -> None:
        pass
