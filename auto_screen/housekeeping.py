from __future__ import annotations

import re
import shutil
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .config import resolve_path


def _as_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _as_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _storage_cleanup_config(config: dict[str, Any]) -> dict[str, Any]:
    value = dict(config.get("storage_cleanup") or {})
    return {
        "enabled": _as_bool(value.get("enabled"), True),
        "min_free_gb": max(0.1, _as_float(value.get("min_free_gb"), 4.0)),
        "target_free_gb": max(0.1, _as_float(value.get("target_free_gb"), 8.0)),
        "archive_pattern": str(value.get("archive_pattern") or "^archive"),
        "archives_keep_latest": max(0, _as_int(value.get("archives_keep_latest"), 2)),
        "archives_max_age_days": max(0, _as_int(value.get("archives_max_age_days"), 10)),
        "accounts_keep_latest": max(0, _as_int(value.get("accounts_keep_latest"), 4000)),
        "accounts_max_age_days": max(0, _as_int(value.get("accounts_max_age_days"), 30)),
        "protect_pushed_accounts": _as_bool(value.get("protect_pushed_accounts"), True),
        "protected_sent_accounts_limit": max(0, _as_int(value.get("protected_sent_accounts_limit"), 5000)),
        "runs_retention_days": max(1, _as_int(value.get("runs_retention_days"), 60)),
        "alerts_retention_days": max(1, _as_int(value.get("alerts_retention_days"), 120)),
        "cycles_retention_days": max(1, _as_int(value.get("cycles_retention_days"), 60)),
        "keep_recent_runs": max(1000, _as_int(value.get("keep_recent_runs"), 500000)),
        "keep_recent_alerts": max(1000, _as_int(value.get("keep_recent_alerts"), 200000)),
        "log_max_mb": max(1, _as_int(value.get("log_max_mb"), 80)),
        "log_truncate_mb": max(1, _as_int(value.get("log_truncate_mb"), 20)),
        "log_paths": list(value.get("log_paths") or []),
        "progress_tmp_max_age_days": max(1, _as_int(value.get("progress_tmp_max_age_days"), 2)),
        "mid_cycle_check_every": max(1, _as_int(value.get("mid_cycle_check_every"), 50)),
        "emergency_archives_keep_latest": max(0, _as_int(value.get("emergency_archives_keep_latest"), 0)),
        "emergency_accounts_keep_latest": max(0, _as_int(value.get("emergency_accounts_keep_latest"), 1200)),
        "emergency_accounts_max_age_days": max(0, _as_int(value.get("emergency_accounts_max_age_days"), 10)),
        "emergency_runs_retention_days": max(1, _as_int(value.get("emergency_runs_retention_days"), 21)),
        "emergency_alerts_retention_days": max(1, _as_int(value.get("emergency_alerts_retention_days"), 45)),
        "emergency_log_truncate_mb": max(1, _as_int(value.get("emergency_log_truncate_mb"), 5)),
    }


