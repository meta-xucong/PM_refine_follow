from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import AccountCandidate, PrefilterResult, ScoringResult


PENDING_CANDIDATE_STATUSES = ("pending", "refresh_score")
REFRESH_SCORE_STATUS = "refresh_score"
REFRESH_SCORE_PROMPT = "刷新分数"
PREVIOUS_ROUND_STATUS = "previous_round"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class StateStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path, timeout=30)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA busy_timeout=30000")
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.init_schema()

    def close(self) -> None:
        self.conn.close()

    def init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS cycles (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              started_at TEXT NOT NULL,
              finished_at TEXT,
              status TEXT NOT NULL,
              note TEXT
            );
            CREATE TABLE IF NOT EXISTS candidates (
              address TEXT PRIMARY KEY,
              display_name TEXT,
              best_rank INTEGER,
              discovery_score REAL,
              source_keys TEXT,
              leaderboard_context TEXT,
              status TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS runs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              address TEXT NOT NULL,
              status TEXT NOT NULL,
              final_score REAL,
              decision TEXT,
              alert_grade TEXT,
              auto_action TEXT,
              reason TEXT,
              payload TEXT,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS alerts (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              address TEXT NOT NULL,
              final_score REAL,
              alert_grade TEXT,
              title TEXT,
              message TEXT,
              created_at TEXT NOT NULL,
              push_status TEXT NOT NULL DEFAULT 'pending',
              push_batch_id TEXT,
              pushed_at TEXT,
              push_result TEXT
            );
            CREATE TABLE IF NOT EXISTS watchlist_manual_accounts (
              address TEXT PRIMARY KEY,
              label TEXT,
              note TEXT,
              enabled INTEGER NOT NULL DEFAULT 1,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS watchlist_refresh_batches (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              started_at TEXT NOT NULL,
              finished_at TEXT,
              status TEXT NOT NULL,
              total INTEGER NOT NULL DEFAULT 0,
              succeeded INTEGER NOT NULL DEFAULT 0,
              failed INTEGER NOT NULL DEFAULT 0,
              skipped_recent INTEGER NOT NULL DEFAULT 0,
              stable_count INTEGER NOT NULL DEFAULT 0,
              watch_count INTEGER NOT NULL DEFAULT 0,
              downgrade_count INTEGER NOT NULL DEFAULT 0,
              remove_count INTEGER NOT NULL DEFAULT 0,
              serverchan_push_status TEXT,
              serverchan_pushed_at TEXT,
              serverchan_push_result TEXT,
              summary_json TEXT
            );
            CREATE TABLE IF NOT EXISTS watchlist_refresh_runs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              batch_id INTEGER,
              address TEXT NOT NULL,
              label TEXT,
              source_reason TEXT,
              old_score REAL,
              fresh_score REAL,
              score_delta REAL,
              fresh_grade TEXT,
              decision TEXT,
              auto_action TEXT,
              recommendation TEXT,
              score_flags TEXT,
              applied_caps TEXT,
              analysis_path TEXT,
              error TEXT,
              created_at TEXT NOT NULL
            );
            """
        )
        self._ensure_alert_push_columns()
        self._ensure_indexes()
        self.conn.commit()

    def _ensure_alert_push_columns(self) -> None:
        columns = {row["name"] for row in self.conn.execute("PRAGMA table_info(alerts)").fetchall()}
        legacy_without_status = "push_status" not in columns
        if legacy_without_status:
            self.conn.execute("ALTER TABLE alerts ADD COLUMN push_status TEXT")
        if "push_batch_id" not in columns:
            self.conn.execute("ALTER TABLE alerts ADD COLUMN push_batch_id TEXT")
        if "pushed_at" not in columns:
            self.conn.execute("ALTER TABLE alerts ADD COLUMN pushed_at TEXT")
        if "push_result" not in columns:
            self.conn.execute("ALTER TABLE alerts ADD COLUMN push_result TEXT")
        if legacy_without_status:
            self.conn.execute("UPDATE alerts SET push_status='sent' WHERE push_status IS NULL")

    def _ensure_indexes(self) -> None:
        self.conn.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_runs_status_address_created
              ON runs(status, address, created_at DESC, id DESC);
            CREATE INDEX IF NOT EXISTS idx_runs_status_created
              ON runs(status, created_at DESC, id DESC);
            CREATE INDEX IF NOT EXISTS idx_alerts_push_address_created
              ON alerts(push_status, address, pushed_at DESC, created_at DESC, id DESC);
            CREATE INDEX IF NOT EXISTS idx_alerts_push_created
              ON alerts(push_status, pushed_at DESC, created_at DESC, id DESC);
            CREATE INDEX IF NOT EXISTS idx_watchlist_refresh_runs_address_created
              ON watchlist_refresh_runs(address, created_at DESC, id DESC);
            """
        )

    def start_cycle(self) -> int:
        now = utc_now()
        self.conn.execute(
            """
            UPDATE cycles
            SET finished_at=?, status=?, note=?
            WHERE status='running' AND finished_at IS NULL
            """,
            (now, "interrupted", "superseded_by_new_cycle"),
        )
        cur = self.conn.execute(
            "INSERT INTO cycles(started_at, status) VALUES (?, ?)",
            (now, "running"),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def finish_cycle(self, cycle_id: int, status: str, note: str = "") -> None:
        self.conn.execute(
            "UPDATE cycles SET finished_at=?, status=?, note=? WHERE id=?",
            (utc_now(), status, note, cycle_id),
        )
        self.conn.commit()

    def start_fresh_candidate_round(self, supersede_pending_alerts: bool = True) -> dict[str, int]:
        now = utc_now()
        cur = self.conn.execute(
            """
            UPDATE candidates
            SET status=?, updated_at=?
            WHERE status<>?
            """,
            (PREVIOUS_ROUND_STATUS, now, PREVIOUS_ROUND_STATUS),
        )
        candidates_marked = int(cur.rowcount if cur.rowcount is not None else 0)
        alerts_marked = 0
        if supersede_pending_alerts:
            payload = json.dumps(
                {
                    "sent": False,
                    "reason": "superseded_by_new_scoring_round",
                    "note": "保留历史记录，但不再把旧模型的未发送告警混入新一轮推送。",
                },
                ensure_ascii=False,
            )
            cur = self.conn.execute(
                """
                UPDATE alerts
                SET push_status='superseded',
                    push_batch_id='superseded_by_new_scoring_round',
                    push_result=?
                WHERE push_status='pending'
                """,
                (payload,),
            )
            alerts_marked = int(cur.rowcount if cur.rowcount is not None else 0)
        self.conn.commit()
        return {"candidates_marked_previous_round": candidates_marked, "pending_alerts_superseded": alerts_marked}

    def upsert_candidate(self, candidate: AccountCandidate, status: str = "pending") -> dict[str, int]:
        return self.upsert_candidates([candidate], status=status)

    def existing_candidates(self, addresses: list[str]) -> dict[str, dict[str, Any]]:
        existing: dict[str, dict[str, Any]] = {}
        normalized = [address.lower() for address in addresses if address]
        for start in range(0, len(normalized), 500):
            chunk = normalized[start : start + 500]
            if not chunk:
                continue
            placeholders = ",".join("?" for _ in chunk)
            rows = self.conn.execute(
                f"SELECT * FROM candidates WHERE address IN ({placeholders})",
                tuple(chunk),
            ).fetchall()
            existing.update({row["address"]: dict(row) for row in rows})
        return existing

    def upsert_candidates(self, candidates: list[AccountCandidate], status: str = "pending") -> dict[str, int]:
        if not candidates:
            return {"inserted": 0, "refresh_score": 0}
        now = utc_now()
        existing = self.existing_candidates([candidate.address for candidate in candidates])
        rows = []
        inserted = 0
        refresh_score = 0
        for candidate in candidates:
            address = candidate.address.lower()
            previous = existing.get(address)
            context = dict(candidate.leaderboard_context)
            row_status = status
            if previous and status == "pending":
                row_status = REFRESH_SCORE_STATUS
                refresh_score += 1
                context["seen_before"] = True
                context["scan_prompt"] = REFRESH_SCORE_PROMPT
                context["previous_status"] = previous.get("status")
                context["previous_updated_at"] = previous.get("updated_at")
                context["previous_best_rank"] = previous.get("best_rank")
            else:
                inserted += 1
                context.setdefault("seen_before", False)
                context.setdefault("scan_prompt", "新发现")
            rows.append(
                (
                    address,
                    candidate.display_name,
                    candidate.best_rank,
                    candidate.discovery_score,
                    json.dumps(candidate.source_keys, ensure_ascii=False),
                    json.dumps(context, ensure_ascii=False),
                    row_status,
                    now,
                )
            )
        self.conn.executemany(
            """
            INSERT INTO candidates(address, display_name, best_rank, discovery_score, source_keys, leaderboard_context, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(address) DO UPDATE SET
              display_name=excluded.display_name,
              best_rank=excluded.best_rank,
              discovery_score=excluded.discovery_score,
              source_keys=excluded.source_keys,
              leaderboard_context=excluded.leaderboard_context,
              status=excluded.status,
              updated_at=excluded.updated_at
            """,
            rows,
        )
        self.conn.commit()
        return {"inserted": inserted, "refresh_score": refresh_score}

    def pending_candidates(self, limit: int) -> list[dict[str, Any]]:
        placeholders = ",".join("?" for _ in PENDING_CANDIDATE_STATUSES)
        rows = self.conn.execute(
            f"SELECT * FROM candidates WHERE status IN ({placeholders}) ORDER BY discovery_score DESC LIMIT ?",
            (*PENDING_CANDIDATE_STATUSES, limit),
        ).fetchall()
        return [dict(row) for row in rows]

    def pending_candidate_count(self) -> int:
        placeholders = ",".join("?" for _ in PENDING_CANDIDATE_STATUSES)
        row = self.conn.execute(
            f"SELECT COUNT(*) AS n FROM candidates WHERE status IN ({placeholders})",
            PENDING_CANDIDATE_STATUSES,
        ).fetchone()
        return int(row["n"] if row is not None else 0)

    def set_candidate_status(self, address: str, status: str) -> None:
        self.conn.execute(
            "UPDATE candidates SET status=?, updated_at=? WHERE address=?",
            (status, utc_now(), address),
        )
        self.conn.commit()

    def record_prefilter(self, result: PrefilterResult) -> None:
        self.conn.execute(
            """
            INSERT INTO runs(address, status, reason, payload, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                result.address,
                "prefilter_passed" if result.passed else "prefilter_skipped",
                result.reason,
                json.dumps(
                    {
                        "trade_count": result.trade_count,
                        "active_days": result.active_days,
                        "avg_trades_per_day": result.avg_trades_per_day,
                        "flags": result.flags,
                    },
                    ensure_ascii=False,
                ),
                utc_now(),
            ),
        )
        self.conn.commit()

    def record_scoring(self, result: ScoringResult) -> None:
        self.conn.execute(
            """
            INSERT INTO runs(address, status, final_score, decision, alert_grade, auto_action, payload, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.address,
                "scored",
                result.final_score,
                result.decision,
                result.alert_grade,
                result.auto_action,
                json.dumps(result.payload, ensure_ascii=False),
                utc_now(),
            ),
        )
        self.conn.commit()

    def record_account_error(self, address: str, status: str, reason: str, payload: dict[str, Any] | None = None) -> None:
        self.conn.execute(
            """
            INSERT INTO runs(address, status, reason, payload, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                address,
                status,
                reason,
                json.dumps(payload or {"error": reason}, ensure_ascii=False),
                utc_now(),
            ),
        )
        self.conn.commit()

    def record_alert(
        self,
        address: str,
        final_score: float,
        alert_grade: str,
        title: str,
        message: str,
        push_status: str = "pending",
    ) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO alerts(address, final_score, alert_grade, title, message, created_at, push_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (address, final_score, alert_grade, title, message, utc_now(), push_status),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def pending_alerts_for_push(self, limit: int) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT *
            FROM alerts
            WHERE push_status='pending'
            ORDER BY id ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]

    def pending_alert_push_count(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) AS n FROM alerts WHERE push_status='pending'").fetchone()
        return int(row["n"] if row is not None else 0)

    def archive_pending_alerts_missing_markers(self, required_markers: list[str], reason: str) -> int:
        markers = [marker for marker in required_markers if marker]
        if not markers:
            return 0
        rows = self.conn.execute(
            """
            SELECT id, message
            FROM alerts
            WHERE push_status='pending'
            ORDER BY id ASC
            """
        ).fetchall()

        def has_marker_group(message: str, marker_group: str) -> bool:
            alternatives = [item.strip() for item in marker_group.split("||") if item.strip()]
            return any(marker in message for marker in alternatives)

        stale_ids = [
            int(row["id"])
            for row in rows
            if any(not has_marker_group(str(row["message"] or ""), marker) for marker in markers)
        ]
        if not stale_ids:
            return 0
        placeholders = ",".join("?" for _ in stale_ids)
        payload = json.dumps(
            {
                "sent": False,
                "reason": reason,
                "required_markers": markers,
            },
            ensure_ascii=False,
        )
        self.conn.execute(
            f"""
            UPDATE alerts
            SET push_status='archived',
                push_batch_id=?,
                push_result=?
            WHERE id IN ({placeholders})
            """,
            (reason, payload, *stale_ids),
        )
        self.conn.commit()
        return len(stale_ids)

    def archive_pending_alerts_at_or_below_score(self, threshold: float, reason: str) -> int:
        rows = self.conn.execute(
            """
            SELECT id
            FROM alerts
            WHERE push_status='pending'
              AND COALESCE(final_score, 0) <= ?
            ORDER BY id ASC
            """,
            (threshold,),
        ).fetchall()
        stale_ids = [int(row["id"]) for row in rows]
        if not stale_ids:
            return 0
        placeholders = ",".join("?" for _ in stale_ids)
        payload = json.dumps(
            {
                "sent": False,
                "reason": reason,
                "minimum_score_exclusive": threshold,
            },
            ensure_ascii=False,
        )
        self.conn.execute(
            f"""
            UPDATE alerts
            SET push_status='archived',
                push_batch_id=?,
                push_result=?
            WHERE id IN ({placeholders})
            """,
            (reason, payload, *stale_ids),
        )
        self.conn.commit()
        return len(stale_ids)

    def mark_alert_push_result(self, alert_ids: list[int], batch_id: str, result: dict[str, Any]) -> None:
        if not alert_ids:
            return
        status = "sent" if bool(result.get("sent")) else "pending"
        pushed_at = utc_now() if status == "sent" else None
        payload = json.dumps(result, ensure_ascii=False)
        placeholders = ",".join("?" for _ in alert_ids)
        self.conn.execute(
            f"""
            UPDATE alerts
            SET push_status=?,
                push_batch_id=?,
                pushed_at=?,
                push_result=?
            WHERE id IN ({placeholders})
            """,
            (status, batch_id, pushed_at, payload, *alert_ids),
        )
        self.conn.commit()

    def upsert_manual_watchlist_account(self, address: str, label: str = "", note: str = "", enabled: bool = True) -> None:
        now = utc_now()
        self.conn.execute(
            """
            INSERT INTO watchlist_manual_accounts(address, label, note, enabled, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(address) DO UPDATE SET
              label=excluded.label,
              note=excluded.note,
              enabled=excluded.enabled,
              updated_at=excluded.updated_at
            """,
            (address.lower(), label, note, 1 if enabled else 0, now, now),
        )
        self.conn.commit()

    def set_manual_watchlist_enabled(self, address: str, enabled: bool) -> None:
        self.conn.execute(
            "UPDATE watchlist_manual_accounts SET enabled=?, updated_at=? WHERE address=?",
            (1 if enabled else 0, utc_now(), address.lower()),
        )
        self.conn.commit()

    def start_watchlist_refresh_batch(self) -> int:
        cur = self.conn.execute(
            "INSERT INTO watchlist_refresh_batches(started_at, status) VALUES (?, ?)",
            (utc_now(), "running"),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def record_watchlist_refresh_run(self, row: dict[str, Any]) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO watchlist_refresh_runs(
              batch_id, address, label, source_reason, old_score, fresh_score, score_delta,
              fresh_grade, decision, auto_action, recommendation, score_flags, applied_caps,
              analysis_path, error, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row.get("batch_id"),
                str(row.get("address") or "").lower(),
                row.get("label"),
                row.get("source_reason"),
                row.get("old_score"),
                row.get("fresh_score"),
                row.get("score_delta"),
                row.get("fresh_grade"),
                row.get("decision"),
                row.get("auto_action"),
                row.get("recommendation"),
                json.dumps(row.get("score_flags") or [], ensure_ascii=False),
                json.dumps(row.get("applied_caps") or [], ensure_ascii=False),
                row.get("analysis_path"),
                row.get("error"),
                row.get("created_at") or utc_now(),
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def finish_watchlist_refresh_batch(
        self,
        batch_id: int,
        status: str,
        summary: dict[str, Any],
        serverchan_result: dict[str, Any] | None = None,
    ) -> None:
        result = serverchan_result or {}
        push_status = "sent" if bool(result.get("sent")) else str(result.get("reason") or "not_sent")
        pushed_at = utc_now() if bool(result.get("sent")) else None
        self.conn.execute(
            """
            UPDATE watchlist_refresh_batches
            SET finished_at=?,
                status=?,
                total=?,
                succeeded=?,
                failed=?,
                skipped_recent=?,
                stable_count=?,
                watch_count=?,
                downgrade_count=?,
                remove_count=?,
                serverchan_push_status=?,
                serverchan_pushed_at=?,
                serverchan_push_result=?,
                summary_json=?
            WHERE id=?
            """,
            (
                utc_now(),
                status,
                int(summary.get("total") or 0),
                int(summary.get("succeeded") or 0),
                int(summary.get("failed") or 0),
                int(summary.get("skipped_recent") or 0),
                int(summary.get("stable_count") or 0),
                int(summary.get("watch_count") or 0),
                int(summary.get("downgrade_count") or 0),
                int(summary.get("remove_count") or 0),
                push_status,
                pushed_at,
                json.dumps(result, ensure_ascii=False),
                json.dumps(summary, ensure_ascii=False),
                batch_id,
            ),
        )
        self.conn.commit()

    def status(self) -> dict[str, Any]:
        counts = {}
        for row in self.conn.execute("SELECT status, count(*) AS n FROM candidates GROUP BY status"):
            counts[row["status"]] = row["n"]
        alert_counts = {}
        for row in self.conn.execute("SELECT push_status, count(*) AS n FROM alerts GROUP BY push_status"):
            alert_counts[row["push_status"] or "unknown"] = row["n"]
        latest_cycle = self.conn.execute("SELECT * FROM cycles ORDER BY id DESC LIMIT 1").fetchone()
        return {
            "db_path": str(self.path),
            "candidate_counts": counts,
            "alert_push_counts": alert_counts,
            "latest_cycle": dict(latest_cycle) if latest_cycle else None,
        }
