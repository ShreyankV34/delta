"""YAML config loader with a small fallback parser for checked-in configs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from delta_os.infrastructure.config.schema_validation import validate_config_shape


class YamlConfigLoader:
    """Load YAML config using PyYAML when available."""

    def load(self, path: Path) -> dict[str, Any]:
        """Load a YAML file."""

        text = path.read_text(encoding="utf-8")
        try:
            import yaml  # type: ignore[import-untyped]
        except ModuleNotFoundError:
            return validate_config_shape(path, _parse_simple_yaml(text))
        loaded = yaml.safe_load(text) or {}
        if not isinstance(loaded, dict):
            raise ValueError("Top-level YAML config must be a mapping")
        return validate_config_shape(path, loaded)


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    lines = [
        (len(raw) - len(raw.lstrip(" ")), raw.strip())
        for raw in text.splitlines()
        if raw.strip() and not raw.strip().startswith("#")
    ]
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]

    for index, (indent, content) in enumerate(lines):
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if content.startswith("- "):
            if not isinstance(parent, list):
                raise ValueError("List item found outside a YAML list")
            parent.append(_parse_scalar(content[2:].strip()))
            continue

        key, separator, raw_value = content.partition(":")
        if not separator:
            raise ValueError(f"Unsupported YAML line: {content}")
        key = key.strip()
        raw_value = raw_value.strip()
        if raw_value:
            parent[key] = _parse_scalar(raw_value)
            continue

        next_is_list = False
        if index + 1 < len(lines):
            next_indent, next_content = lines[index + 1]
            next_is_list = next_indent > indent and next_content.startswith("- ")
        container: Any = [] if next_is_list else {}
        parent[key] = container
        stack.append((indent, container))

    return root


def _parse_scalar(value: str) -> Any:
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(item.strip()) for item in inner.split(",")]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "null":
        return None
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value.strip('"').strip("'")
