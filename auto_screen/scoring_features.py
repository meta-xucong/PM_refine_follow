from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import AccountCandidate, PrefilterResult


def build_leaderboard_context(candidate: AccountCandidate, prefilter: PrefilterResult | None = None) -> dict[str, Any]:
    context = dict(candidate.leaderboard_context)
    context["discovery_score"] = candidate.discovery_score
    context["source_keys"] = candidate.source_keys
    context["best_rank"] = candidate.best_rank
    context["display_name"] = candidate.display_name
    if prefilter is not None:
        context["prefilter"] = {
            "passed": prefilter.passed,
            "reason": prefilter.reason,
            "trade_count": prefilter.trade_count,
            "active_days": prefilter.active_days,
            "avg_trades_per_day": prefilter.avg_trades_per_day,
            "flags": prefilter.flags,
        }
    return context


def write_leaderboard_context(path: str | Path, candidate: AccountCandidate, prefilter: PrefilterResult | None = None) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build_leaderboard_context(candidate, prefilter), ensure_ascii=False, indent=2), encoding="utf-8")
    return out
