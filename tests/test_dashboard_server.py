from __future__ import annotations

import csv
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from auto_screen.models import ScoringResult
from auto_screen.state_store import StateStore
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

    def test_auto_state_summary_groups_pushed_accounts_by_address(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "state.sqlite3"
            store = StateStore(db_path)
            first = store.record_alert(
                "0x1111111111111111111111111111111111111111",
                55,
                "B",
                "账号筛选结果：优先复核｜55.00 分｜Alpha",
                "m1",
                push_status="pending",
            )
            second = store.record_alert(
                "0x1111111111111111111111111111111111111111",
                62,
                "B",
                "账号筛选结果：优先复核｜62.00 分｜Alpha",
                "m2",
                push_status="pending",
            )
            pending = store.record_alert(
                "0x2222222222222222222222222222222222222222",
                80,
                "A",
                "账号筛选结果：重点关注｜80.00 分｜Beta",
                "m3",
                push_status="pending",
            )
            store.mark_alert_push_result([first], "batch-1", {"sent": True})
            store.mark_alert_push_result([second], "batch-2", {"sent": True})
            store.close()
            self.assertIsInstance(pending, int)

            with patch.object(dashboard_server, "ROOT", root):
                summary = dashboard_server.auto_state_summary({"state_db": "state.sqlite3"})

            pushed = summary["pushed_accounts"]
            self.assertEqual(len(pushed), 1)
            self.assertEqual(pushed[0]["address"], "0x1111111111111111111111111111111111111111")
            self.assertEqual(pushed[0]["label"], "Alpha")
            self.assertEqual(pushed[0]["push_count"], 2)
            self.assertEqual([r["score"] for r in pushed[0]["rounds"]], [62, 55])
            self.assertEqual([r["round_number"] for r in pushed[0]["rounds"]], [2, 1])

    def test_pushed_accounts_csv_exports_sent_alert_details(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "state.sqlite3"
            store = StateStore(db_path)
            alert_id = store.record_alert(
                "0x1111111111111111111111111111111111111111",
                62,
                "B",
                "账号筛选结果：B级｜62.00 分｜Alpha",
                "## 一句话结论\n这个账号当前评分为 62 分，系统归为“B级”。适合筛选后再考虑跟单。\n\n## 核心概括\n- 当前评分：62 分\n- 系统评级：B级\n- 系统建议：适合筛选后再考虑跟单。",
                push_status="pending",
            )
            store.mark_alert_push_result([alert_id], "batch-1", {"sent": True})
            store.close()

            with patch.object(dashboard_server, "ROOT", root):
                csv_text = dashboard_server.pushed_accounts_csv({"state_db": "state.sqlite3"})

            self.assertIn("钱包地址,昵称,分数,评级", csv_text)
            self.assertIn("0x1111111111111111111111111111111111111111", csv_text)
            self.assertIn("Alpha", csv_text)
            self.assertIn("batch-1", csv_text)
            data_rows = list(csv.reader(io.StringIO(csv_text)))
            self.assertEqual(data_rows[1][-1], "适合筛选后再考虑跟单。")
            self.assertNotIn("62", data_rows[1][-1])
            self.assertNotIn("B级", data_rows[1][-1])

    def test_serverchan_key_info_masks_and_saves_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            key_path = Path(tmp) / "sendkey.txt"
            cfg = {"serverchan": {"sendkey_file": str(key_path), "sendkey_env": "PM_TEST_SENDKEY"}}
            with patch.dict(os.environ, {"PM_TEST_SENDKEY": ""}, clear=False):
                empty = dashboard_server.serverchan_key_info(cfg)
                self.assertEqual(empty["active_source"], "未设置")

                saved = dashboard_server.save_serverchan_key(cfg, "SCT1234567890")

            self.assertEqual(key_path.read_text(encoding="utf-8"), "SCT1234567890")
            self.assertTrue(saved["saved"])
            self.assertEqual(saved["active_source"], "本地文件")
            self.assertEqual(saved["active_masked"], "SCT1...7890")
            self.assertEqual(saved["file_masked"], "SCT1...7890")

    def test_serverchan_key_info_env_takes_precedence_over_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            key_path = Path(tmp) / "sendkey.txt"
            key_path.write_text("SCTFILE1234", encoding="utf-8")
            cfg = {"serverchan": {"sendkey_file": str(key_path), "sendkey_env": "PM_TEST_SENDKEY"}}

            with patch.dict(os.environ, {"PM_TEST_SENDKEY": "SCTENV5678"}, clear=False):
                info = dashboard_server.serverchan_key_info(cfg)

            self.assertEqual(info["active_source"], "环境变量")
            self.assertEqual(info["active_masked"], "SCTE...5678")
            self.assertEqual(info["file_masked"], "SCTF...1234")

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
            store = StateStore(root / "state.sqlite3")
            store.record_scoring(
                ScoringResult(
                    address="0xabc",
                    final_score=42,
                    decision="old",
                    alert_grade="none",
                    auto_action="store_only",
                    analysis_path=str(account_dir / "old.json"),
                    payload={"account_address": "0xabc"},
                )
            )
            store.record_scoring(
                ScoringResult(
                    address="0xabc",
                    final_score=48.5,
                    decision="watch",
                    alert_grade="B",
                    auto_action="notify",
                    analysis_path=str(account_dir / "account_analysis.json"),
                    payload={"account_address": "0xabc"},
                )
            )
            store.close()

            with patch.object(dashboard_server, "ROOT", root):
                accounts = dashboard_server.list_accounts({"data_dir": "auto_screen_data", "state_db": "state.sqlite3"}, limit=10)

            self.assertEqual(len(accounts), 1)
            self.assertEqual(accounts[0]["label"], "Alpha")
            self.assertEqual(accounts[0]["agent_verdict"], "watchlist")
            self.assertEqual(accounts[0]["agent_confidence"], 0.82)
            self.assertEqual([item["score"] for item in accounts[0]["score_history"]], [48.5, 42])

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

    def test_progress_summary_exposes_leaderboard_api_cap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            progress_path = root / "auto_screen_data" / "progress.json"
            progress_path.parent.mkdir(parents=True)
            progress_path.write_text(
                json.dumps(
                    {
                        "phase": "leaderboard_scanned",
                        "phase_label": "排行榜扫描完成",
                        "message": "发现 10050 个候选账号",
                        "updated_at": "2026-05-15T12:00:00+00:00",
                        "updated_ts": 9999999999,
                        "cycle_id": 9,
                        "leaderboard_scan": {
                            "requested_rank_cap": 100000,
                            "api_cap_detected": True,
                            "api_visible_cap_rank": 10050,
                            "unique_candidates": 10050,
                        },
                    }
                ),
                encoding="utf-8",
            )

            with patch.object(dashboard_server, "ROOT", root):
                summary = dashboard_server.progress_summary(
                    {"progress_path": "auto_screen_data/progress.json"},
                    {"running": True},
                    {"latest_cycles": [{"id": 9, "status": "running"}]},
                )

            self.assertTrue(summary["leaderboard_scan"]["api_cap_detected"])
            self.assertEqual(summary["leaderboard_scan"]["api_visible_cap_rank"], 10050)

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

    def test_launch_watchlist_refresh_uses_detached_safe_stdio(self) -> None:
        class FakeProcess:
            pid = 2468

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui_dir = root / "auto_screen_data" / "dashboard"
            auto_config = root / "auto_screen_config.ui.json"
            auto_example = root / "auto_screen_config.example.json"
            agent_config = root / "agent_core_config.ui.json"
            agent_example = root / "agent_core_config.example.json"
            auto_example.write_text("{}", encoding="utf-8")
            agent_example.write_text("{}", encoding="utf-8")
            pid_file = ui_dir / "watchlist_refresh_process.json"
            log_file = ui_dir / "auto_screen.log"

            with (
                patch.object(dashboard_server, "ROOT", root),
                patch.object(dashboard_server, "UI_DIR", ui_dir),
                patch.object(dashboard_server, "AUTO_CONFIG", auto_config),
                patch.object(dashboard_server, "AGENT_CONFIG", agent_config),
                patch.object(dashboard_server, "AUTO_CONFIG_EXAMPLE", auto_example),
                patch.object(dashboard_server, "AGENT_CONFIG_EXAMPLE", agent_example),
                patch.object(dashboard_server, "WATCHLIST_PID_FILE", pid_file),
                patch.object(dashboard_server, "LOG_FILE", log_file),
                patch.object(dashboard_server, "read_watchlist_process_state", return_value={"running": False}),
                patch.object(dashboard_server.subprocess, "Popen", return_value=FakeProcess()) as popen,
            ):
                result = dashboard_server.launch_watchlist_refresh(
                    {"min_score": 60, "limit": 120, "interval_hours": 48, "dry_run_serverchan": True}
                )

            self.assertTrue(result["started"])
            args, kwargs = popen.call_args
            self.assertIn("refresh-watchlist", args[0])
            self.assertIn("--min-score", args[0])
            self.assertIn("60.0", args[0])
            self.assertIn("--interval-hours", args[0])
            self.assertIn("48.0", args[0])
            self.assertIn("--dry-run-serverchan", args[0])
            self.assertIs(kwargs["stdin"], dashboard_server.subprocess.DEVNULL)
            self.assertEqual(kwargs["stderr"], dashboard_server.subprocess.STDOUT)
            self.assertEqual(json.loads(pid_file.read_text(encoding="utf-8"))["pid"], 2468)

    def test_watchlist_refresh_summary_reads_db_and_latest_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "auto_screen_data"
            latest_dir = data_dir / "watchlist_refresh"
            latest_dir.mkdir(parents=True)
            db_path = data_dir / "state.sqlite3"
            store = StateStore(db_path)
            batch_id = store.start_watchlist_refresh_batch()
            store.record_watchlist_refresh_run(
                {
                    "batch_id": batch_id,
                    "address": "0x1111111111111111111111111111111111111111",
                    "label": "Alpha",
                    "source_reason": "latest_score>=60",
                    "old_score": 66,
                    "fresh_score": 62,
                    "score_delta": -4,
                    "recommendation": "watch",
                    "score_flags": ["unit"],
                    "applied_caps": ["cap"],
                }
            )
            store.finish_watchlist_refresh_batch(
                batch_id,
                "done",
                {"total": 1, "attempted": 1, "succeeded": 1, "failed": 0, "watch_count": 1},
                {"sent": True, "serverchan_code": 0},
            )
            store.close()
            (latest_dir / "latest_summary.json").write_text(
                json.dumps({"summary": {"attempted": 1}, "rows": [{"address": "0x1111111111111111111111111111111111111111"}]}),
                encoding="utf-8",
            )
            (latest_dir / "latest_summary.csv").write_text("address,label\n0x1,Alpha\n", encoding="utf-8-sig")

            with (
                patch.object(dashboard_server, "ROOT", root),
                patch.object(dashboard_server, "read_watchlist_process_state", return_value={"running": False}),
            ):
                summary = dashboard_server.watchlist_refresh_summary({"data_dir": "auto_screen_data", "state_db": "auto_screen_data/state.sqlite3"})
                csv_text = dashboard_server.watchlist_refresh_csv({"data_dir": "auto_screen_data"})

            self.assertEqual(summary["latest_batch"]["status"], "done")
            self.assertEqual(summary["latest_batch"]["summary"]["watch_count"], 1)
            self.assertEqual(summary["runs"][0]["score_flags"], ["unit"])
            self.assertEqual(summary["runs"][0]["applied_caps"], ["cap"])
            self.assertIn("0x1,Alpha", csv_text)

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

    def test_autostart_auto_screen_honors_env_flag(self) -> None:
        with (
            patch.dict(os.environ, {"PM_AUTOSTART_SCAN": "1"}, clear=False),
            patch.object(dashboard_server, "read_process_state", return_value={"running": False}),
            patch.object(dashboard_server, "launch_auto_screen", return_value={"started": True, "pid": 1234}) as launch,
        ):
            result = dashboard_server.autostart_auto_screen_if_requested()

        self.assertTrue(result["autostart"])
        self.assertEqual(result["pid"], 1234)
        launch.assert_called_once_with(["run"], "run")

    def test_autostart_auto_screen_stays_disabled_by_default(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(dashboard_server, "launch_auto_screen") as launch,
        ):
            result = dashboard_server.autostart_auto_screen_if_requested()

        self.assertFalse(result["autostart"])
        self.assertEqual(result["reason"], "disabled")
        launch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
