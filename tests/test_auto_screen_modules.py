from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from auto_screen import scheduler
from auto_screen.config import load_config
from auto_screen.excel_store import ExcelStore
from auto_screen.leaderboard_scanner import scan_candidates
from auto_screen.models import AccountCandidate, PrefilterResult, ScoringResult
from auto_screen.notifier import format_alert_batch, format_candidate_message, send_serverchan
from auto_screen.official_sources import scan_candidates as scan_official_candidates
from auto_screen.prefilter import prefilter_account
from auto_screen.progress import ProgressReporter
from auto_screen.state_store import StateStore


class FakeClient:
    def __init__(self):
        self.calls = []

    def get(self, path, params):
        self.calls.append((path, dict(params)))
        offset = params.get("offset", 0)
        if offset > 0:
            return []
        return [
            {
                "rank": 1,
                "proxyWallet": "0x1111111111111111111111111111111111111111",
                "name": "Alpha",
                "pnl": 1000,
            }
        ]

    def fetch_activity(self, user, limit=300, offset=0, extra=None):
        return [
            {"timestamp": 1700000000 + i, "type": "TRADE"}
            for i in range(limit)
        ]


class FakeCappedLeaderboardClient:
    def __init__(self):
        self.calls = []

    def get(self, path, params):
        self.calls.append((path, dict(params)))
        offset = int(params.get("offset", 0))
        pages = {
            0: [
                {"rank": 1, "proxyWallet": "0x1111111111111111111111111111111111111111", "pnl": 100},
                {"rank": 2, "proxyWallet": "0x2222222222222222222222222222222222222222", "pnl": 90},
            ],
            2: [
                {"rank": 3, "proxyWallet": "0x3333333333333333333333333333333333333333", "pnl": 80},
                {"rank": 4, "proxyWallet": "0x4444444444444444444444444444444444444444", "pnl": 70},
            ],
            4: [
                {"rank": 3, "proxyWallet": "0x5555555555555555555555555555555555555555", "pnl": 60},
                {"rank": 4, "proxyWallet": "0x6666666666666666666666666666666666666666", "pnl": 50},
            ],
        }
        return pages.get(offset, [])


class FakeOfficialDataClient:
    def __init__(self):
        self.trade_calls = []
        self.holder_calls = []

    def fetch_trades(self, params):
        self.trade_calls.append(dict(params))
        return [
            {
                "proxyWallet": "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "name": "TradeAlpha",
                "size": 120,
                "price": 0.5,
                "conditionId": params["market"],
                "slug": "official-market",
            },
            {
                "proxyWallet": "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "pseudonym": "TradeBeta",
                "size": 80,
                "price": 0.75,
                "conditionId": params["market"],
                "slug": "official-market",
            },
        ]

    def fetch_holders(self, params):
        self.holder_calls.append(dict(params))
        return [
            {
                "token": "token-1",
                "holders": [
                    {
                        "proxyWallet": "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                        "name": "TradeAlpha",
                        "amount": 2000,
                    },
                    {
                        "proxyWallet": "0xcccccccccccccccccccccccccccccccccccccccc",
                        "pseudonym": "HolderGamma",
                        "amount": 300,
                    },
                ],
            }
        ]


class FakeGammaClient:
    def fetch_markets(self, params):
        return [
            {
                "conditionId": "0x1111111111111111111111111111111111111111111111111111111111111111",
                "slug": "official-market",
                "question": "Official market?",
                "volume24hr": "250000",
                "liquidity": "5000",
                "enableOrderBook": True,
            }
        ]


