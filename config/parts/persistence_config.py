from dataclasses import dataclass, field
from typing import Literal

from ..base_config import BaseConfig


@dataclass
class MockPersistenceTargetConfig(BaseConfig):
    implementation: Literal["mock_persistence_target"] = "mock_persistence_target"


@dataclass
class FilePersistenceTargetConfig(BaseConfig):
    implementation: Literal["file_persistence_target"] = "file_persistence_target"

    file_path: str = ""


type PersistenceTargetConfig = MockPersistenceTargetConfig | FilePersistenceTargetConfig


@dataclass
class MockCoverStatePersistenceConfig(MockPersistenceTargetConfig):
    pass


@dataclass
class FileCoverStatePersistenceConfig(FilePersistenceTargetConfig):
    file_path: str = "pypoolpi.state"


type CoverStatePersistenceConfig = MockCoverStatePersistenceConfig | FileCoverStatePersistenceConfig


@dataclass
class PersistenceConfig(BaseConfig):
    cover_state: CoverStatePersistenceConfig = field(default_factory=MockCoverStatePersistenceConfig)
