from dataclasses import dataclass, field

from utils.log import LogLevel

from ..base_config import BaseConfig


@dataclass
class LogConfig(BaseConfig):
    enable: bool = True

    min_level: LogLevel = "info"
    max_records_in_memory: int = 50

    excluded_modules: set[str] = field(default_factory=set[str])
    excluded_http_paths: set[str] = field(default_factory=set[str])
