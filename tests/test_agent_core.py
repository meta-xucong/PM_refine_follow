from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from agent_core.candidate_reviewer import review_analysis
from agent_core.config import load_config
from agent_core.daily_planner import build_daily_plan
from agent_core.feedback import import_feedback_events
from agent_core.json_schema import SchemaValidationError, load_schema, validate_json
from agent_core.llm_client import StaticMockLlmClient
from agent_core.memory_store import AgentMemoryStore
from agent_core.outcome_tracker import review_outcome
from auto_screen.excel_store import ExcelStore
from auto_screen.scheduler import maybe_run_agent_review, result_row


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "docs" / "agent_core" / "schemas"
PROMPT_DIR = ROOT / "docs" / "agent_core" / "prompts"


def agent_config(tmp: str | Path) -> dict:
    cfg = load_config(None)
    cfg["memory_db"] = str(Path(tmp) / "agent_memory.sqlite3")
    cfg["prompt_dir"] = str(PROMPT_DIR)
    cfg["schema_dir"] = str(SCHEMA_DIR)
    return cfg


def sample_analysis(score: float = 66.0, **overrides) -> dict:
    data = {
        "account_address": "0x1111111111111111111111111111111111111111",
        "account_label": "Alpha",
        "analysis_window": "2026-05-01 -> 2026-05-14",
        "final_score": score,
        "decision": "selective_copying_only",
        "alert_grade": "B" if score >= 65 else "C",
        "auto_action": "push_selective_candidate" if score >= 65 else "push_watchlist",
        "data_quality_score": 8.0,
        "pnl_quality_score": 10.0,
        "copy_capacity_score": 6.0,
        "score_flags": [],
        "metrics": {},
        "pnl_curve": {},
        "keyword_profile": {},
        "api_summary": {"traded_markets": 10, "positions_value": 100},
        "score_breakdown": {
            "closed_positions_realized_pnl_7d": 10,
            "closed_positions_realized_pnl_30d": 50,
        },
    }
    data.update(overrides)
    return data


