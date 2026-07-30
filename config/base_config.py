from copy import deepcopy
from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from .manager import ConfigManager


@dataclass
class BaseConfig:
    def _bind(self, manager: "ConfigManager", path: list[str]) -> None:
        setattr(self, "__manager", manager)
        setattr(self, "__path", path)

        for field in fields(self):
            self.__bind_field(field.name, getattr(self, field.name))

    def _unbind(self) -> None:
        setattr(self, "__manager", None)
        setattr(self, "__path", [])

        for field in fields(self):
            self.__unbind_field(getattr(self, field.name))

    def __bind_field(self, name: str, value: Any) -> None:
        manager = getattr(self, "__manager", None)
        path = getattr(self, "__path", [])

        if manager is not None and isinstance(value, BaseConfig):
            value._bind(manager, [*path, name])

    def __unbind_field(self, value: Any) -> None:
        if isinstance(value, BaseConfig):
            value._unbind()

    def __setattr__(self, name: str, new_value: Any) -> None:
        if name.startswith("__"):
            object.__setattr__(self, name, new_value)
            return

        manager = getattr(self, "__manager", None)

        if manager is None:
            self.__unbind_field(getattr(self, name, None))
            object.__setattr__(self, name, new_value)
            self.__bind_field(name, getattr(self, name, None))
            return

        with manager.change_config() as config:
            for field in getattr(self, "__path", []):
                config = getattr(config, field)
            setattr(config, name, new_value)

    def __deepcopy__(self, memo) -> Self:
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result

        for field in fields(self):
            name = field.name
            setattr(result, name, deepcopy(getattr(self, name), memo))

        return result
