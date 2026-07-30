from dataclasses import dataclass, field

from .base_config import BaseConfig
from .parts.controller_config import ControllerConfig
from .parts.hardware_config import HardwareConfig
from .parts.http_config import HttpConfig
from .parts.log_config import LogConfig
from .parts.mqtt_config import MqttConfig
from .parts.persistence_config import PersistenceConfig


@dataclass
class ConfigData(BaseConfig):
    log: LogConfig = field(default_factory=LogConfig)
    http: HttpConfig = field(default_factory=HttpConfig)
    mqtt: MqttConfig = field(default_factory=MqttConfig)
    controller: ControllerConfig = field(default_factory=ControllerConfig)
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    persistence: PersistenceConfig = field(default_factory=PersistenceConfig)
