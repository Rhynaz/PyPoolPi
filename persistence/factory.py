from abc import ABC, abstractmethod

from config import PersistenceTargetConfig
from utils.log import log


class PersistenceTarget(ABC):
    @abstractmethod
    def load(self) -> str:
        pass

    @abstractmethod
    def store(self, data: str) -> None:
        pass

    @abstractmethod
    def deallocate(self) -> None:
        pass


def create_persistence_target(name: str, config: PersistenceTargetConfig) -> PersistenceTarget:
    log("info", f"Instantiating persistence target implementation: {config.implementation}")
    match config.implementation:
        case "file_persistence_target":
            from .targets.file_target import FilePersistenceTarget

            return FilePersistenceTarget(name, config)

        case "mock_persistence_target":
            pass

        case _:
            log(
                "error",
                f"Unknown persistence target implementation (falling back to mock): {config.implementation}",
            )

    from .targets.mock_target import MockPersistenceTarget

    return MockPersistenceTarget(name)
