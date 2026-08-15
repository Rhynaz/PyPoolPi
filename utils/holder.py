from __future__ import annotations

from collections.abc import Callable
from threading import Lock
from typing import Any, overload

type ValueChangedCallback[T] = Callable[[T, T], None]


class Holder[T]:
    def __init__(self, initial_value: T) -> None:
        self._value = initial_value
        self._callbacks = set[ValueChangedCallback[T]]()
        self._lock = Lock()

    def get(self) -> T:
        with self._lock:
            return self._value

    def set(self, new_value: T) -> None:
        with self._lock:
            old_value = self._value
            self._value = new_value

            if old_value == new_value:
                return

            callbacks = list(self._callbacks)

        for callback in callbacks:
            callback(old_value, new_value)

    def add_value_changed_callback(self, callback: ValueChangedCallback[T]) -> None:
        with self._lock:
            self._callbacks.add(callback)

    def remove_value_changed_callback(self, callback: ValueChangedCallback[T]) -> None:
        with self._lock:
            self._callbacks.discard(callback)

    def has_value_changed_callback(self, callback: ValueChangedCallback[T] | None = None) -> bool:
        with self._lock:
            return len(self._callbacks) > 0 and (True if callback is None else callback in self._callbacks)

    def deallocate(self) -> None:
        with self._lock:
            self._callbacks.clear()


class HolderProperty[T]:
    def __init__(self, initial_value: T) -> None:
        self._initial_value = initial_value
        self._name = f"_holder_{id(self)}"

    def __set_name__(self, owner: Any, name: str) -> None:
        self._name = f"_holder_{name}"

    @overload
    def __get__(self, instance: None, owner: Any) -> HolderProperty[T]: ...

    @overload
    def __get__(self, instance: object, owner: Any) -> T: ...

    def __get__(self, instance: Any, owner: Any) -> Any:
        if instance is None:
            return self

        if self._name not in instance.__dict__:
            instance.__dict__[self._name] = Holder(self._initial_value)

        return instance.__dict__[self._name].get()

    def __set__(self, instance: Any, value: T) -> None:
        if self._name not in instance.__dict__:
            instance.__dict__[self._name] = Holder(value)
        else:
            instance.__dict__[self._name].set(value)

    def __delete__(self, instance: Any) -> None:
        if self._name not in instance.__dict__:
            return

        instance.__dict__[self._name].deallocate()
        del instance.__dict__[self._name]

    @staticmethod
    def change_holder(instance: Any, property: HolderProperty[T], holder: Holder[T]) -> None:
        if property._name in instance.__dict__:
            instance.__dict__[property._name].deallocate()

        instance.__dict__[property._name] = holder

    @staticmethod
    def add_value_changed_callback(
        instance: Any,
        property: HolderProperty[T],
        callback: ValueChangedCallback[T],
    ) -> None:
        if property._name not in instance.__dict__:
            instance.__dict__[property._name] = Holder(property._initial_value)

        instance.__dict__[property._name].add_value_changed_callback(callback)

    @staticmethod
    def remove_value_changed_callback(
        instance: Any,
        property: HolderProperty[T],
        callback: ValueChangedCallback[T],
    ) -> None:
        if property._name not in instance.__dict__:
            instance.__dict__[property._name] = Holder(property._initial_value)

        instance.__dict__[property._name].remove_value_changed_callback(callback)

    @staticmethod
    def has_value_changed_callback(
        instance: Any,
        property: HolderProperty[T],
        callback: ValueChangedCallback[T] | None = None,
    ) -> bool:
        if property._name not in instance.__dict__:
            instance.__dict__[property._name] = Holder(property._initial_value)

        return instance.__dict__[property._name].has_value_changed_callback(callback)

    @staticmethod
    def deallocate(instance: Any, property: HolderProperty[T]) -> None:
        if property._name in instance.__dict__:
            instance.__dict__[property._name].deallocate()
