from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dashboard import server as dashboard_server


class DashboardServerTests(unittest.TestCase):
    def test_ensure_ui_files_copies_example_configs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "auto_screen_data" / "dashboard"
            auto_config = root / "auto_screen_config.ui.json"
            agent_config = root / "agent_core_config.ui.json"
            auto_example = root / "auto_screen_config.example.json"
            agent_example = root / "agent_core_config.example.json"
            auto_example.write_text('{"data_dir": "auto_screen_data"}', encoding="utf-8")
            agent_example.write_text('{"mode": "mock"}', encoding="utf-8")

            with (
                patch.object(dashboard_server, "UI_DIR", ui_dir),
                patch.object(dashboard_server, "AUTO_CONFIG", auto_config),
                patch.object(dashboard_server, "AGENT_CONFIG", agent_config),
                patch.object(dashboard_server, "AUTO_CONFIG_EXAMPLE", auto_example),
                patch.object(dashboard_server, "AGENT_CONFIG_EXAMPLE", agent_example),
            ):
                dashboard_server.ensure_ui_files()

            self.assertTrue(ui_dir.exists())
            self.assertEqual(json.loads(auto_config.read_text(encoding="utf-8"))["data_dir"], "auto_screen_data")
            self.assertEqual(json.loads(agent_config.read_text(encoding="utf-8"))["mode"], "mock")

    def test_excel_sidecar_summary_counts_and_reverses_recent_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            excel_path = root / "out" / "candidates.xlsx"
            excel_path.parent.mkdir(parents=True)
            sidecar = excel_path.with_suffix(excel_path.suffix + ".json")
            sidecar.write_text(
                json.dumps(
                    {
                        "alerts": [{"address": "old"}, {"address": "new"}],
                        "all_scored": [{"address": "scored"}],
                        "agent_reviews": [{"address": "reviewed"}],
                        "skipped": [],
                    }
                ),
                encoding="utf-8",
            )

            with patch.object(dashboard_server, "ROOT", root):
                summary = dashboard_server.excel_sidecar_summary({"excel_path": "out/candidates.xlsx"})

            self.assertEqual(summary["sheet_counts"]["alerts"], 2)
            self.assertEqual(summary["alerts"][0]["address"], "new")
            self.assertEqual(summary["excel_path"], str(excel_path))

    def test_list_accounts_reads_recent_analysis_and_agent_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            account_dir = root / "auto_screen_data" / "accounts" / "0xabc"
            account_dir.mkdir(parents=True)
            (account_dir / "account_analysis.json").write_text(
                json.dumps(
                    {
                        "account_label": "Alpha",
                        "final_score": 48.5,
                        "alert_grade": "B",
                        "auto_action": "notify",
                        "decision": "watch",
                        "data_quality_score": 72,
                        "pnl_quality_score": 61,
                        "copy_capacity_score": 54,
                    }
                ),
                encoding="utf-8",
            )
            (account_dir / "agent_review.json").write_text(
                json.dumps({"agent_verdict": "watchlist", "confidence": 0.82}),
                encoding="utf-8",
            )

            with patch.object(dashboard_server, "ROOT", root):
                accounts = dashboard_server.list_accounts({"data_dir": "auto_screen_data"}, limit=10)

            self.assertEqual(len(accounts), 1)
            self.assertEqual(accounts[0]["label"], "Alpha")
            self.assertEqual(accounts[0]["agent_verdict"], "watchlist")
            self.assertEqual(accounts[0]["agent_confidence"], 0.82)

    def test_progress_summary_reads_progress_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            progress_path = root / "auto_screen_data" / "progress.json"
            progress_path.parent.mkdir(parents=True)
            progress_path.write_text(
                json.dumps(
                    {
                        "phase": "collecting_account",
                        "phase_label": "拉取账号数据",
                        "message": "collecting",
                        "updated_at": "2026-05-13T18:00:00+00:00",
                        "updated_ts": 9999999999,
                        "cycle_id": 7,
                        "current_account": "0xabc",
                        "current_index": 2,
                        "batch_total": 4,
                        "stats": {"scanned": 10, "processed": 1, "alerts": 0, "skipped": 0},
                        "history": [{"phase": "collecting_account"}],
                    }
                ),
                encoding="utf-8",
            )

            with patch.object(dashboard_server, "ROOT", root):
                summary = dashboard_server.progress_summary(
                    {"progress_path": "auto_screen_data/progress.json"},
                    {"running": True},
                    {"latest_cycles": [{"id": 7, "status": "running"}]},
                )

            self.assertEqual(summary["health"], "ok")
            self.assertEqual(summary["phase"], "collecting_account")
            self.assertEqual(summary["percent"], 50.0)
            self.assertEqual(summary["stats"]["scanned"], 10)

    def test_progress_summary_keeps_sleeping_cycle_healthy_during_configured_sleep(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            progress_path = root / "auto_screen_data" / "progress.json"
            progress_path.parent.mkdir(parents=True)
            progress_path.write_text(
                json.dumps(
                    {
                        "phase": "sleeping",
                        "phase_label": "等待下一轮",
                        "message": "本轮完成，休眠 600 秒后继续",
                        "updated_at": "2026-05-13T18:00:00+00:00",
                        "updated_ts": 1000,
                        "cycle_id": 8,
                        "sleep_seconds": 600,
                        "stats": {"scanned": 10, "processed": 4, "alerts": 1, "skipped": 1},
                    }
                ),
                encoding="utf-8",
            )

            with (
                patch.object(dashboard_server, "ROOT", root),
                patch.object(dashboard_server.time, "time", return_value=1500.0),
            ):
                summary = dashboard_server.progress_summary(
                    {"progress_path": "auto_screen_data/progress.json", "scan": {"cycle_sleep_seconds": 600}},
                    {"running": True},
                    {"latest_cycles": [{"id": 8, "status": "done"}]},
                )

            self.assertEqual(summary["health"], "ok")
            self.assertEqual(summary["phase"], "sleeping")
            self.assertEqual(summary["percent"], 100)

    def test_launch_auto_screen_uses_detached_safe_stdio(self) -> None:
        class FakeProcess:
            pid = 4321

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "auto_screen_data" / "dashboard"
            auto_config = root / "auto_screen_config.ui.json"
            auto_example = root / "auto_screen_config.example.json"
            agent_config = root / "agent_core_config.ui.json"
            agent_example = root / "agent_core_config.example.json"
            auto_example.write_text("{}", encoding="utf-8")
            agent_example.write_text("{}", encoding="utf-8")
            pid_file = ui_dir / "auto_screen_process.json"
            log_file = ui_dir / "auto_screen.log"

            with (
                patch.object(dashboard_server, "ROOT", root),
                patch.object(dashboard_server, "UI_DIR", ui_dir),
                patch.object(dashboard_server, "AUTO_CONFIG", auto_config),
                patch.object(dashboard_server, "AGENT_CONFIG", agent_config),
                patch.object(dashboard_server, "AUTO_CONFIG_EXAMPLE", auto_example),
                patch.object(dashboard_server, "AGENT_CONFIG_EXAMPLE", agent_example),
                patch.object(dashboard_server, "PID_FILE", pid_file),
                patch.object(dashboard_server, "LOG_FILE", log_file),
                patch.object(dashboard_server, "read_process_state", return_value={"running": False}),
                patch.object(dashboard_server.subprocess, "Popen", return_value=FakeProcess()) as popen,
            ):
                result = dashboard_server.launch_auto_screen(["once", "--dry-run-alerts"], "once")

            self.assertTrue(result["started"])
            args, kwargs = popen.call_args
            self.assertEqual(args[0][-2:], ["once", "--dry-run-alerts"])
            self.assertIs(kwargs["stdin"], dashboard_server.subprocess.DEVNULL)
            self.assertEqual(kwargs["stderr"], dashboard_server.subprocess.STDOUT)
            self.assertEqual(kwargs["env"]["PYTHONUTF8"], "1")
            self.assertEqual(kwargs["env"]["PYTHONIOENCODING"], "utf-8")
            self.assertEqual(json.loads(pid_file.read_text(encoding="utf-8"))["pid"], 4321)

    def test_build_auto_screen_args_defaults_to_real_alerts(self) -> None:
        self.assertEqual(dashboard_server.build_auto_screen_args("run", {}), ["run"])
        self.assertEqual(
            dashboard_server.build_auto_screen_args("once", {"limit_candidates": 10, "process_limit": 3}),
            ["once", "--limit-candidates", "10", "--process-limit", "3"],
        )

    def test_build_auto_screen_args_only_dry_runs_when_requested(self) -> None:
        self.assertEqual(
            dashboard_server.build_auto_screen_args("run", {"dry_run_alerts": True}),
            ["run", "--dry-run-alerts"],
        )
        self.assertEqual(
            dashboard_server.build_auto_screen_args(
                "once",
                {"limit_candidates": 10, "process_limit": 3, "dry_run_alerts": True, "prefilter_only": True},
            ),
            ["once", "--limit-candidates", "10", "--process-limit", "3", "--dry-run-alerts", "--prefilter-only"],
        )


if __name__ == "__main__":
    unittest.main()
