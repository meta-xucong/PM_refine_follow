from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AgentMemoryStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

    def close(self) -> None:
        self.conn.close()

    def init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS agent_decisions (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              account_address TEXT NOT NULL,
              final_score REAL,
              alert_grade TEXT,
              auto_action TEXT,
              agent_verdict TEXT NOT NULL,
              confidence REAL NOT NULL,
              human_review_priority INTEGER NOT NULL,
              copy_style TEXT NOT NULL,
              reasoning_json TEXT NOT NULL,
              source_analysis_path TEXT,
              model_name TEXT,
              prompt_version TEXT,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS user_feedback (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              account_address TEXT NOT NULL,
              feedback_type TEXT NOT NULL,
              note TEXT,
              source TEXT NOT NULL,
              source_ref TEXT,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS candidate_snapshots (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              account_address TEXT NOT NULL,
              snapshot_date TEXT NOT NULL,
              final_score REAL,
              alert_grade TEXT,
              data_quality_score REAL,
              pnl_quality_score REAL,
              copy_capacity_score REAL,
              realized_pnl_7d REAL,
              realized_pnl_30d REAL,
              traded_markets INTEGER,
              positions_value REAL,
              payload_json TEXT,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS followup_outcomes (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              account_address TEXT NOT NULL,
              pushed_at TEXT,
              horizon_days INTEGER NOT NULL,
              outcome_verdict TEXT NOT NULL,
              pnl_delta REAL,
              score_delta REAL,
              false_positive_reason TEXT,
              review_json TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS preference_profile (
              key TEXT PRIMARY KEY,
              value_json TEXT NOT NULL,
              confidence REAL NOT NULL DEFAULT 0,
              updated_at TEXT NOT NULL
            );
            """
        )
        self.conn.commit()

    def add_decision(
        self,
        *,
        account_address: str,
        analysis: dict[str, Any],
        review: dict[str, Any],
        source_analysis_path: str | None,
        model_name: str,
        prompt_version: str,
    ) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO agent_decisions(
              account_address, final_score, alert_grade, auto_action, agent_verdict,
              confidence, human_review_priority, copy_style, reasoning_json,
              source_analysis_path, model_name, prompt_version, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                account_address.lower(),
                analysis.get("final_score"),
                analysis.get("alert_grade"),
                analysis.get("auto_action"),
                review["agent_verdict"],
                review["confidence"],
                review["human_review_priority"],
                review["copy_style"],
                json.dumps(review, ensure_ascii=False),
                source_analysis_path,
                model_name,
                prompt_version,
                utc_now(),
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def add_feedback(self, event: dict[str, Any]) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO user_feedback(account_address, feedback_type, note, source, source_ref, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(event["account_address"]).lower(),
                event["feedback_type"],
                event.get("note"),
                event["source"],
                event.get("source_ref"),
                event.get("created_at") or utc_now(),
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def add_snapshot(self, analysis: dict[str, Any], snapshot_date: str | None = None) -> int:
        api = analysis.get("api_summary") or {}
        breakdown = analysis.get("score_breakdown") or {}
        cur = self.conn.execute(
            """
            INSERT INTO candidate_snapshots(
              account_address, snapshot_date, final_score, alert_grade, data_quality_score,
              pnl_quality_score, copy_capacity_score, realized_pnl_7d, realized_pnl_30d,
              traded_markets, positions_value, payload_json, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(analysis.get("account_address") or "").lower(),
                snapshot_date or utc_now()[:10],
                analysis.get("final_score"),
                analysis.get("alert_grade"),
                analysis.get("data_quality_score"),
                analysis.get("pnl_quality_score"),
                analysis.get("copy_capacity_score"),
                breakdown.get("closed_positions_realized_pnl_7d"),
                breakdown.get("closed_positions_realized_pnl_30d"),
                api.get("traded_markets"),
                api.get("positions_value"),
                json.dumps(analysis, ensure_ascii=False),
                utc_now(),
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def add_outcome(self, review: dict[str, Any], pushed_at: str | None = None, score_delta: float | None = None) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO followup_outcomes(
              account_address, pushed_at, horizon_days, outcome_verdict, pnl_delta,
              score_delta, false_positive_reason, review_json, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(review["account_address"]).lower(),
                pushed_at,
                review["horizon_days"],
                review["outcome_verdict"],
                None,
                score_delta,
                review.get("false_positive_reason"),
                json.dumps(review, ensure_ascii=False),
                utc_now(),
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def recent_memory(self, account_address: str, limit: int = 20) -> dict[str, list[dict[str, Any]]]:
        address = account_address.lower()
        decisions = [
            _row_to_dict(row)
            for row in self.conn.execute(
                "SELECT * FROM agent_decisions WHERE account_address=? ORDER BY id DESC LIMIT ?",
                (address, limit),
            )
        ]
        feedback = [
            _row_to_dict(row)
            for row in self.conn.execute(
                "SELECT * FROM user_feedback WHERE account_address=? ORDER BY id DESC LIMIT ?",
                (address, limit),
            )
        ]
        outcomes = [
            _row_to_dict(row)
            for row in self.conn.execute(
                "SELECT * FROM followup_outcomes WHERE account_address=? ORDER BY id DESC LIMIT ?",
                (address, limit),
            )
        ]
        return {"previous_reviews": decisions, "user_feedback": feedback, "followup_outcomes": outcomes}

    def status(self) -> dict[str, Any]:
        def count(table: str) -> int:
            return int(self.conn.execute(f"SELECT count(*) AS n FROM {table}").fetchone()["n"])

        return {
            "memory_db": str(self.path),
            "agent_decisions": count("agent_decisions"),
            "user_feedback": count("user_feedback"),
            "candidate_snapshots": count("candidate_snapshots"),
            "followup_outcomes": count("followup_outcomes"),
        }


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    for key in ("reasoning_json", "review_json", "payload_json", "value_json"):
        if isinstance(data.get(key), str):
            try:
                data[key] = json.loads(data[key])
            except json.JSONDecodeError:
                pass
    return data