def _utc_cutoff_iso(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


def _disk_usage_summary(anchor: Path) -> dict[str, float]:
    path = anchor if anchor.exists() else anchor.parent
    total, _used, free = shutil.disk_usage(path)
    return {
        "total_gb": round(total / (1024**3), 3),
        "free_gb": round(free / (1024**3), 3),
        "free_bytes": int(free),
    }


def _safe_rmtree(path: Path) -> bool:
    try:
        if path.exists():
            shutil.rmtree(path)
        return True
    except OSError:
        return False


def _safe_unlink(path: Path) -> bool:
    try:
        if path.exists():
            path.unlink()
        return True
    except OSError:
        return False


def _protected_addresses(state_db: Path, limit_sent: int) -> set[str]:
    if not state_db.exists():
        return set()
    conn = sqlite3.connect(state_db, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA busy_timeout=10000")
        sent_rows = conn.execute(
            """
            SELECT DISTINCT lower(address) AS address
            FROM alerts
            WHERE push_status IN ('sent', 'pending')
            ORDER BY COALESCE(pushed_at, created_at) DESC, id DESC
            LIMIT ?
            """,
            (limit_sent,),
        ).fetchall()
        active_rows = conn.execute(
            """
            SELECT DISTINCT lower(address) AS address
            FROM candidates
            WHERE status IN ('pending', 'refresh_score', 'defer_recheck')
            """
        ).fetchall()
    except sqlite3.Error:
        return set()
    finally:
        conn.close()
    addresses = {str(row["address"] or "").strip().lower() for row in sent_rows + active_rows}
    return {item for item in addresses if item}


def _cleanup_archives(parent_dir: Path, pattern: str, keep_latest: int, max_age_days: int) -> dict[str, Any]:
    if not parent_dir.exists():
        return {"removed": 0}
    try:
        regex = re.compile(pattern)
    except re.error:
        regex = re.compile("^archive")
    now = time.time()
    targets = [p for p in parent_dir.iterdir() if p.is_dir() and regex.search(p.name)]
    targets.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    removed = 0
    kept = 0
    for index, path in enumerate(targets):
        age_days = max(0.0, (now - path.stat().st_mtime) / 86400.0)
        should_keep = index < keep_latest and age_days < max_age_days
        if should_keep:
            kept += 1
            continue
        if _safe_rmtree(path):
            removed += 1
    return {"matched": len(targets), "kept": kept, "removed": removed}


def _cleanup_archives_multi(search_dirs: list[Path], pattern: str, keep_latest: int, max_age_days: int) -> dict[str, Any]:
    matched = 0
    kept = 0
    removed = 0
    checked_dirs: list[str] = []
    seen: set[str] = set()
    for directory in search_dirs:
        key = str(directory.resolve()) if directory.exists() else str(directory)
        if key in seen:
            continue
        seen.add(key)
        checked_dirs.append(str(directory))
        result = _cleanup_archives(directory, pattern, keep_latest, max_age_days)
        matched += int(result.get("matched") or 0)
        kept += int(result.get("kept") or 0)
        removed += int(result.get("removed") or 0)
    return {"checked_dirs": checked_dirs, "matched": matched, "kept": kept, "removed": removed}


def _cleanup_account_cache(
    accounts_dir: Path,
    keep_latest: int,
    max_age_days: int,
    protected_addresses: set[str],
) -> dict[str, Any]:
    if not accounts_dir.exists():
        return {"removed": 0}
    now = time.time()
    rows = [p for p in accounts_dir.iterdir() if p.is_dir()]
    rows.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    removed = 0
    skipped_protected = 0
    for index, path in enumerate(rows):
        address = path.name.lower()
        if address in protected_addresses:
            skipped_protected += 1
            continue
        age_days = max(0.0, (now - path.stat().st_mtime) / 86400.0)
        if index < keep_latest and age_days < max_age_days:
            continue
        if _safe_rmtree(path):
            removed += 1
    return {"matched": len(rows), "removed": removed, "skipped_protected": skipped_protected}


def _candidate_log_paths(data_dir: Path, configured_paths: list[Any]) -> list[Path]:
    paths: list[Path] = []
    for raw in configured_paths:
        item = Path(str(raw)).expanduser()
        paths.append(item if item.is_absolute() else data_dir.parent / item)
    default_paths = [
        data_dir / "dashboard" / "auto_screen.log",
        data_dir.parent / "dashboard_server.err.log",
        data_dir.parent / "auto_screen.log",
    ]
    for item in default_paths:
        if item not in paths:
            paths.append(item)
    deduped: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = str(path.resolve()) if path.exists() else str(path)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(path)
    return deduped


def _truncate_file_to_tail(path: Path, keep_bytes: int) -> bool:
    if not path.exists():
        return False
    try:
        size = path.stat().st_size
        if size <= keep_bytes:
            return False
        with path.open("rb") as f:
            f.seek(-keep_bytes, 2)
            tail = f.read()
        with path.open("wb") as f:
            f.write(tail)
        return True
    except OSError:
        return False


def _cleanup_logs(data_dir: Path, max_bytes: int, truncate_to_bytes: int, configured_paths: list[Any]) -> dict[str, Any]:
    touched = 0
    truncated = 0
    for path in _candidate_log_paths(data_dir, configured_paths):
        if not path.exists() or not path.is_file():
            continue
        touched += 1
        try:
            if path.stat().st_size > max_bytes and _truncate_file_to_tail(path, truncate_to_bytes):
                truncated += 1
        except OSError:
            continue
    return {"checked": touched, "truncated": truncated}


def _cleanup_progress_tmp(progress_path: Path, max_age_days: int) -> dict[str, Any]:
    parent = progress_path.parent
    if not parent.exists():
        return {"removed": 0}
    prefix = f"{progress_path.name}."
    cutoff_ts = time.time() - (max_age_days * 86400)
    removed = 0
    for path in parent.iterdir():
        if not path.is_file():
            continue
        if not path.name.startswith(prefix) or not path.name.endswith(".tmp"):
            continue
        try:
            if path.stat().st_mtime <= cutoff_ts and _safe_unlink(path):
                removed += 1
        except OSError:
            continue
    return {"removed": removed}


def _trim_table_to_recent(conn: sqlite3.Connection, table: str, keep_recent: int) -> int:
    keep_recent = max(1, keep_recent)
    row = conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()
    total = int(row["n"] if row else 0)
    if total <= keep_recent:
        return 0
    marker = conn.execute(
        f"""
        SELECT id
        FROM {table}
        ORDER BY id DESC
        LIMIT 1 OFFSET ?
        """,
        (keep_recent - 1,),
    ).fetchone()
    if not marker:
        return 0
    threshold = int(marker["id"])
    result = conn.execute(f"DELETE FROM {table} WHERE id < ?", (threshold,))
    return int(result.rowcount if result.rowcount is not None else 0)


def _trim_alerts_to_recent_non_pending(conn: sqlite3.Connection, keep_recent: int) -> int:
    keep_recent = max(1, keep_recent)
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM alerts WHERE push_status <> 'pending'"
    ).fetchone()
    total = int(row["n"] if row else 0)
    if total <= keep_recent:
        return 0
    marker = conn.execute(
        """
        SELECT id
        FROM alerts
        WHERE push_status <> 'pending'
        ORDER BY id DESC
        LIMIT 1 OFFSET ?
        """,
        (keep_recent - 1,),
    ).fetchone()
    if not marker:
        return 0
    threshold = int(marker["id"])
    result = conn.execute(
        """
        DELETE FROM alerts
        WHERE push_status <> 'pending'
          AND id < ?
        """,
        (threshold,),
    )
    return int(result.rowcount if result.rowcount is not None else 0)


def _cleanup_state_db(
    state_db: Path,
    runs_retention_days: int,
    alerts_retention_days: int,
    cycles_retention_days: int,
    keep_recent_runs: int,
    keep_recent_alerts: int,
) -> dict[str, Any]:
    if not state_db.exists():
        return {"skipped": True}
    conn = sqlite3.connect(state_db, timeout=20)
    conn.row_factory = sqlite3.Row
    removed_runs = 0
    removed_alerts = 0
    removed_cycles = 0
    trimmed_runs = 0
    trimmed_alerts = 0
    vacuumed = False
    try:
        conn.execute("PRAGMA busy_timeout=20000")
        runs_cutoff = _utc_cutoff_iso(runs_retention_days)
        alerts_cutoff = _utc_cutoff_iso(alerts_retention_days)
        cycles_cutoff = _utc_cutoff_iso(cycles_retention_days)

        removed_runs_res = conn.execute("DELETE FROM runs WHERE created_at < ?", (runs_cutoff,))
        removed_runs = int(removed_runs_res.rowcount if removed_runs_res.rowcount is not None else 0)

        removed_alerts_res = conn.execute(
            """
            DELETE FROM alerts
            WHERE created_at < ?
              AND push_status IN ('sent', 'archived', 'superseded', 'disabled', 'dry_run')
            """,
            (alerts_cutoff,),
        )
        removed_alerts = int(removed_alerts_res.rowcount if removed_alerts_res.rowcount is not None else 0)

        removed_cycles_res = conn.execute(
            """
            DELETE FROM cycles
            WHERE started_at < ?
              AND status <> 'running'
            """,
            (cycles_cutoff,),
        )
        removed_cycles = int(removed_cycles_res.rowcount if removed_cycles_res.rowcount is not None else 0)

        trimmed_runs = _trim_table_to_recent(conn, "runs", keep_recent_runs)
        trimmed_alerts = _trim_alerts_to_recent_non_pending(conn, keep_recent_alerts)

        conn.commit()
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        vacuumed = any([removed_runs, removed_alerts, removed_cycles, trimmed_runs, trimmed_alerts])
        if vacuumed:
            conn.execute("VACUUM")
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        conn.close()
    return {
        "removed_runs": removed_runs,
        "removed_alerts": removed_alerts,
        "removed_cycles": removed_cycles,
        "trimmed_runs": trimmed_runs,
        "trimmed_alerts": trimmed_alerts,
        "vacuumed": vacuumed,
    }


def checkpoint_state_db(state_db: Path, timeout_seconds: float = 60.0) -> dict[str, Any]:
    if not state_db.exists():
        return {"skipped": True, "reason": "state_db_missing", "state_db": str(state_db)}
    wal_path = Path(f"{state_db}-wal")
    before_bytes = wal_path.stat().st_size if wal_path.exists() else 0
    conn = sqlite3.connect(state_db, timeout=max(1.0, float(timeout_seconds)))
    try:
        conn.execute(f"PRAGMA busy_timeout={int(max(1.0, float(timeout_seconds)) * 1000)}")
        row = conn.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
    finally:
        conn.close()
    after_bytes = wal_path.stat().st_size if wal_path.exists() else 0
    return {
        "state_db": str(state_db),
        "wal_before_bytes": before_bytes,
        "wal_after_bytes": after_bytes,
        "freed_bytes": max(0, before_bytes - after_bytes),
        "checkpoint": list(row) if row is not None else None,
    }


def perform_storage_cleanup(
    config: dict[str, Any],
    *,
    reason: str = "manual",
    include_sqlite: bool = True,
) -> dict[str, Any]:
    cfg = _storage_cleanup_config(config)
    data_dir = resolve_path(config, "data_dir")
    state_db = resolve_path(config, "state_db")
    progress_path = resolve_path(config, "progress_path")
    anchor = data_dir if data_dir.exists() else state_db.parent
    summary: dict[str, Any] = {
        "enabled": cfg["enabled"],
        "reason": reason,
        "include_sqlite": bool(include_sqlite),
        "actions": {},
        "errors": [],
        "emergency_triggered": False,
    }
    if not cfg["enabled"]:
        summary["disk"] = _disk_usage_summary(anchor)
        return summary

    before = _disk_usage_summary(anchor)
    protected_addresses = (
        _protected_addresses(state_db, cfg["protected_sent_accounts_limit"])
        if cfg["protect_pushed_accounts"]
        else set()
    )
    try:
        summary["actions"]["archives"] = _cleanup_archives_multi(
            [data_dir, data_dir.parent],
            cfg["archive_pattern"],
            cfg["archives_keep_latest"],
            cfg["archives_max_age_days"],
        )
        summary["actions"]["accounts"] = _cleanup_account_cache(
            data_dir / "accounts",
            cfg["accounts_keep_latest"],
            cfg["accounts_max_age_days"],
            protected_addresses,
        )
        summary["actions"]["progress_tmp"] = _cleanup_progress_tmp(progress_path, cfg["progress_tmp_max_age_days"])
        summary["actions"]["logs"] = _cleanup_logs(
            data_dir,
            cfg["log_max_mb"] * 1024 * 1024,
            cfg["log_truncate_mb"] * 1024 * 1024,
            cfg["log_paths"],
        )
        if include_sqlite:
            summary["actions"]["state_db"] = _cleanup_state_db(
                state_db,
                cfg["runs_retention_days"],
                cfg["alerts_retention_days"],
                cfg["cycles_retention_days"],
                cfg["keep_recent_runs"],
                cfg["keep_recent_alerts"],
            )
    except Exception as exc:
        summary["errors"].append(str(exc))

    middle = _disk_usage_summary(anchor)
    if middle["free_gb"] < cfg["min_free_gb"]:
        summary["emergency_triggered"] = True
        try:
            summary["actions"]["emergency_archives"] = _cleanup_archives_multi(
                [data_dir, data_dir.parent],
                cfg["archive_pattern"],
                cfg["emergency_archives_keep_latest"],
                max(0, cfg["archives_max_age_days"]),
            )
            summary["actions"]["emergency_accounts"] = _cleanup_account_cache(
                data_dir / "accounts",
                cfg["emergency_accounts_keep_latest"],
                cfg["emergency_accounts_max_age_days"],
                protected_addresses,
            )
            summary["actions"]["emergency_logs"] = _cleanup_logs(
                data_dir,
                cfg["log_max_mb"] * 1024 * 1024,
                cfg["emergency_log_truncate_mb"] * 1024 * 1024,
                cfg["log_paths"],
            )
            if include_sqlite:
                summary["actions"]["emergency_state_db"] = _cleanup_state_db(
                    state_db,
                    cfg["emergency_runs_retention_days"],
                    cfg["emergency_alerts_retention_days"],
                    cfg["cycles_retention_days"],
                    max(1000, cfg["keep_recent_runs"] // 2),
                    max(1000, cfg["keep_recent_alerts"] // 2),
                )
        except Exception as exc:
            summary["errors"].append(str(exc))

    after = _disk_usage_summary(anchor)
    summary["disk_before"] = before
    summary["disk_after"] = after
    summary["freed_gb"] = round(after["free_gb"] - before["free_gb"], 3)
    summary["below_target"] = after["free_gb"] < cfg["target_free_gb"]
    summary["protected_addresses"] = len(protected_addresses)
    return summary
