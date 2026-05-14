from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AccountCandidate:
    address: str
    display_name: str = ""
    best_rank: int | None = None
    discovery_score: float = 0.0
    source_keys: list[str] = field(default_factory=list)
    leaderboard_context: dict[str, Any] = field(default_factory=dict)
    raw_rows: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class PrefilterResult:
    address: str
    passed: bool
    reason: str
    trade_count: int = 0
    active_days: float = 0.0
    avg_trades_per_day: float = 0.0
    flags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ScoringResult:
    address: str
    final_score: float
    decision: str
    alert_grade: str
    auto_action: str
    analysis_path: str
    report_zh_path: str | None = None
    report_en_path: str | None = None
    score_flags: list[str] = field(default_factory=list)
    payload: dict[str, Any] = field(default_factory=dict)
