from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZE_SCRIPT = ROOT / "skill" / "polymarket-account-review-skill" / "scripts" / "analyze_account.py"
ANCHOR_FILE = ROOT / "skill" / "polymarket-account-review-skill" / "baseline" / "baseline_anchor_auto_v3.json"


def load_analyze_module():
    spec = importlib.util.spec_from_file_location("analyze_account_under_test", ANALYZE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def base_metrics() -> dict:
    return {
        "dual_side_buy_usdc_ratio": 0.0,
        "dual_side_buy_usdc_ratio_1h": 0.0,
        "exclusive_concurrent_leg_ratio": 0.0,
        "nested_concurrent_leg_ratio": 0.0,
        "weighted_multi_market_risk_ratio": 0.0,
        "noncopyable_token_fast_buy_ratio": 0.0,
        "noncopyable_token_fast_sell_ratio": 0.0,
        "noncopyable_token_fast_token_ratio": 0.0,
        "deployable_event_equivalent": 20.0,
        "deployable_event_density": 1.0,
        "event_rebalance_20m_event_ratio": 0.0,
        "trade_count": 300.0,
        "active_trading_days": 20.0,
        "active_day_ratio": 0.8,
        "avg_trades_per_active_day": 15.0,
        "unknown_multi_market_buy_ratio": 0.0,
        "exclusive_sequential_switch_count": 0,
        "nested_sequential_roll_count": 0,
        "top1_event_buy_ratio": 0.10,
        "top3_event_buy_ratio": 0.30,
        "total_buy_usdc": 10000.0,
        "total_sell_usdc": 8000.0,
        "median_buy_notional": 100.0,
        "p90_buy_notional": 500.0,
        "tiny_trade_buy_ratio": 0.0,
        "extreme_price_trade_ratio": 0.0,
        "sell_usdc_ratio_within_20m": 0.0,
    }


def good_api_summary() -> dict:
    return {
        "summary": {
            "positions_value": 100.0,
            "traded_markets": 50,
            "closed_positions_recent_coverage_days": 35,
            "closed_positions_incomplete": False,
            "closed_positions_recent_incomplete": False,
            "closed_positions_realized_pnl_total": 5000.0,
            "account_total_pnl": 5000.0,
            "closed_positions_realized_pnl_30d": 900.0,
            "closed_positions_realized_pnl_7d": 120.0,
            "account_age_days": 600,
            "closed_position_active_days": 120,
            "closed_position_active_months": 12,
            "account_lifetime_months": 20,
            "closed_position_active_month_ratio": 0.86,
            "closed_position_active_days_30d": 18,
        },
        "snapshot": {},
        "snapshot_error": None,
        "pnl_curve": {
            "all_time": {
                "shape": "smooth_up",
                "score": 12,
                "total_return": 5000,
                "max_drawdown": 100,
                "drawdown_to_return_ratio": 0.02,
                "daily_volatility_to_return_ratio": 0.03,
                "largest_daily_abs_move_to_return_ratio": 0.08,
                "largest_daily_gain_share": 0.12,
            },
            "d30": {"shape": "smooth_up", "score": 6, "total_return": 900, "max_drawdown": 100},
            "d7": {"shape": "smooth_up", "score": 2, "total_return": 120, "max_drawdown": 20},
            "summary_tag": "long_mid_short_strong",
        },
    }


class AutoV3ScoringTests(unittest.TestCase):
    def setUp(self):
        self.analyze = load_analyze_module()

    def test_anchor_file_exists_and_has_v3_raw_base(self):
        data = json.loads(ANCHOR_FILE.read_text(encoding="utf-8"))
        self.assertEqual(data["anchor_account"], "0x39d0f1dca6fb7e5514858c1a337724a426764fe8")
        self.assertIn("raw_base_score_v3", data)
        self.assertNotEqual(data["raw_base_score_v3"], data.get("legacy_raw_base_score"))

    def test_data_quality_cap_blocks_alert_when_activity_incomplete(self):
        metrics = base_metrics()
        metrics["activity_incomplete"] = True
        result = self.analyze.compute_scores_auto_v3(metrics, good_api_summary(), None, {}, 50.0, 60.0, None)
        self.assertLess(result["data_quality_score"], 4)
        self.assertLessEqual(result["final_score"], 39)
        self.assertEqual(result["alert_grade"], "none")
        self.assertIn("activity_incomplete", result["score_flags"])

    def test_high_frequency_skip_and_caps(self):
        metrics = base_metrics()
        metrics["avg_trades_per_active_day"] = 700.0
        result = self.analyze.compute_scores_auto_v3(metrics, good_api_summary(), None, {}, 50.0, 60.0, None)
        self.assertEqual(result["auto_action"], "skip")
        self.assertIn("hft_suspected", result["score_flags"])
        self.assertLessEqual(result["final_score"], 64)

    def test_negative_total_pnl_is_hard_rejected(self):
        summary = good_api_summary()
        summary["summary"]["account_total_pnl"] = -1.0
        summary["summary"]["closed_positions_realized_pnl_total"] = -1.0
        result = self.analyze.compute_scores_auto_v3(base_metrics(), summary, None, {}, 50.0, 60.0, None)
        self.assertEqual(result["decision"], "not_recommended")
        self.assertEqual(result["alert_grade"], "none")
        self.assertEqual(result["auto_action"], "skip")
        self.assertLessEqual(result["final_score"], 39)
        self.assertIn("negative_total_pnl", result["score_flags"])

    def test_account_age_under_nine_months_is_hard_rejected(self):
        summary = good_api_summary()
        summary["summary"]["account_age_days"] = 120
        result = self.analyze.compute_scores_auto_v3(base_metrics(), summary, None, {}, 50.0, 60.0, None)
        self.assertEqual(result["auto_action"], "skip")
        self.assertEqual(result["alert_grade"], "none")
        self.assertLessEqual(result["final_score"], 39)
        self.assertIn("account_age_under_9m", result["score_flags"])

    def test_smooth_long_term_activity_adds_score(self):
        result = self.analyze.compute_scores_auto_v3(base_metrics(), good_api_summary(), None, {}, 50.0, 60.0, None)
        breakdown = result["score_breakdown_v3"]
        self.assertGreater(breakdown["pnl_smoothness_adjustment"], 0)
        self.assertGreater(breakdown["lifetime_activity_adjustment"], 0)
        self.assertIn("long_consistent_activity", result["score_flags"])

    def test_spiky_pnl_and_dormant_recent_spike_are_penalized(self):
        summary = good_api_summary()
        summary["summary"].update(
            {
                "account_age_days": 520,
                "closed_position_active_days": 12,
                "closed_position_active_months": 2,
                "account_lifetime_months": 18,
                "closed_position_active_month_ratio": 0.11,
                "closed_position_active_days_30d": 10,
            }
        )
        summary["pnl_curve"]["all_time"].update(
            {
                "shape": "volatile_up",
                "max_drawdown": 3800,
                "drawdown_to_return_ratio": 0.76,
                "daily_volatility_to_return_ratio": 0.42,
                "largest_daily_abs_move_to_return_ratio": 0.72,
                "largest_daily_gain_share": 0.78,
            }
        )
        result = self.analyze.compute_scores_auto_v3(base_metrics(), summary, None, {}, 50.0, 60.0, None)
        breakdown = result["score_breakdown_v3"]
        self.assertLess(breakdown["pnl_smoothness_adjustment"], 0)
        self.assertLess(breakdown["lifetime_activity_adjustment"], 0)
        self.assertIn("pnl_spiky", result["score_flags"])
        self.assertIn("dormant_recent_spike", result["score_flags"])

    def test_severe_risk_gate_blocks_alert_push_even_with_high_score(self):
        metrics = base_metrics()
        metrics["dual_side_buy_usdc_ratio"] = 0.70
        result = self.analyze.compute_scores_auto_v3(metrics, good_api_summary(), None, {}, 50.0, 60.0, None)
        self.assertEqual(result["decision"], "not_recommended")
        self.assertEqual(result["alert_grade"], "none")
        self.assertEqual(result["auto_action"], "skip")
        self.assertIn("severe_risk_gate", result["score_flags"])

    def test_alert_grade_is_capped_to_c_when_data_quality_is_low(self):
        metrics = base_metrics()
        summary = good_api_summary()
        summary["summary"]["positions_value"] = None
        summary["summary"]["closed_positions_recent_coverage_days"] = 0
        summary["summary"]["closed_positions_recent_incomplete"] = True
        result = self.analyze.compute_scores_auto_v3(metrics, summary, None, {}, 50.0, 60.0, None)
        self.assertLess(result["data_quality_score"], 6)
        self.assertIn(result["alert_grade"], {"C", "none"})

    def test_analyze_cli_can_emit_v2_compatible_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "trades.csv"
            out_path = Path(tmp) / "analysis.json"
            summary_path = Path(tmp) / "summary.json"
            address = "0x1111111111111111111111111111111111111111"
            csv_path.write_text(
                "account_address,timestamp,side,conditionId,eventSlug,outcome,size,usdcSize,price,type\n"
                f"{address},1700000000,BUY,c1,e1,Yes,100,50,0.5,TRADE\n"
                f"{address},1700003600,SELL,c1,e1,Yes,100,80,0.8,TRADE\n",
                encoding="utf-8",
            )
            summary_path.write_text(json.dumps(good_api_summary()), encoding="utf-8")
            args = self.analyze.parse_args.__globals__["argparse"].Namespace(
                csv=str(csv_path),
                account=address,
                api_summary=str(summary_path),
                score_version="v2_2",
                leaderboard_context=None,
                allow_live_api_fallback=False,
                live_api_timeout=1,
                live_api_retries=0,
                anchor_file=None,
                auto_v3_anchor_file=None,
                disable_anchor=True,
                output_json=str(out_path),
            )
            result = self.analyze.analyze(args)
            self.assertNotIn("score_breakdown_v3", result["score_breakdown"])
            self.assertEqual(result["score_version"], "v2_2")


if __name__ == "__main__":
    unittest.main()
