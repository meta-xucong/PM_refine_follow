from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .json_schema import load_schema, validate_json
from .memory_store import AgentMemoryStore


def normalize_feedback_event(raw: dict[str, Any], default_source: str = "json") -> dict[str, Any]:
    return {
        "account_address": str(raw.get("account_address") or raw.get("address") or "").lower(),
        "feedback_type": str(raw.get("feedback_type") or raw.get("feedback") or "neutral"),
        "note": raw.get("note"),
        "source": str(raw.get("source") or default_source),
        "source_ref": raw.get("source_ref"),
        "created_at": raw.get("created_at"),
    }


def import_feedback_events(
    events: list[dict[str, Any]],
    *,
    schema_path: str | Path,
    memory_store: AgentMemoryStore,
    default_source: str = "json",
) -> dict[str, Any]:
    schema = load_schema(schema_path)
    imported = 0
    errors: list[str] = []
    for idx, raw in enumerate(events):
        event = normalize_feedback_event(raw, default_source=default_source)
        try:
            validate_json(event, schema)
            memory_store.add_feedback(event)
            imported += 1
        except Exception as exc:
            errors.append(f"row {idx}: {exc}")
    return {"imported": imported, "ignored": len(events) - imported, "errors": errors}


def load_feedback_file(path: str | Path) -> list[dict[str, Any]]:
    p = Path(path)
    if p.suffix.lower() == ".json":
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = data.get("feedback") or data.get("events") or [data]
        if not isinstance(data, list):
            raise ValueError("Feedback JSON must be an object or list")
        return [x for x in data if isinstance(x, dict)]
    if p.suffix.lower() == ".csv":
        with p.open("r", encoding="utf-8-sig", newline="") as f:
            return [dict(row) for row in csv.DictReader(f)]
    raise ValueError(f"Unsupported feedback file: {p}")


def import_feedback_file(
    path: str | Path,
    *,
    schema_path: str | Path,
    memory_store: AgentMemoryStore,
    default_source: str = "json",
) -> dict[str, Any]:
    return import_feedback_events(
        load_feedback_file(path),
        schema_path=schema_path,
        memory_store=memory_store,
        default_source=default_source,
    )

