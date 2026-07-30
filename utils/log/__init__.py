from __future__ import annotations

from logging import DEBUG, ERROR, FATAL, INFO, NOTSET, WARNING, Formatter, LogRecord, StreamHandler, getLogger
from sys import stdout
from typing import TYPE_CHECKING, Literal

from utils.caller_name import get_caller_module_name

from .exclude_modules_filter import ExcludeModulesFilter
from .in_memory_handler import InMemoryHandler, LogEmittedCallback

if TYPE_CHECKING:
    from config import ConfigData, ConfigManager, LogConfig

LogLevel = Literal["debug", "info", "warning", "error", "fatal"]

_LEVELS: dict[LogLevel, int] = {
    "debug": DEBUG,
    "info": INFO,
    "warning": WARNING,
    "error": ERROR,
    "fatal": FATAL,
}

# setup early logging
_EARLY_IN_MEMORY_HANDLER = InMemoryHandler()
getLogger().addHandler(_EARLY_IN_MEMORY_HANDLER)
getLogger().setLevel(NOTSET)


_EXCLUDE_FILTER = ExcludeModulesFilter()
_FORMATTER = Formatter(
    fmt="%(asctime)s | %(levelname)s | %(name)s => %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_IN_MEMORY_HANDLER = InMemoryHandler()
_IN_MEMORY_HANDLER.addFilter(_EXCLUDE_FILTER)
_IN_MEMORY_HANDLER.setFormatter(_FORMATTER)

_CONSOLE_HANDLER = StreamHandler(stdout)
_CONSOLE_HANDLER.addFilter(_EXCLUDE_FILTER)
_CONSOLE_HANDLER.setFormatter(_FORMATTER)


def setup_log(config_manager: ConfigManager) -> None:
    _apply_log_config(config_manager.config.log)

    logger = getLogger()

    logger.addHandler(_IN_MEMORY_HANDLER)
    logger.addHandler(_CONSOLE_HANDLER)

    logger.removeHandler(_EARLY_IN_MEMORY_HANDLER)

    for record in _EARLY_IN_MEMORY_HANDLER.records:
        logger.handle(record)

    config_manager.add_config_changed_callback(_config_changed)


def log(level: LogLevel, msg: str, *args, **kwargs) -> None:
    if "stacklevel" not in kwargs:
        kwargs["stacklevel"] = 2

    logger = getLogger(get_caller_module_name())
    logger.log(_LEVELS[level], msg, *args, **kwargs)


def get_log_records() -> list[LogRecord]:
    return _IN_MEMORY_HANDLER.records


def get_log_lines() -> list[str]:
    return _IN_MEMORY_HANDLER.lines


def add_log_emitted_callback(callback: LogEmittedCallback):
    _IN_MEMORY_HANDLER.add_log_emitted_callback(callback)


def remove_log_emitted_callback(callback: LogEmittedCallback):
    _IN_MEMORY_HANDLER.remove_log_emitted_callback(callback)


def _config_changed(old_config: ConfigData, new_config: ConfigData) -> None:
    if old_config.log == new_config.log:
        return

    _apply_log_config(new_config.log)


def _apply_log_config(config: LogConfig) -> None:
    if config.enable:
        _IN_MEMORY_HANDLER.setLevel(_LEVELS[config.min_level])
        _CONSOLE_HANDLER.setLevel(_LEVELS[config.min_level])
    else:
        _IN_MEMORY_HANDLER.setLevel(FATAL + 1)
        _CONSOLE_HANDLER.setLevel(FATAL + 1)

    _EXCLUDE_FILTER.excludes = config.excluded_modules
    _IN_MEMORY_HANDLER.size = config.max_records_in_memory


__all__ = [
    "setup_log",
    "log",
    "get_log_records",
    "get_log_lines",
    "add_log_emitted_callback",
    "remove_log_emitted_callback",
]
