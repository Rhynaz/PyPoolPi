from dataclasses import dataclass, field

from ..base_config import BaseConfig


@dataclass
class EndDetectionConfig(BaseConfig):
    enable: bool = False

    opening_overrun_duration: float = 0.5  # seconds
    closing_overrun_duration: float = 2.5  # seconds


@dataclass
class SafetyTimeoutConfig(BaseConfig):
    enable: bool = False

    max_opening_duration: float = 85  # seconds
    max_closing_duration: float = 85  # seconds


@dataclass
class DiveSequenceConfig(BaseConfig):
    enable: bool = False

    use_sensor: bool = False
    activation_delay: float = 1.5  # seconds

    hanging_duration: float = 2  # seconds
    diving_duration: float = 3  # seconds
    surfacing_duration: float = 4  # seconds


@dataclass
class ControllerConfig(BaseConfig):
    end_detection: EndDetectionConfig = field(default_factory=EndDetectionConfig)
    safety_timeout: SafetyTimeoutConfig = field(default_factory=SafetyTimeoutConfig)
    dive_sequence: DiveSequenceConfig = field(default_factory=DiveSequenceConfig)