class AgentCoreTests(unittest.TestCase):
    def test_schema_validation_accepts_candidate_review_and_rejects_bad_enum(self):
        schema = load_schema(SCHEMA_DIR / "candidate_review.schema.json")
        valid = {
            "agent_verdict": "watchlist",
            "confidence": 0.7,
            "copy_style": "selective",
            "human_review_priority": 2,
            "main_reason": "good enough",
            "risk_summary": "some risk",
            "recommended_followup": "review manually",
            "positive_evidence": [],
            "negative_evidence": [],
            "tags": ["b"],
            "safety_overrides": [],
            "needs_human_confirmation": True,
        }
        validate_json(valid, schema)
        invalid = dict(valid)
        invalid["agent_verdict"] = "buy_now"
        with self.assertRaises(SchemaValidationError):
            validate_json(invalid, schema)

    def test_memory_store_records_decision_feedback_snapshot_and_outcome(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = AgentMemoryStore(Path(tmp) / "memory.sqlite3")
            analysis = sample_analysis()
            review = {
                "agent_verdict": "watchlist",
                "confidence": 0.7,
                "copy_style": "selective",
                "human_review_priority": 2,
                "main_reason": "ok",
                "risk_summary": "risk",
                "recommended_followup": "manual",
                "positive_evidence": [],
                "negative_evidence": [],
                "tags": [],
                "safety_overrides": [],
                "needs_human_confirmation": True,
            }
            store.add_decision(
                account_address=analysis["account_address"],
                analysis=analysis,
                review=review,
                source_analysis_path="analysis.json",
                model_name="mock",
                prompt_version="candidate_review_zh.md",
            )
            store.add_feedback({"account_address": analysis["account_address"], "feedback_type": "watch", "source": "manual"})
            store.add_snapshot(analysis)
            store.add_outcome(
                {
                    "account_address": analysis["account_address"],
                    "horizon_days": 7,
                    "outcome_verdict": "still_watchlist",
                    "false_positive_reason": None,
                }
            )
            status = store.status()
            self.assertEqual(status["agent_decisions"], 1)
            self.assertEqual(status["user_feedback"], 1)
            self.assertEqual(status["candidate_snapshots"], 1)
            self.assertEqual(status["followup_outcomes"], 1)
            store.close()

    def test_candidate_review_applies_hard_safety_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = agent_config(tmp)
            analysis = sample_analysis(31.0)
            llm = StaticMockLlmClient(
                {
                    "agent_verdict": "strong_candidate",
                    "confidence": 1.5,
                    "copy_style": "broad",
                    "human_review_priority": 0,
                    "main_reason": "too optimistic",
                    "risk_summary": "none",
                    "recommended_followup": "copy",
                    "positive_evidence": [],
                    "negative_evidence": [],
                    "tags": [],
                    "safety_overrides": [],
                    "needs_human_confirmation": True,
                }
            )
            review = review_analysis(analysis, cfg, llm_client=llm, dry_run=True)
            self.assertEqual(review["agent_verdict"], "reject")
            self.assertEqual(review["copy_style"], "none")
            self.assertIn("score_below_or_equal_40", review["safety_overrides"])
            self.assertEqual(review["confidence"], 1.0)
            self.assertEqual(review["human_review_priority"], 5)

    def test_candidate_review_writes_memory(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = agent_config(tmp)
            store = AgentMemoryStore(cfg["memory_db"])
            review = review_analysis(sample_analysis(), cfg, memory_store=store, source_analysis_path="analysis.json")
            self.assertIn(review["agent_verdict"], {"watchlist", "strong_candidate"})
            self.assertEqual(store.status()["agent_decisions"], 1)
            store.close()

    def test_feedback_import_validates_and_stores(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = agent_config(tmp)
            store = AgentMemoryStore(cfg["memory_db"])
            result = import_feedback_events(
                [
                    {
                        "account_address": "0x1111111111111111111111111111111111111111",
                        "feedback_type": "blacklist",
                        "source": "manual",
                    },
                    {"account_address": "bad", "feedback_type": "bad", "source": "manual"},
                ],
                schema_path=SCHEMA_DIR / "feedback_event.schema.json",
                memory_store=store,
            )
            self.assertEqual(result["imported"], 1)
            self.assertEqual(result["ignored"], 1)
            self.assertEqual(store.status()["user_feedback"], 1)
            store.close()

    def test_daily_plan_and_outcome_review_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = agent_config(tmp)
            plan = build_daily_plan({"date": "2026-05-14"}, cfg)
            self.assertTrue(plan["scan_plan"])
            outcome = review_outcome(sample_analysis(60), sample_analysis(70), cfg, horizon_days=7)
            self.assertEqual(outcome["outcome_verdict"], "validated_good")

    def test_cli_status_and_review_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = agent_config(tmp)
            cfg_path = Path(tmp) / "agent_config.json"
            cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
            analysis_path = Path(tmp) / "analysis.json"
            analysis_path.write_text(json.dumps(sample_analysis()), encoding="utf-8")
            status = subprocess.run(
                [sys.executable, "-m", "agent_core.cli", "--config", str(cfg_path), "status"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("agent_decisions", status.stdout)
            review = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agent_core.cli",
                    "--config",
                    str(cfg_path),
                    "review",
                    "--analysis",
                    str(analysis_path),
                    "--dry-run",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("agent_verdict", review.stdout)

    def test_auto_screen_optional_agent_integration(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = {
                "excel_path": str(Path(tmp) / "candidates.xlsx"),
                "agent": {
                    "enabled": True,
                    "config_path": str(Path(tmp) / "agent_config.json"),
                    "dry_run": False,
                    "fail_open": True,
                },
            }
            agent_cfg = agent_config(tmp)
            Path(cfg["agent"]["config_path"]).write_text(json.dumps(agent_cfg), encoding="utf-8")
            analysis_path = Path(tmp) / "analysis.json"
            analysis_path.write_text(json.dumps(sample_analysis()), encoding="utf-8")
            result = SimpleNamespace(analysis_path=str(analysis_path), payload=sample_analysis())
            review = maybe_run_agent_review(cfg, result)
            self.assertIsNotNone(review)
            self.assertEqual(result.payload["agent_review"]["agent_verdict"], review["agent_verdict"])
            self.assertTrue((Path(tmp) / "agent_review.json").exists())
            row = result_row(result.payload)
            self.assertIn("agent_verdict", row)
            data = ExcelStore(cfg["excel_path"]).load()
            self.assertIn("agent_reviews", data)


if __name__ == "__main__":
    unittest.main()
