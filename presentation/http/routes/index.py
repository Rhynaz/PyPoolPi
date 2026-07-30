from dataclasses import MISSING, fields, is_dataclass
from json import dumps
from types import UnionType
from typing import Any, Literal, TypeAliasType, Union, get_args, get_origin

from flask import Blueprint, render_template, url_for

from config import ConfigData

INDEX = Blueprint("index", __name__)


@INDEX.get("/")
def view_index():
    return render_template(
        "index.html",
        endpoint_map=dumps(_generate_endpoint_map()),
        config_schema=dumps(_generate_config_schema()),
    )


def _generate_endpoint_map() -> dict[str, Any]:
    return {
        endpoint[0]: {"url": url_for(endpoint[0]), "method": endpoint[1]}
        for endpoint in [
            ("command.send_open", "POST"),
            ("command.send_close", "POST"),
            ("command.send_stop", "POST"),
            ("status.view_status", "GET"),
            ("config.view_config", "GET"),
            ("config.change_config", "PUT"),
            ("log.view_log", "GET"),
            ("events.stream_events", "GET"),
        ]
    }


def _generate_config_schema(cls: type = ConfigData, path_prefix: str = "") -> list[dict[str, Any]]:
    schema = []

    for f in fields(cls):
        f_name = f.name if path_prefix == "" else f"{path_prefix}.{f.name}"
        f_type = _resolve_type_alias(f.type)

        if get_origin(f_type) in (Union, UnionType):
            variants = [_resolve_type_alias(var) for var in get_args(f_type)]

            schema.append(
                {
                    "name": f_name,
                    "properties": {var.__name__.rstrip("Config"): _get_properties(var) for var in variants},
                }
            )

            for var in variants:
                schema.extend(_generate_config_schema(var, f_name))

        elif isinstance(f_type, type) and is_dataclass(f_type):
            properties = _get_properties(f_type)
            if len(properties) > 0:
                schema.append({"name": f_name, "properties": properties})

            schema.extend(_generate_config_schema(f_type, f_name))

    return schema


_PRIMITIVES = {
    bool: "boolean",
    int: "integer",
    float: "float",
    str: "string",
}


def _get_properties(cls: type) -> list[dict[str, Any]]:
    properties = []

    for f in fields(cls):
        f_type = _resolve_type_alias(f.type)
        origin = get_origin(f_type)

        if is_dataclass(f_type) or origin in (Union, UnionType):
            continue

        if f.default is not MISSING:
            default = f.default
        elif f.default_factory is not MISSING:
            default = f.default_factory()
        else:
            default = None

        if origin is Literal:
            variants = get_args(f_type)
            if len(variants) == 1:
                properties.append({"name": f.name, "type": "constant", "default": default})
            else:
                properties.append({"name": f.name, "type": "enum", "default": default, "variants": list(variants)})

        elif origin in (list, set):
            items = get_args(f_type)
            properties.append(
                {
                    "name": f.name,
                    "type": "list",
                    "default": list(default) if default is not None else [],
                    "items": _PRIMITIVES.get(_resolve_type_alias(items[0]) if len(items) > 0 else Any, "unknown"),
                }
            )

        else:
            properties.append({"name": f.name, "type": _PRIMITIVES.get(f_type, "unknown"), "default": default})

    return properties


def _resolve_type_alias(t: Any) -> Any:
    while isinstance(t, TypeAliasType):
        t = t.__value__

    return t
