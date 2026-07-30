from dataclasses import dataclass, field
from typing import Literal

from ..base_config import BaseConfig


@dataclass
class MqttTopicConfig(BaseConfig):
    command: str = "pypoolpi/command"
    cover_state: str = "pypoolpi/state"
    log: str = "pypoolpi/log"


@dataclass
class MqttConfig(BaseConfig):
    enable: bool = False

    client_id: str = "pypoolpi"
    protocol_version: Literal["3.1", "3.1.1", "5.0"] = "5.0"

    host: str = "localhost"
    port: int = 1883
    username: str = ""
    password: str = ""

    topics: MqttTopicConfig = field(default_factory=MqttTopicConfig)