class AutoScreenModuleTests(unittest.TestCase):
    def test_load_config_merges_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(json.dumps({"scan": {"max_rank": 123}}), encoding="utf-8")
            cfg = load_config(path)
            self.assertEqual(cfg["scan"]["max_rank"], 123)
            self.assertIn("prefilter", cfg)
            self.assertEqual(cfg["scoring"]["alert_threshold"], 50)

    def test_leaderboard_scanner_merges_candidate_context(self):
        cfg = load_config(None)
        cfg["leaderboard"]["shards"] = [{"name": "month_pnl", "params": {"period": "month"}}]
        progress = []
        candidates = scan_candidates(cfg, FakeClient(), limit=1, progress_callback=progress.append)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].address, "0x1111111111111111111111111111111111111111")
        self.assertIn("month_pnl", candidates[0].source_keys)
        self.assertGreater(candidates[0].discovery_score, 0)
        self.assertEqual(progress[0]["shard"], "month_pnl")
        self.assertEqual(progress[0]["unique_candidates"], 1)
        self.assertEqual(progress[0]["new_candidates"], 1)

    def test_leaderboard_scanner_detects_api_rank_cap_and_skips_capped_page(self):
        cfg = load_config(None)
        cfg["scan"]["max_rank"] = 100
        cfg["scan"]["page_limit"] = 2
        cfg["scan"]["leaderboard_progress_pages"] = 1
        cfg["leaderboard"]["shards"] = [{"name": "month_pnl", "params": {"period": "month"}}]
        progress = []
        client = FakeCappedLeaderboardClient()

        candidates = scan_candidates(cfg, client, progress_callback=progress.append)

        self.assertEqual([call[1]["offset"] for call in client.calls], [0, 2, 4])
        self.assertEqual(len(candidates), 4)
        self.assertNotIn("0x5555555555555555555555555555555555555555", {c.address for c in candidates})
        self.assertTrue(progress[-1]["api_cap_detected"])
        self.assertEqual(progress[-1]["api_cap_rank"], 4)
        self.assertEqual(progress[-1]["early_stop_reason"], "api_rank_cap")

    def test_official_sources_add_trade_and_holder_candidates(self):
        cfg = load_config(None)
        cfg["candidate_sources"]["leaderboard_enabled"] = False
        cfg["candidate_sources"]["market_discovery"]["limit"] = 1
        cfg["candidate_sources"]["market_trades"]["markets_limit"] = 1
        cfg["candidate_sources"]["holders"]["markets_limit"] = 1
        progress = []

        with patch("auto_screen.official_sources.GammaApiClient", return_value=FakeGammaClient()):
            candidates = scan_official_candidates(cfg, FakeOfficialDataClient(), progress_callback=progress.append)

        by_address = {candidate.address: candidate for candidate in candidates}
        self.assertIn("0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", by_address)
        self.assertIn("0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", by_address)
        self.assertIn("0xcccccccccccccccccccccccccccccccccccccccc", by_address)
        alpha = by_address["0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]
        self.assertEqual(alpha.source_keys, ["holders", "market_trades"])
        self.assertEqual(alpha.leaderboard_context["official_source_count"], 2)
        self.assertGreater(alpha.leaderboard_context["official_trade_usdc"], 0)
        self.assertGreater(alpha.leaderboard_context["official_holder_balance"], 0)
        self.assertIn("official_trades", {item["source_type"] for item in progress})
        self.assertIn("official_holders", {item["source_type"] for item in progress})

    def test_prefilter_detects_hft(self):
        cfg = load_config(None)
        cfg["prefilter"]["skip_avg_trades_per_day"] = 10
        candidate = AccountCandidate(address="0x1111111111111111111111111111111111111111")
        result = prefilter_account(candidate, FakeClient(), cfg)
        self.assertFalse(result.passed)
        self.assertEqual(result.reason, "hft_suspected_prefilter")

    def test_state_store_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StateStore(Path(tmp) / "state.sqlite3")
            first_cycle = store.start_cycle()
            second_cycle = store.start_cycle()
            candidate = AccountCandidate(address="0x1111111111111111111111111111111111111111", discovery_score=10)
            store.upsert_candidate(candidate)
            self.assertEqual(len(store.pending_candidates(10)), 1)
            store.set_candidate_status(candidate.address, "scored")
            self.assertEqual(store.status()["candidate_counts"]["scored"], 1)
            cycles = store.conn.execute("SELECT id, status FROM cycles ORDER BY id").fetchall()
            self.assertEqual(first_cycle, cycles[0]["id"])
            self.assertEqual(second_cycle, cycles[1]["id"])
            self.assertEqual(cycles[0]["status"], "interrupted")
            self.assertEqual(cycles[1]["status"], "running")
            store.close()

    def test_state_store_marks_seen_before_candidates_for_score_refresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StateStore(Path(tmp) / "state.sqlite3")
            address = "0x1111111111111111111111111111111111111111"
            first = AccountCandidate(address=address, display_name="Alpha", best_rank=3, discovery_score=10)
            store.upsert_candidate(first)
            store.set_candidate_status(address, "push_watchlist")

            second = AccountCandidate(
                address=address,
                display_name="Alpha",
                best_rank=1,
                discovery_score=99,
                leaderboard_context={"month_pnl_rank": 1},
            )
            summary = store.upsert_candidates([second], status="pending")
            row = store.conn.execute("SELECT status, leaderboard_context FROM candidates WHERE address=?", (address,)).fetchone()
            pending = store.pending_candidates(10)
            store.close()

            context = json.loads(row["leaderboard_context"])
            self.assertEqual(summary["refresh_score"], 1)
            self.assertEqual(row["status"], "refresh_score")
            self.assertTrue(context["seen_before"])
            self.assertEqual(context["scan_prompt"], "刷新分数")
            self.assertEqual(context["previous_status"], "push_watchlist")
            self.assertEqual(pending[0]["address"], address)

    def test_state_store_tracks_pending_alert_pushes(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StateStore(Path(tmp) / "state.sqlite3")
            alert_ids = [
                store.record_alert(
                    f"0x{i:040x}",
                    50 + i,
                    "C",
                    f"Polymarket候选 C | {50 + i} | A{i}",
                    "结论: selective_copying_only\n自动动作: push_watchlist",
                    push_status="pending",
                )
                for i in range(1, 3)
            ]
            self.assertEqual(store.pending_alert_push_count(), 2)
            pending = store.pending_alerts_for_push(10)
            self.assertEqual([row["id"] for row in pending], alert_ids)
            store.mark_alert_push_result(alert_ids, "batch-1", {"sent": True, "serverchan_code": 0})
            self.assertEqual(store.pending_alert_push_count(), 0)
            rows = store.conn.execute("SELECT push_status, push_batch_id FROM alerts ORDER BY id").fetchall()
            store.close()
            self.assertEqual([row["push_status"] for row in rows], ["sent", "sent"])
            self.assertEqual({row["push_batch_id"] for row in rows}, {"batch-1"})

    def test_state_store_marks_legacy_alerts_sent_on_migration(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.sqlite3"
            conn = sqlite3.connect(path)
            conn.execute(
                """
                CREATE TABLE alerts (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  address TEXT NOT NULL,
                  final_score REAL,
                  alert_grade TEXT,
                  title TEXT,
                  message TEXT,
                  created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                INSERT INTO alerts(address, final_score, alert_grade, title, message, created_at)
                VALUES ('0x1', 50, 'C', 'old', 'old', '2026-01-01T00:00:00+00:00')
                """
            )
            conn.commit()
            conn.close()

            store = StateStore(path)
            row = store.conn.execute("SELECT push_status FROM alerts").fetchone()
            pending = store.pending_alert_push_count()
            store.close()
            self.assertEqual(row["push_status"], "sent")
            self.assertEqual(pending, 0)

    def test_state_store_archives_pending_alerts_at_or_below_score_threshold(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StateStore(Path(tmp) / "state.sqlite3")
            store.record_alert("0x1111111111111111111111111111111111111111", 50, "C", "low", "low", push_status="pending")
            store.record_alert("0x2222222222222222222222222222222222222222", 50.01, "C", "ok", "ok", push_status="pending")
            archived = store.archive_pending_alerts_at_or_below_score(50, "archived_below_alert_threshold")
            rows = [dict(row) for row in store.conn.execute("SELECT address, push_status FROM alerts ORDER BY id")]
            store.close()

            self.assertEqual(archived, 1)
            self.assertEqual(rows[0]["push_status"], "archived")
            self.assertEqual(rows[1]["push_status"], "pending")

    def _run_alert_batch_scenario(self, root: Path, candidate_count: int):
        cfg = load_config(None)
        cfg["data_dir"] = str(root / "data")
        cfg["state_db"] = str(root / "state.sqlite3")
        cfg["excel_path"] = str(root / "candidates.xlsx")
        cfg["progress_path"] = str(root / "progress.json")
        cfg["scan"]["process_batch_size"] = 4
        cfg["scan"]["process_all_candidates_per_cycle"] = True
        cfg["serverchan"]["batch_size"] = 10
        candidates = [
            AccountCandidate(address=f"0x{i:040x}", display_name=f"A{i}", discovery_score=100 - i)
            for i in range(1, candidate_count + 1)
        ]
        reporter = ProgressReporter(root / "progress.json", emit_log=False)

        def fake_score(address, *_args):
            return ScoringResult(
                address=address,
                final_score=55,
                decision="selective_copying_only",
                alert_grade="C",
                auto_action="push_watchlist",
                analysis_path=str(root / "analysis.json"),
                payload={
                    "account_address": address,
                    "account_label": address,
                    "final_score": 55,
                    "decision": "selective_copying_only",
                    "alert_grade": "C",
                    "auto_action": "push_watchlist",
                    "score_flags": ["unit_test"],
                    "score_breakdown_v3": {
                        "account_total_pnl": 1000,
                        "account_age_days": 400,
                        "pnl_smoothness_adjustment": 2,
                        "lifetime_activity_adjustment": 1,
                    },
                },
            )

        with (
            patch.object(scheduler, "scan_candidates", return_value=candidates),
            patch.object(scheduler, "prefilter_account", side_effect=lambda c, *_: PrefilterResult(c.address, True, "passed")),
            patch.object(scheduler, "collect_account_files", return_value=(root / "trades.csv", root / "summary.json")),
            patch.object(scheduler, "score_account", side_effect=fake_score),
            patch.object(
                scheduler,
                "send_serverchan",
                return_value={"sent": True, "status_code": 200, "serverchan_code": 0, "serverchan_error": "SUCCESS"},
            ) as send,
        ):
            stats = scheduler.run_once(cfg, dry_run_alerts=False, reporter=reporter)

        store = StateStore(root / "state.sqlite3")
        rows = [dict(row) for row in store.conn.execute("SELECT * FROM alerts ORDER BY id").fetchall()]
        store.close()
        return stats, send, rows

    def test_run_once_waits_until_serverchan_batch_is_full(self):
        with tempfile.TemporaryDirectory() as tmp:
            stats, send, rows = self._run_alert_batch_scenario(Path(tmp), 9)
            self.assertEqual(stats["alerts"], 9)
            self.assertEqual(send.call_count, 0)
            self.assertEqual({row["push_status"] for row in rows}, {"pending"})

    def test_run_once_sends_serverchan_batch_at_ten_alerts(self):
        with tempfile.TemporaryDirectory() as tmp:
            stats, send, rows = self._run_alert_batch_scenario(Path(tmp), 10)
            self.assertEqual(stats["alerts"], 10)
            self.assertEqual(send.call_count, 1)
            title, message, _cfg = send.call_args.args
            self.assertIn("10 个", title)
            self.assertIn("本批已凑满 10 个可关注账号", message)
            self.assertIn("## 10 个地址", message)
            for i in range(1, 11):
                self.assertIn(f"0x{i:040x}", message)
                self.assertIn(f"0x{i:040x} ｜ 分数：55.00 分｜评级：C级", message)
            self.assertIn("只适合筛选后谨慎跟单", message)
            self.assertEqual({row["push_status"] for row in rows}, {"sent"})
            self.assertEqual(len({row["push_batch_id"] for row in rows}), 1)

    def test_run_once_uses_configured_candidate_discovery_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = load_config(None)
            cfg["data_dir"] = str(root / "data")
            cfg["state_db"] = str(root / "state.sqlite3")
            cfg["excel_path"] = str(root / "candidates.xlsx")
            cfg["progress_path"] = str(root / "progress.json")
            cfg["scan"]["candidate_discovery_limit"] = 123
            reporter = ProgressReporter(root / "progress.json", emit_log=False)

            with patch.object(scheduler, "scan_candidates", return_value=[]) as scan:
                stats = scheduler.run_once(cfg, dry_run_alerts=True, reporter=reporter)

            self.assertEqual(stats["scanned"], 0)
            self.assertEqual(scan.call_args.kwargs["limit"], 123)

    def test_run_once_does_not_queue_serverchan_alert_at_or_below_threshold(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = load_config(None)
            cfg["data_dir"] = str(root / "data")
            cfg["state_db"] = str(root / "state.sqlite3")
            cfg["excel_path"] = str(root / "candidates.xlsx")
            cfg["progress_path"] = str(root / "progress.json")
            cfg["scan"]["process_batch_size"] = 1
            candidate = AccountCandidate(address="0x1111111111111111111111111111111111111111", display_name="A1", discovery_score=99)
            reporter = ProgressReporter(root / "progress.json", emit_log=False)

            def fake_score(address, *_args):
                return ScoringResult(
                    address=address,
                    final_score=48,
                    decision="selective_copying_only",
                    alert_grade="C",
                    auto_action="push_watchlist",
                    analysis_path=str(root / "analysis.json"),
                    payload={
                        "account_address": address,
                        "account_label": address,
                        "final_score": 48,
                        "decision": "selective_copying_only",
                        "alert_grade": "C",
                        "auto_action": "push_watchlist",
                    },
                )

            with (
                patch.object(scheduler, "scan_candidates", return_value=[candidate]),
                patch.object(scheduler, "prefilter_account", return_value=PrefilterResult(candidate.address, True, "passed")),
                patch.object(scheduler, "collect_account_files", return_value=(root / "trades.csv", root / "summary.json")),
                patch.object(scheduler, "score_account", side_effect=fake_score),
                patch.object(scheduler, "send_serverchan") as send,
            ):
                stats = scheduler.run_once(cfg, dry_run_alerts=False, reporter=reporter)

            store = StateStore(root / "state.sqlite3")
            alert_count = store.conn.execute("SELECT COUNT(*) AS n FROM alerts").fetchone()["n"]
            store.close()

            self.assertEqual(stats["alerts"], 0)
            self.assertEqual(alert_count, 0)
            self.assertEqual(send.call_count, 0)

    def test_run_once_archives_legacy_pending_alerts_before_batching(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = load_config(None)
            cfg["data_dir"] = str(root / "data")
            cfg["state_db"] = str(root / "state.sqlite3")
            cfg["excel_path"] = str(root / "candidates.xlsx")
            cfg["progress_path"] = str(root / "progress.json")
            cfg["scan"]["process_batch_size"] = 1
            cfg["scan"]["process_all_candidates_per_cycle"] = True
            cfg["serverchan"]["batch_size"] = 10
            store = StateStore(root / "state.sqlite3")
            for index in range(9):
                store.record_alert(
                    f"0x{index + 1:040x}",
                    50,
                    "C",
                    "Polymarket候选 C | 50 | legacy",
                    "结论: selective_copying_only\n自动动作: push_watchlist",
                    push_status="pending",
                )
            store.close()
            candidate = AccountCandidate(address="0x9999999999999999999999999999999999999999", discovery_score=99)
            reporter = ProgressReporter(root / "progress.json", emit_log=False)

            def fake_score(address, *_args):
                return ScoringResult(
                    address=address,
                    final_score=55,
                    decision="selective_copying_only",
                    alert_grade="C",
                    auto_action="push_watchlist",
                    analysis_path=str(root / "analysis.json"),
                    payload={
                        "account_address": address,
                        "account_label": address,
                        "final_score": 55,
                        "decision": "selective_copying_only",
                        "alert_grade": "C",
                        "auto_action": "push_watchlist",
                        "score_flags": ["unit_test"],
                        "score_breakdown_v3": {
                            "account_total_pnl": 1000,
                            "account_age_days": 400,
                            "pnl_smoothness_adjustment": 2,
                            "lifetime_activity_adjustment": 1,
                        },
                    },
                )

            with (
                patch.object(scheduler, "scan_candidates", return_value=[candidate]),
                patch.object(scheduler, "prefilter_account", return_value=PrefilterResult(candidate.address, True, "passed")),
                patch.object(scheduler, "collect_account_files", return_value=(root / "trades.csv", root / "summary.json")),
                patch.object(scheduler, "score_account", side_effect=fake_score),
                patch.object(
                    scheduler,
                    "send_serverchan",
                    return_value={"sent": True, "status_code": 200, "serverchan_code": 0, "serverchan_error": "SUCCESS"},
                ) as send,
            ):
                stats = scheduler.run_once(cfg, dry_run_alerts=False, reporter=reporter)

            self.assertEqual(stats["alerts"], 1)
            self.assertEqual(send.call_count, 0)
            store = StateStore(root / "state.sqlite3")
            counts = {
                row["push_status"]: row["n"]
                for row in store.conn.execute("SELECT push_status, count(*) AS n FROM alerts GROUP BY push_status")
            }
            store.close()
            self.assertEqual(counts["archived"], 9)
            self.assertEqual(counts["pending"], 1)

    def test_run_once_defers_single_account_collection_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = load_config(None)
            cfg["data_dir"] = str(root / "data")
            cfg["state_db"] = str(root / "state.sqlite3")
            cfg["excel_path"] = str(root / "candidates.xlsx")
            cfg["progress_path"] = str(root / "progress.json")
            cfg["scan"]["process_batch_size"] = 1
            candidate = AccountCandidate(
                address="0x1111111111111111111111111111111111111111",
                display_name="Alpha",
                discovery_score=10,
            )
            reporter = ProgressReporter(root / "progress.json", emit_log=False)

            with (
                patch.object(scheduler, "scan_candidates", return_value=[candidate]),
                patch.object(
                    scheduler,
                    "prefilter_account",
                    return_value=PrefilterResult(candidate.address, True, "passed"),
                ),
                patch.object(scheduler, "collect_account_files", side_effect=RuntimeError("temporary summary failure")),
            ):
                stats = scheduler.run_once(cfg, dry_run_alerts=True, reporter=reporter)

            self.assertEqual(stats["skipped"], 1)
            self.assertEqual(stats["processed"], 0)
            store = StateStore(root / "state.sqlite3")
            row = store.conn.execute("SELECT status FROM candidates WHERE address=?", (candidate.address,)).fetchone()
            run = store.conn.execute("SELECT status, reason FROM runs ORDER BY id DESC LIMIT 1").fetchone()
            cycle = store.conn.execute("SELECT status FROM cycles ORDER BY id DESC LIMIT 1").fetchone()
            store.close()
            self.assertEqual(row["status"], "defer_recheck")
            self.assertEqual(run["status"], "account_failed")
            self.assertIn("temporary summary failure", run["reason"])
            self.assertEqual(cycle["status"], "done")

    def test_run_once_process_all_candidates_across_batches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = load_config(None)
            cfg["data_dir"] = str(root / "data")
            cfg["state_db"] = str(root / "state.sqlite3")
            cfg["excel_path"] = str(root / "candidates.xlsx")
            cfg["progress_path"] = str(root / "progress.json")
            cfg["scan"]["process_batch_size"] = 2
            cfg["scan"]["process_all_candidates_per_cycle"] = True
            candidates = [
                AccountCandidate(address=f"0x{i:040x}", display_name=f"A{i}", discovery_score=10 - i)
                for i in range(1, 4)
            ]
            reporter = ProgressReporter(root / "progress.json", emit_log=False)

            def fake_score(address, *_args):
                return ScoringResult(
                    address=address,
                    final_score=10,
                    decision="not_recommended",
                    alert_grade="none",
                    auto_action="store_only",
                    analysis_path=str(root / "analysis.json"),
                    payload={
                        "account_address": address,
                        "account_label": address,
                        "final_score": 10,
                        "decision": "not_recommended",
                        "alert_grade": "none",
                        "auto_action": "store_only",
                    },
                )

            with (
                patch.object(scheduler, "scan_candidates", return_value=candidates),
                patch.object(scheduler, "prefilter_account", side_effect=lambda c, *_: PrefilterResult(c.address, True, "passed")),
                patch.object(scheduler, "collect_account_files", return_value=(root / "trades.csv", root / "summary.json")) as collect,
                patch.object(scheduler, "score_account", side_effect=fake_score),
            ):
                stats = scheduler.run_once(cfg, dry_run_alerts=True, reporter=reporter)

            self.assertEqual(stats["processed"], 3)
            self.assertEqual(stats["skipped"], 0)
            self.assertEqual(collect.call_count, 3)
            progress = json.loads((root / "progress.json").read_text(encoding="utf-8"))
            self.assertEqual(progress["stats"]["processed"], 3)
            store = StateStore(root / "state.sqlite3")
            counts = store.status()["candidate_counts"]
            store.close()
            self.assertEqual(counts["store_only"], 3)

    def test_full_cycle_does_not_retry_deferred_account_until_next_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = load_config(None)
            cfg["data_dir"] = str(root / "data")
            cfg["state_db"] = str(root / "state.sqlite3")
            cfg["excel_path"] = str(root / "candidates.xlsx")
            cfg["progress_path"] = str(root / "progress.json")
            cfg["scan"]["process_batch_size"] = 1
            cfg["scan"]["process_all_candidates_per_cycle"] = True
            failed = AccountCandidate(address="0x1111111111111111111111111111111111111111", discovery_score=10)
            ok = AccountCandidate(address="0x2222222222222222222222222222222222222222", discovery_score=9)
            reporter = ProgressReporter(root / "progress.json", emit_log=False)

            def fake_collect(address, *_args):
                if address == failed.address:
                    raise RuntimeError("temporary api failure")
                return root / "trades.csv", root / "summary.json"

            def fake_score(address, *_args):
                return ScoringResult(
                    address=address,
                    final_score=10,
                    decision="not_recommended",
                    alert_grade="none",
                    auto_action="store_only",
                    analysis_path=str(root / "analysis.json"),
                    payload={
                        "account_address": address,
                        "account_label": address,
                        "final_score": 10,
                        "decision": "not_recommended",
                        "alert_grade": "none",
                        "auto_action": "store_only",
                    },
                )

            with (
                patch.object(scheduler, "scan_candidates", return_value=[failed, ok]),
                patch.object(scheduler, "prefilter_account", side_effect=lambda c, *_: PrefilterResult(c.address, True, "passed")),
                patch.object(scheduler, "collect_account_files", side_effect=fake_collect) as collect,
                patch.object(scheduler, "score_account", side_effect=fake_score),
            ):
                stats = scheduler.run_once(cfg, dry_run_alerts=True, reporter=reporter)

            self.assertEqual(stats["processed"], 1)
            self.assertEqual(stats["skipped"], 1)
            self.assertEqual(collect.call_count, 2)
            store = StateStore(root / "state.sqlite3")
            rows = {
                row["address"]: row["status"]
                for row in store.conn.execute("SELECT address, status FROM candidates").fetchall()
            }
            store.close()
            self.assertEqual(rows[failed.address], "defer_recheck")
            self.assertEqual(rows[ok.address], "store_only")

    def test_run_once_cools_down_after_repeated_transient_api_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = load_config(None)
            cfg["data_dir"] = str(root / "data")
            cfg["state_db"] = str(root / "state.sqlite3")
            cfg["excel_path"] = str(root / "candidates.xlsx")
            cfg["progress_path"] = str(root / "progress.json")
            cfg["scan"]["process_batch_size"] = 3
            cfg["scan"]["process_all_candidates_per_cycle"] = True
            cfg["scan"]["api_error_cooldown_threshold"] = 2
            cfg["scan"]["api_error_cooldown_seconds"] = 0.01
            failed_1 = AccountCandidate(address="0x1111111111111111111111111111111111111111", discovery_score=10)
            failed_2 = AccountCandidate(address="0x2222222222222222222222222222222222222222", discovery_score=9)
            ok = AccountCandidate(address="0x3333333333333333333333333333333333333333", discovery_score=8)
            reporter = ProgressReporter(root / "progress.json", emit_log=False)

            transient = RuntimeError(
                "Request failed after 4 retries: "
                "https://data-api.polymarket.com/activity?user=0xabc&limit=500&offset=0"
            )

            def fake_collect(address, *_args):
                if address in {failed_1.address, failed_2.address}:
                    raise transient
                return root / "trades.csv", root / "summary.json"

            def fake_score(address, *_args):
                return ScoringResult(
                    address=address,
                    final_score=10,
                    decision="not_recommended",
                    alert_grade="none",
                    auto_action="store_only",
                    analysis_path=str(root / "analysis.json"),
                    payload={
                        "account_address": address,
                        "account_label": address,
                        "final_score": 10,
                        "decision": "not_recommended",
                        "alert_grade": "none",
                        "auto_action": "store_only",
                    },
                )

            with (
                patch.object(scheduler, "scan_candidates", return_value=[failed_1, failed_2, ok]),
                patch.object(scheduler, "prefilter_account", side_effect=lambda c, *_: PrefilterResult(c.address, True, "passed")),
                patch.object(scheduler, "collect_account_files", side_effect=fake_collect),
                patch.object(scheduler, "score_account", side_effect=fake_score),
                patch.object(scheduler.time, "sleep") as sleep,
            ):
                stats = scheduler.run_once(cfg, dry_run_alerts=True, reporter=reporter)

            sleep.assert_called_once_with(0.01)
            self.assertEqual(stats["processed"], 1)
            self.assertEqual(stats["skipped"], 2)
            progress = json.loads((root / "progress.json").read_text(encoding="utf-8"))
            phases = [item["phase"] for item in progress["history"]]
            self.assertIn("api_cooldown", phases)

    def test_progress_reporter_writes_current_event_and_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "progress.json"
            reporter = ProgressReporter(path, emit_log=False)
            reporter.update("scanning_leaderboard", "scan", cycle_id=1)
            reporter.update("processing_batch", "batch", cycle_id=1, current_index=2, batch_total=5)
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["phase"], "processing_batch")
            self.assertEqual(data["phase_label"], "准备处理候选")
            self.assertEqual(data["current_index"], 2)
            self.assertEqual(len(data["history"]), 2)

    def test_excel_store_writes_xlsx_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.xlsx"
            store = ExcelStore(path)
            store.append("alerts", {"account": "0x1", "score": 50})
            self.assertTrue(path.exists())
            with zipfile.ZipFile(path) as zf:
                self.assertIn("xl/workbook.xml", zf.namelist())
                self.assertIn("xl/worksheets/sheet1.xml", zf.namelist())

    def test_notifier_dry_run(self):
        analysis = {
            "account_address": "0x1111111111111111111111111111111111111111",
            "account_label": "Alpha",
            "final_score": 66,
            "decision": "selective_copying_only",
            "alert_grade": "B",
            "auto_action": "push_selective_candidate",
            "score_flags": ["multi_category_hit"],
        }
        title, message = format_candidate_message(analysis)
        self.assertIn("Alpha", title)
        self.assertIn("B级", title)
        self.assertIn("一句话结论", message)
        self.assertIn("系统评级：B级", message)
        self.assertIn("系统建议", message)
        self.assertNotIn("final_score", message)
        self.assertNotIn("auto_action", message)
        self.assertNotIn("selective_copying_only", message)
        result = send_serverchan(title, message, {"enabled": True, "dry_run": True})
        self.assertEqual(result["reason"], "dry_run")

    def test_notifier_formats_alert_batch(self):
        rows = [
            {
                "address": "0x1111111111111111111111111111111111111111",
                "final_score": 55,
                "alert_grade": "C",
                "title": "Polymarket候选 C | 55 | Alpha",
                "message": (
                    "结论: selective_copying_only\n"
                    "自动动作: push_watchlist\n"
                    "总PnL: 1000\n"
                    "账号年龄天数: 400\n"
                    "数据质量: 8\n"
                    "收益质量: 20\n"
                    "跟单容量: 5\n"
                    "标记: multi_category_hit"
                ),
            }
            for _ in range(10)
        ]
        title, message = format_alert_batch(rows)
        self.assertIn("10 个", title)
        self.assertIn("0x1111111111111111111111111111111111111111 ｜ 分数：55.00 分｜评级：C级", message)
        self.assertIn("Alpha", message)
        self.assertIn("评级：C级", message)
        self.assertIn("只适合筛选后谨慎跟单", message)
        self.assertIn("覆盖多个题材", message)
        self.assertNotIn("selective_copying_only", message)
        self.assertNotIn("push_watchlist", message)
        self.assertNotIn("评级：观察名单", message)

    def test_notifier_parses_serverchan_success(self):
        class FakeResponse:
            status_code = 200
            text = "{}"

            def json(self):
                return {"code": 0, "data": {"error": "SUCCESS"}}

        with (
            patch.dict("os.environ", {"TEST_SENDKEY": "SCTFAKE"}),
            patch("auto_screen.notifier.requests.post", return_value=FakeResponse()),
        ):
            result = send_serverchan("title", "message", {"enabled": True, "sendkey_env": "TEST_SENDKEY"})

        self.assertTrue(result["sent"])
        self.assertEqual(result["serverchan_code"], 0)
        self.assertEqual(result["serverchan_error"], "SUCCESS")

    def test_notifier_reports_serverchan_business_error(self):
        class FakeResponse:
            status_code = 200
            text = "{}"

            def json(self):
                return {"code": 1, "data": {"error": "BAD_SENDKEY"}}

        with (
            patch.dict("os.environ", {"TEST_SENDKEY": "SCTFAKE"}),
            patch("auto_screen.notifier.requests.post", return_value=FakeResponse()),
        ):
            result = send_serverchan("title", "message", {"enabled": True, "sendkey_env": "TEST_SENDKEY"})

        self.assertFalse(result["sent"])
        self.assertEqual(result["reason"], "serverchan_error")
        self.assertEqual(result["serverchan_error"], "BAD_SENDKEY")


if __name__ == "__main__":
    unittest.main()
