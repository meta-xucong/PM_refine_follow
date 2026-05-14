from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class SchemaValidationError(ValueError):
    pass


def load_schema(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        schema = json.load(f)
    if not isinstance(schema, dict):
        raise ValueError(f"Schema must be a JSON object: {path}")
    return schema


def validate_json(data: Any, schema: dict[str, Any]) -> None:
    try:
        import jsonschema  # type: ignore

        jsonschema.validate(instance=data, schema=schema)
        return
    except ModuleNotFoundError:
        pass
    except Exception as exc:
        raise SchemaValidationError(str(exc)) from exc
    _validate_fallback(data, schema, "$")


def _validate_fallback(data: Any, schema: dict[str, Any], path: str) -> None:
    if "enum" in schema and data not in schema["enum"]:
        raise SchemaValidationError(f"{path}: {data!r} not in enum")
    schema_type = schema.get("type")
    if schema_type is not None and not _type_matches(data, schema_type):
        raise SchemaValidationError(f"{path}: expected {schema_type}, got {type(data).__name__}")
    if isinstance(data, dict):
        required = schema.get("required") or []
        for key in required:
            if key not in data:
                raise SchemaValidationError(f"{path}: missing required key {key}")
        properties = schema.get("properties") or {}
        additional = schema.get("additionalProperties", True)
        for key, value in data.items():
            if key in properties:
                _validate_fallback(value, properties[key], f"{path}.{key}")
            elif additional is False:
                raise SchemaValidationError(f"{path}: unexpected key {key}")
    if isinstance(data, list):
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for idx, item in enumerate(data):
                _validate_fallback(item, item_schema, f"{path}[{idx}]")
    if isinstance(data, (int, float)) and not isinstance(data, bool):
        if "minimum" in schema and data < schema["minimum"]:
            raise SchemaValidationError(f"{path}: below minimum")
        if "maximum" in schema and data > schema["maximum"]:
            raise SchemaValidationError(f"{path}: above maximum")
    if isinstance(data, str):
        if "minLength" in schema and len(data) < schema["minLength"]:
            raise SchemaValidationError(f"{path}: shorter than minLength")
        if "pattern" in schema and not re.search(schema["pattern"], data):
            raise SchemaValidationError(f"{path}: pattern mismatch")


def _type_matches(data: Any, expected: Any) -> bool:
    if isinstance(expected, list):
        return any(_type_matches(data, item) for item in expected)
    if expected == "object":
        return isinstance(data, dict)
    if expected == "array":
        return isinstance(data, list)
    if expected == "string":
        return isinstance(data, str)
    if expected == "number":
        return isinstance(data, (int, float)) and not isinstance(data, bool)
    if expected == "integer":
        return isinstance(data, int) and not isinstance(data, bool)
    if expected == "boolean":
        return isinstance(data, bool)
    if expected == "null":
        return data is None
    return True

