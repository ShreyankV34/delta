"""Shared DTO serialization helpers."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Mapping


class SerializableDTO:
    """Mixin for DTOs that need deterministic dictionary output."""

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary."""

        value = _serialize(self)
        if not isinstance(value, dict):
            raise TypeError("DTO serialization must produce a dictionary")
        return value


def _serialize(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _serialize(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): _serialize(item) for key, item in value.items()}
    if isinstance(value, tuple | list):
        return [_serialize(item) for item in value]
    return value
