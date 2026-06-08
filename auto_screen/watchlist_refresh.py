from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .collector import CollectionSkipped, collect_account_files
from .config import resolve_path
from .models import AccountCandidate
from .notifier import send_serverchan
from .scorer import score_account
from .scoring_features import write_leaderboard_context
from .state_store import StateStore, utc_now


HARD_CAP_FLAGS = {
    "dual_side_material_50",
    "dual_side_high_45",
    "dual_side_severe_39",
    "copy_capacity_low_48",
    "extreme_price_structured_45",
    "hard_extreme_price_structure_50",
    "recent_7d_loss_heavy_48",
    "recent_pnl_negative_45",
}


@dataclass(slots=True)
class WatchlistCandidate:
    address: str
    label: str = ""
    old_score: float | None = None
    source_reason: str = ""
    priority: int = 0


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _json_loads(value: Any, default: Any) -> Any:
    if value in (None, ""):
        return default
    try:
        return json.loads(str(value))
    except json.JSONDecodeError:
        return default


def _label_from_payload(payload_text: Any, fallback: str) -> str:
    payload = _json_loads(payload_text, {})
    if isinstance(payload, dict):
        return str(payload.get("account_label") or payload.get("label") or fallback)
    return fallback


def _iso_cutoff(hours: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=max(0.0, hours))).isoformat()


def _parse_datetime(value: Any) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _last_refresh_by_address(store: StateStore) -> dict[str, dict[str, Any]]:
    rows = store.conn.execute(
        """
        SELECT address, fresh_score, recommendation, created_at
        FROM watchlist_refresh_runs
        WHERE error IS NULL
        ORDER BY created_at DESC, id DESC
        """
    ).fetchall()
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        address = str(row["address"] or "").lower()
        if address and address not in out:
            out[address] = dict(row)
    return out


