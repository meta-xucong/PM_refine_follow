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
            """
        )
        self._ensure_alert_push_columns()
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
        stale_ids = [
            int(row["id"])
            for row in rows
            if any(marker not in str(row["message"] or "") for marker in markers)
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
