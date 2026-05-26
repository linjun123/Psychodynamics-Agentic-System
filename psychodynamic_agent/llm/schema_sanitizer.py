from __future__ import annotations

from copy import deepcopy
from typing import Any


def sanitize_schema_for_openai(schema: dict[str, Any]) -> dict[str, Any]:
    """Return a deep-copied schema without any $ref sibling keywords."""

    def _sanitize(value: Any) -> Any:
        if isinstance(value, dict):
            if "$ref" in value:
                return {"$ref": value["$ref"]}
            return {key: _sanitize(child) for key, child in value.items()}
        if isinstance(value, list):
            return [_sanitize(item) for item in value]
        return value

    return _sanitize(deepcopy(schema))


def assert_no_ref_siblings(schema: dict[str, Any]) -> None:
    """Raise ValueError when a schema node has $ref with sibling keywords."""

    def _walk(value: Any, path: tuple[Any, ...]) -> None:
        if isinstance(value, dict):
            if "$ref" in value and set(value.keys()) != {"$ref"}:
                raise ValueError(
                    f"$ref node has sibling keywords at path {path}: {sorted(value.keys())}"
                )
            for key, child in value.items():
                _walk(child, (*path, key))
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                _walk(item, (*path, idx))

    _walk(schema, ())