def _latest_rows_by_address(rows: list[Any]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        item = dict(row)
        address = str(item.get("address") or "").lower()
        if address and address not in latest:
            latest[address] = item
    return latest


def select_watchlist_candidates(
    store: StateStore,
    *,
    min_score: float = 60.0,
    limit: int = 200,
    refresh_interval_hours: float = 48.0,
    include_recent: bool = False,
) -> tuple[list[WatchlistCandidate], list[dict[str, Any]]]:
    candidates: dict[str, WatchlistCandidate] = {}

    def add(address: str, label: str, score: float | None, reason: str, priority: int) -> None:
        address = str(address or "").lower()
        if not address:
            return
        existing = candidates.get(address)
        if existing is None or priority > existing.priority or (
            priority == existing.priority and (score or 0.0) > (existing.old_score or 0.0)
        ):
            candidates[address] = WatchlistCandidate(
                address=address,
                label=label or address,
                old_score=score,
                source_reason=reason,
                priority=priority,
            )

    run_rows = store.conn.execute(
        """
        SELECT address, final_score, payload, created_at
        FROM runs
        WHERE status='scored'
        ORDER BY created_at DESC, id DESC
        """
    ).fetchall()
    latest_run_by_address = _latest_rows_by_address(run_rows)
    for row in latest_run_by_address.values():
        score = _to_float(row["final_score"])
        if score is None or score < min_score:
            continue
        label = _label_from_payload(row["payload"], str(row["address"] or ""))
        add(row["address"], label, score, f"latest_score>={min_score:g}", 80)

    alert_rows = store.conn.execute(
        """
        SELECT address, final_score, alert_grade, title, created_at, pushed_at
        FROM alerts
        WHERE push_status='sent'
        ORDER BY COALESCE(pushed_at, created_at) DESC, id DESC
        """
    ).fetchall()
    for row in _latest_rows_by_address(alert_rows).values():
        address = str(row["address"] or "").lower()
        if address in latest_run_by_address:
            continue
        score = _to_float(row["final_score"])
        if score is None or score < min_score:
            continue
        title = str(row["title"] or "")
        label = title.split("｜")[-1].strip() if "｜" in title else str(row["address"] or "")
        add(row["address"], label, score, f"latest_pushed_score>={min_score:g}", 90)

    manual_rows = store.conn.execute(
        """
        SELECT address, label, note
        FROM watchlist_manual_accounts
        WHERE enabled=1
        ORDER BY updated_at DESC
        """
    ).fetchall()
    for row in manual_rows:
        address = str(row["address"] or "").lower()
        if address not in candidates:
            latest_run = latest_run_by_address.get(address)
            score = _to_float(latest_run["final_score"]) if latest_run is not None else None
            if score is None or score < min_score:
                continue
            add(address, str(row["label"] or address), score, f"manual_latest_score>={min_score:g}", 100)
            continue
        existing = candidates[address]
        label = str(row["label"] or existing.label or address)
        add(address, label, existing.old_score, f"manual_{existing.source_reason}", 100)

    last_refresh = _last_refresh_by_address(store)
    cutoff = _parse_datetime(_iso_cutoff(refresh_interval_hours))
    selected: list[WatchlistCandidate] = []
    skipped_recent: list[dict[str, Any]] = []
    for candidate in sorted(candidates.values(), key=lambda x: (x.priority, x.old_score or 0.0), reverse=True):
        latest = last_refresh.get(candidate.address)
        if latest and not include_recent:
            created_at = _parse_datetime(latest["created_at"])
            if created_at > cutoff:
                skipped_recent.append(
                    {
                        "address": candidate.address,
                        "label": candidate.label,
                        "source_reason": candidate.source_reason,
                        "old_score": candidate.old_score,
                        "last_refresh_at": latest["created_at"],
                        "last_fresh_score": latest["fresh_score"],
                        "last_recommendation": latest["recommendation"],
                    }
                )
                continue
        selected.append(candidate)
        if len(selected) >= limit:
            break
    return selected, skipped_recent


def recommendation_for_result(fresh_score: float | None, flags: list[str], caps: list[str]) -> str:
    score = fresh_score if fresh_score is not None else 0.0
    flag_set = set(flags) | set(caps)
    if flag_set & HARD_CAP_FLAGS or score < 55:
        return "remove_candidate"
    if score < 60:
        return "downgrade"
    if score < 65:
        return "watch"
    return "stable"


def _batch_summary(rows: list[dict[str, Any]], skipped_recent: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {
        "total": len(rows) + len(skipped_recent),
        "attempted": len(rows),
        "succeeded": sum(1 for row in rows if not row.get("error")),
        "failed": sum(1 for row in rows if row.get("error")),
        "skipped_recent": len(skipped_recent),
        "stable_count": sum(1 for row in rows if row.get("recommendation") == "stable"),
        "watch_count": sum(1 for row in rows if row.get("recommendation") == "watch"),
        "downgrade_count": sum(1 for row in rows if row.get("recommendation") == "downgrade"),
        "remove_count": sum(1 for row in rows if row.get("recommendation") == "remove_candidate"),
    }
    summary["hard_cap_count"] = sum(
        1
        for row in rows
        if set(row.get("score_flags") or []) & HARD_CAP_FLAGS or set(row.get("applied_caps") or []) & HARD_CAP_FLAGS
    )
    return summary


def format_watchlist_refresh_message(summary: dict[str, Any], rows: list[dict[str, Any]]) -> tuple[str, str]:
    title = (
        f"高分复核完成：{summary.get('succeeded', 0)} 成功｜"
        f"稳定 {summary.get('stable_count', 0)}｜降级 {summary.get('downgrade_count', 0) + summary.get('remove_count', 0)}"
    )
    stable = [row for row in rows if row.get("recommendation") == "stable"]
    watch = [row for row in rows if row.get("recommendation") == "watch"]
    downgraded = [row for row in rows if row.get("recommendation") in {"downgrade", "remove_candidate"}]
    failed = [row for row in rows if row.get("error")]

    def line(row: dict[str, Any]) -> str:
        delta = row.get("score_delta")
        delta_text = "暂无旧分" if delta is None else f"{delta:+.2f}"
        flags = ", ".join((row.get("score_flags") or [])[:3])
        return (
            f"- {row.get('label') or row.get('address')} `{row.get('address')}`："
            f"{row.get('old_score') if row.get('old_score') is not None else '-'} -> {row.get('fresh_score')} "
            f"({delta_text})"
            + (f"，{flags}" if flags else "")
        )

    lines = [
        "## 高分复核结果",
        f"- 本次候选：{summary.get('total', 0)}",
        f"- 实际复核：{summary.get('attempted', 0)}",
        f"- 48 小时内已复核跳过：{summary.get('skipped_recent', 0)}",
        f"- 成功 / 失败：{summary.get('succeeded', 0)} / {summary.get('failed', 0)}",
        f"- 稳定 / 观察 / 降级 / 移出：{summary.get('stable_count', 0)} / {summary.get('watch_count', 0)} / {summary.get('downgrade_count', 0)} / {summary.get('remove_count', 0)}",
        f"- hard cap 数量：{summary.get('hard_cap_count', 0)}",
        "",
        "## 稳定候选",
    ]
    lines.extend(line(row) for row in stable[:10])
    if not stable:
        lines.append("- 暂无")
    lines.extend(["", "## 观察候选"])
    lines.extend(line(row) for row in watch[:10])
    if not watch:
        lines.append("- 暂无")
    lines.extend(["", "## 降级/移出"])
    lines.extend(line(row) for row in downgraded[:12])
    if not downgraded:
        lines.append("- 暂无")
    if failed:
        lines.extend(["", "## 失败账号"])
        lines.extend(f"- `{row.get('address')}`：{row.get('error')}" for row in failed[:8])
    lines.extend(["", "完整结果已写入 dashboard 的高分复核板块和 latest_summary.csv。"])
    return title, "\n".join(lines)


def write_refresh_outputs(config: dict[str, Any], rows: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, str]:
    data_dir = resolve_path(config, "data_dir")
    out_dir = data_dir / "watchlist_refresh"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "latest_summary.json"
    csv_path = out_dir / "latest_summary.csv"
    payload = {"summary": summary, "rows": rows, "generated_at": utc_now()}
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    fieldnames = [
        "address",
        "label",
        "source_reason",
        "old_score",
        "fresh_score",
        "score_delta",
        "fresh_grade",
        "decision",
        "auto_action",
        "recommendation",
        "score_flags",
        "applied_caps",
        "analysis_path",
        "error",
        "created_at",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["score_flags"] = ",".join(row.get("score_flags") or [])
            out["applied_caps"] = ",".join(row.get("applied_caps") or [])
            writer.writerow(out)
    return {"json_path": str(json_path), "csv_path": str(csv_path)}


def run_watchlist_refresh(
    config: dict[str, Any],
    *,
    min_score: float = 60.0,
    limit: int = 200,
    refresh_interval_hours: float = 48.0,
    include_recent: bool = False,
    dry_run_serverchan: bool = False,
) -> dict[str, Any]:
    store = StateStore(resolve_path(config, "state_db"))
    batch_id = store.start_watchlist_refresh_batch()
    rows: list[dict[str, Any]] = []
    skipped_recent: list[dict[str, Any]] = []
    try:
        candidates, skipped_recent = select_watchlist_candidates(
            store,
            min_score=min_score,
            limit=limit,
            refresh_interval_hours=refresh_interval_hours,
            include_recent=include_recent,
        )
        data_dir = resolve_path(config, "data_dir")
        for candidate in candidates:
            created_at = utc_now()
            account_dir = data_dir / "watchlist_refresh" / "accounts" / candidate.address
            context_candidate = AccountCandidate(
                address=candidate.address,
                display_name=candidate.label,
                discovery_score=0.0,
                source_keys=["watchlist_refresh"],
                leaderboard_context={
                    "source_keys": ["watchlist_refresh"],
                    "watchlist_refresh": True,
                    "source_reason": candidate.source_reason,
                    "previous_score": candidate.old_score,
                },
            )
            context_path = write_leaderboard_context(
                account_dir / "leaderboard_context.json",
                context_candidate,
                None,
            )
            row: dict[str, Any] = {
                "batch_id": batch_id,
                "address": candidate.address,
                "label": candidate.label,
                "source_reason": candidate.source_reason,
                "old_score": candidate.old_score,
                "created_at": created_at,
            }
            try:
                csv_path, summary_path = collect_account_files(candidate.address, candidate.label, config, data_dir / "watchlist_refresh")
                result = score_account(candidate.address, csv_path, summary_path, context_path, account_dir, config)
                breakdown = result.payload.get("score_breakdown_v3") or result.payload.get("score_breakdown") or {}
                caps = list(breakdown.get("applied_final_caps") or [])
                fresh_score = float(result.final_score)
                score_delta = None if candidate.old_score is None else round(fresh_score - float(candidate.old_score), 2)
                row.update(
                    {
                        "fresh_score": fresh_score,
                        "score_delta": score_delta,
                        "fresh_grade": result.alert_grade,
                        "decision": result.decision,
                        "auto_action": result.auto_action,
                        "score_flags": result.score_flags,
                        "applied_caps": caps,
                        "analysis_path": result.analysis_path,
                    }
                )
                row["recommendation"] = recommendation_for_result(fresh_score, result.score_flags, caps)
            except CollectionSkipped as exc:
                row.update({"error": str(exc), "recommendation": "remove_candidate", "score_flags": ["collection_skipped"], "applied_caps": []})
            except Exception as exc:  # pragma: no cover - exact network failures vary
                row.update({"error": str(exc), "recommendation": "error", "score_flags": ["refresh_error"], "applied_caps": []})
            store.record_watchlist_refresh_run(row)
            rows.append(row)
            time.sleep(0.05)

        summary = _batch_summary(rows, skipped_recent)
        output_paths = write_refresh_outputs(config, rows, summary)
        summary.update(output_paths)
        title, message = format_watchlist_refresh_message(summary, rows)
        serverchan_cfg = dict(config.get("serverchan") or {})
        if dry_run_serverchan:
            serverchan_cfg["dry_run"] = True
        push_result = send_serverchan(title, message, serverchan_cfg)
        status = "done" if not any(row.get("error") for row in rows) else "partial"
        store.finish_watchlist_refresh_batch(batch_id, status, summary, push_result)
        return {"batch_id": batch_id, "summary": summary, "rows": rows, "skipped_recent": skipped_recent, "serverchan": push_result}
    except Exception as exc:
        summary = _batch_summary(rows, skipped_recent)
        summary["error"] = str(exc)
        store.finish_watchlist_refresh_batch(batch_id, "failed", summary, {"sent": False, "reason": "refresh_failed", "error": str(exc)})
        raise
    finally:
        store.close()
