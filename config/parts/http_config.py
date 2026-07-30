from dataclasses import dataclass, field

from ..base_config import BaseConfig


@dataclass
class EventStreamConfig(BaseConfig):
    queue_size: int = 10
    keep_alive_interval: float = 30  # seconds


@dataclass
class HttpConfig(BaseConfig):
    enable: bool = True

    interface: str = "0.0.0.0"
    port: int = 5000

    thread_count: int = 4

    event_stream: EventStreamConfig = field(default_factory=EventStreamConfig)
