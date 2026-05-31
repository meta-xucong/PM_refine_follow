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


def daily_points_from_months(months: list[tuple[str, int, float]]) -> list[dict]:
    points: list[dict] = []
    cumulative = 0.0
    for month, days, pnl in months:
        year_text, month_text = month.split("-", 1)
        daily = pnl / max(days, 1)
        for index in range(days):
            day = min(index + 1, 28)
            cumulative += daily
            points.append(
                {
                    "date": f"{year_text}-{month_text}-{day:02d}",
                    "daily_realized_pnl": daily,
                    "cumulative_realized_pnl": cumulative,
                }
            )
    return points


class AutoV3ScoringTests(unittest.TestCase):
    def setUp(self):
        self.analyze = load_analyze_module()

    def test_keyword_profile_uses_event_slug_when_title_missing(self):
        rows = [{"eventSlug": "nba-nyk-cle-2026-05-25", "title": ""}]
        event_records = [{"eventSlug": "nba-nyk-cle-2026-05-25", "classification": "clean", "event_buy_usdc": 100.0}]
        event_buy_by_slug = {"nba-nyk-cle-2026-05-25": 100.0}
        profile = self.analyze.keyword_profile(rows, event_records, event_buy_by_slug)
        self.assertIn("sports", profile["sector_tags"])

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

    def test_late_activity_ramp_small_scale_is_capped_to_c(self):
        metrics = base_metrics()
        metrics["total_buy_usdc"] = 15000.0
        metrics["median_buy_notional"] = 10.0
        metrics["p90_buy_notional"] = 120.0
        summary = good_api_summary()
        summary["summary"].update(
            {
                "positions_value": 4000.0,
                "account_total_pnl": 2200.0,
                "closed_positions_realized_pnl_total": 2300.0,
                "account_age_days": 380,
                "closed_position_active_days": 27,
                "closed_position_active_months": 5,
                "account_lifetime_months": 13,
                "closed_position_active_month_ratio": 0.38,
                "closed_position_active_days_30d": 13,
                "closed_position_active_days_90d": 24,
                "closed_position_recent_90d_active_day_share": 0.89,
                "closed_positions_realized_pnl_30d": 5800.0,
                "closed_positions_realized_pnl_7d": 190.0,
            }
        )
        result = self.analyze.compute_scores_auto_v3(metrics, summary, None, {}, 50.0, 60.0, None)
        self.assertLessEqual(result["final_score"], 48)
        self.assertIn("late_activity_ramp", result["score_flags"])
        self.assertIn("capital_scale_small_48", result["score_flags"])
        self.assertIn(result["alert_grade"], {"C", "none"})

    def test_recent_loss_and_extreme_lifetime_drawdown_cap_score(self):
        summary = good_api_summary()
        summary["summary"].update(
            {
                "account_total_pnl": 19000.0,
                "closed_positions_realized_pnl_total": 19000.0,
                "closed_positions_realized_pnl_30d": 17000.0,
                "closed_positions_realized_pnl_7d": -3000.0,
                "account_age_days": 420,
                "closed_position_active_days": 18,
                "closed_position_active_months": 1,
                "account_lifetime_months": 14,
                "closed_position_active_month_ratio": 0.07,
                "closed_position_active_days_30d": 0,
                "closed_position_active_days_90d": 0,
            }
        )
        summary["pnl_curve"]["all_time"].update(
            {
                "shape": "volatile_up",
                "max_drawdown": 51300,
                "daily_volatility": 17860,
                "largest_daily_abs_move": 46930,
                "drawdown_to_return_ratio": 2.7,
                "daily_volatility_to_return_ratio": 0.94,
                "largest_daily_abs_move_to_return_ratio": 2.47,
            }
        )
        result = self.analyze.compute_scores_auto_v3(base_metrics(), summary, None, {}, 50.0, 60.0, None)
        self.assertLessEqual(result["final_score"], 52)
        self.assertNotEqual(result["alert_grade"], "B")
        self.assertIn("recent_7d_loss_material_55", result["score_flags"])
        self.assertIn("lifetime_drawdown_extreme_52", result["score_flags"])

    def test_closed_pnl_overstatement_is_capped_by_total_pnl_retention(self):
        metrics = base_metrics()
        metrics["total_buy_usdc"] = 102000.0
        summary = good_api_summary()
        summary["summary"].update(
            {
                "account_total_pnl": 15845.0,
                "closed_positions_realized_pnl_total": 158323.0,
                "open_positions_cash_pnl_sum": -137607.0,
                "open_positions_realized_pnl_sum": -4871.0,
                "closed_positions_realized_pnl_30d": 49452.0,
                "closed_positions_realized_pnl_7d": 9036.0,
                "positions_value": 13162.0,
                "account_age_days": 522,
                "closed_position_active_days": 363,
                "closed_position_active_months": 18,
                "account_lifetime_months": 18,
                "closed_position_active_month_ratio": 1.0,
                "closed_position_active_days_30d": 22,
                "closed_position_active_days_90d": 72,
            }
        )
        summary["pnl_curve"]["all_time"].update(
            {
                "shape": "smooth_up",
                "total_return": 159518.0,
                "max_drawdown": 5017.0,
                "daily_volatility": 1980.0,
                "largest_daily_abs_move": 14294.0,
                "drawdown_to_return_ratio": 0.03145,
                "daily_volatility_to_return_ratio": 0.0124,
                "largest_daily_abs_move_to_return_ratio": 0.0896,
            }
        )
        summary["pnl_curve"]["d30"].update({"total_return": 49452.0, "max_drawdown": 3363.0})
        summary["pnl_curve"]["d7"].update({"total_return": 10279.0, "max_drawdown": 887.0})

        result = self.analyze.compute_scores_auto_v3(metrics, summary, None, {}, 50.0, 60.0, None)
        breakdown = result["score_breakdown_v3"]

        self.assertLessEqual(result["final_score"], 45)
        self.assertLessEqual(result["pnl_quality_score"], 6)
        self.assertEqual(breakdown["pnl_ratio_base"], "account_total_pnl")
        self.assertGreater(breakdown["closed_to_total_pnl_multiplier"], 5)
        self.assertLess(breakdown["total_pnl_retention_ratio"], 0.2)
        self.assertGreater(breakdown["pnl_largest_daily_abs_move_to_return_ratio"], 0.8)
        self.assertIn("total_pnl_retention_low_45", result["score_flags"])
        self.assertIn("closed_pnl_overstates_total_45", result["score_flags"])
        self.assertNotIn("strong_recent_pnl", result["score_flags"])

    def test_recent_profit_concentration_is_capped_as_short_validated_track(self):
        metrics = base_metrics()
        metrics.update(
            {
                "dual_side_buy_usdc_ratio": 0.157589,
                "dual_side_buy_usdc_ratio_1h": 0.013087,
                "nested_concurrent_leg_ratio": 0.792045,
                "weighted_multi_market_risk_ratio": 0.30508,
                "noncopyable_token_fast_buy_ratio": 0.011427,
                "noncopyable_token_fast_sell_ratio": 0.031508,
                "noncopyable_token_fast_token_ratio": 0.02439,
                "deployable_event_equivalent": 85.5,
                "deployable_event_density": 2.861206,
                "event_rebalance_20m_event_ratio": 0.09322,
                "trade_count": 1707.0,
                "active_trading_days": 31.0,
                "avg_trades_per_active_day": 55.064516,
                "total_buy_usdc": 137402.910221,
                "total_sell_usdc": 102706.015268,
                "median_buy_notional": 96.045447,
                "p90_buy_notional": 242.666174,
                "extreme_price_trade_ratio": 0.039002,
            }
        )
        summary = good_api_summary()
        summary["summary"].update(
            {
                "positions_value": 28458.2815,
                "account_total_pnl": 18308.442308,
                "closed_positions_realized_pnl_total": 14834.097808,
                "open_positions_cash_pnl_sum": 3487.4587,
                "open_positions_realized_pnl_sum": -13.1142,
                "closed_positions_realized_pnl_30d": 6190.19607,
                "closed_positions_realized_pnl_7d": 2169.741635,
                "account_age_days": 343.293,
                "closed_position_active_days": 192,
                "closed_position_active_months": 8,
                "account_lifetime_months": 12,
                "closed_position_active_month_ratio": 0.666667,
                "closed_position_active_days_30d": 30,
                "closed_position_active_days_90d": 90,
                "closed_position_active_day_ratio_lifetime": 0.55814,
                "closed_position_recent_30d_active_day_share": 0.15625,
                "closed_position_recent_90d_active_day_share": 0.46875,
            }
        )
        summary["pnl_curve"]["all_time"].update(
            {
                "shape": "smooth_up",
                "total_return": 14836.305582,
                "max_drawdown": 4543.645281,
                "daily_volatility": 674.613764,
                "largest_daily_abs_move": 5521.296685,
                "largest_daily_gain_share": 0.165346,
            }
        )
        summary["pnl_curve"]["d30"].update({"shape": "volatile_up", "score": 2, "total_return": 4620.238323})
        summary["pnl_curve"]["d7"].update({"shape": "smooth_up", "score": 2, "total_return": 2103.342354})
        summary["pnl_curve"]["daily_points"] = daily_points_from_months(
            [
                ("2025-06", 8, -26.71),
                ("2025-07", 15, -4.32),
                ("2025-12", 20, -31.45),
                ("2026-01", 30, 80.39),
                ("2026-02", 28, -864.84),
                ("2026-03", 31, 2429.50),
                ("2026-04", 30, 7230.89),
                ("2026-05", 30, 6020.65),
            ]
        )
        anchor = {"target_anchor_score": 60, "raw_base_score_v3": 72.43, "calibration_scale": 0.65}

        result = self.analyze.compute_scores_auto_v3(metrics, summary, anchor, {}, 50.0, 60.0, None)
        breakdown = result["score_breakdown_v3"]

        self.assertLessEqual(result["final_score"], 55)
        self.assertIn("short_validated_alpha_track", result["score_flags"])
        self.assertIn("short_validated_alpha_track_55", result["score_flags"])
        self.assertNotIn("consistent_activity", result["score_flags"])
        self.assertEqual(breakdown["validated_profit_months"], 3)
        self.assertEqual(breakdown["pre_recent_validated_profit_months"], 0)
        self.assertGreaterEqual(breakdown["recent_90d_pnl_share"], 0.75)

    def test_distributed_validated_profit_track_is_not_capped(self):
        metrics = base_metrics()
        metrics.update(
            {
                "dual_side_buy_usdc_ratio": 0.011519,
                "nested_concurrent_leg_ratio": 0.636681,
                "weighted_multi_market_risk_ratio": 0.165393,
                "deployable_event_equivalent": 50.5,
                "deployable_event_density": 1.697865,
                "trade_count": 1054.0,
                "active_trading_days": 30.0,
                "avg_trades_per_active_day": 35.133333,
                "total_buy_usdc": 52206.293212,
                "median_buy_notional": 66.0,
                "p90_buy_notional": 108.45192,
                "extreme_price_trade_ratio": 0.093127,
            }
        )
        summary = good_api_summary()
        summary["summary"].update(
            {
                "positions_value": 15840.1478,
                "account_total_pnl": 9039.343002,
                "closed_positions_realized_pnl_total": 8398.780702,
                "closed_positions_realized_pnl_30d": 4742.768396,
                "closed_positions_realized_pnl_7d": 1376.616277,
                "account_age_days": 880.96,
                "closed_position_active_days": 235,
                "closed_position_active_months": 28,
                "account_lifetime_months": 29,
                "closed_position_active_month_ratio": 0.965517,
                "closed_position_active_days_30d": 28,
                "closed_position_active_days_90d": 70,
                "closed_position_active_day_ratio_lifetime": 0.26644,
                "closed_position_recent_90d_active_day_share": 0.297872,
            }
        )
        summary["pnl_curve"]["all_time"].update(
            {
                "shape": "volatile_up",
                "total_return": 8392.626181,
                "max_drawdown": 3416.966274,
                "daily_volatility": 398.903174,
                "largest_daily_abs_move": 2942.986307,
                "largest_daily_gain_share": 0.080537,
            }
        )
        summary["pnl_curve"]["daily_points"] = daily_points_from_months(
            [
                ("2025-10", 18, -79.29),
                ("2025-11", 15, 2925.33),
                ("2025-12", 17, -1871.61),
                ("2026-01", 21, 522.56),
                ("2026-02", 21, 1319.35),
                ("2026-03", 19, -1976.13),
                ("2026-04", 24, 506.06),
                ("2026-05", 28, 6365.98),
            ]
        )

        result = self.analyze.compute_scores_auto_v3(metrics, summary, None, {}, 50.0, 60.0, None)
        breakdown = result["score_breakdown_v3"]

        self.assertNotIn("short_validated_alpha_track", result["score_flags"])
        self.assertIn("long_consistent_activity", result["score_flags"])
        self.assertGreaterEqual(breakdown["validated_profit_months"], 5)
        self.assertLess(breakdown["recent_90d_pnl_share"], 0.75)

    def test_sports_concentration_with_short_track_record_is_hard_capped(self):
        metrics = base_metrics()
        metrics["sports_like_buy_ratio"] = 0.995
        metrics["sports_like_event_count"] = 50
        summary = good_api_summary()
        summary["summary"].update(
            {
                "account_age_days": 320,
                "closed_position_active_days": 35,
                "closed_position_active_months": 6,
                "account_lifetime_months": 11,
                "closed_position_active_month_ratio": 0.545455,
                "closed_position_active_days_30d": 12,
                "closed_position_active_days_90d": 12,
                "closed_position_recent_90d_active_day_share": 0.342857,
                "closed_positions_realized_pnl_30d": 1800.0,
                "closed_positions_realized_pnl_7d": 320.0,
            }
        )
        summary["pnl_curve"]["all_time"].update(
            {
                "shape": "smooth_up",
                "drawdown_to_return_ratio": 0.163124,
                "daily_volatility_to_return_ratio": 0.13,
                "largest_daily_abs_move_to_return_ratio": 0.34,
                "largest_daily_gain_share": 0.30,
            }
        )
        result = self.analyze.compute_scores_auto_v3(metrics, summary, None, {}, 50.0, 60.0, None)
        self.assertLessEqual(result["final_score"], 39)
        self.assertEqual(result["decision"], "not_recommended")
        self.assertEqual(result["alert_grade"], "none")
        self.assertIn("sports_concentration_unstable_39", result["score_flags"])

    def test_stable_moderate_scale_account_can_score_above_70_with_anchor(self):
        metrics = base_metrics()
        metrics["total_buy_usdc"] = 100000.0
        metrics["median_buy_notional"] = 120.0
        metrics["p90_buy_notional"] = 1200.0
        summary = good_api_summary()
        summary["summary"].update(
            {
                "positions_value": 70000.0,
                "account_total_pnl": 29000.0,
                "closed_positions_realized_pnl_total": 29000.0,
                "closed_positions_realized_pnl_30d": 6500.0,
                "closed_positions_realized_pnl_7d": 190.0,
                "account_age_days": 520,
                "closed_position_active_days": 110,
                "closed_position_active_months": 10,
                "account_lifetime_months": 18,
                "closed_position_active_month_ratio": 0.56,
            }
        )
        summary["pnl_curve"]["all_time"].update(
            {
                "shape": "smooth_up",
                "drawdown_to_return_ratio": 0.03,
                "daily_volatility_to_return_ratio": 0.11,
                "largest_daily_abs_move_to_return_ratio": 0.63,
                "largest_daily_gain_share": 0.60,
            }
        )
        anchor = {"target_anchor_score": 60, "raw_base_score_v3": 72.43, "calibration_scale": 0.65}
        result = self.analyze.compute_scores_auto_v3(metrics, summary, anchor, {}, 50.0, 60.0, None)
        self.assertGreater(result["final_score"], 70)
        self.assertEqual(result["alert_grade"], "A")
        self.assertNotIn("single_day_move_high_60", result["score_flags"])

    def test_alert_grade_follows_score_thresholds(self):
        self.assertEqual(self.analyze.alert_grade_from_score(70.01), "A")
        self.assertEqual(self.analyze.alert_grade_from_score(55.01), "B")
        self.assertEqual(self.analyze.alert_grade_from_score(45.01), "C")
        self.assertEqual(self.analyze.alert_grade_from_score(45.0), "none")

    def test_severe_risk_gate_blocks_alert_push_even_with_high_score(self):
        metrics = base_metrics()
        metrics["dual_side_buy_usdc_ratio"] = 0.70
        result = self.analyze.compute_scores_auto_v3(metrics, good_api_summary(), None, {}, 50.0, 60.0, None)
        self.assertEqual(result["decision"], "not_recommended")
        self.assertEqual(result["alert_grade"], "none")
        self.assertEqual(result["auto_action"], "skip")
        self.assertIn("severe_risk_gate", result["score_flags"])

    def test_material_dual_side_ratio_is_not_pushable(self):
        metrics = base_metrics()
        metrics["dual_side_buy_usdc_ratio"] = 0.26
        result = self.analyze.compute_scores_auto_v3(metrics, good_api_summary(), None, {}, 50.0, 60.0, None)
        self.assertLessEqual(result["final_score"], 50)
        self.assertEqual(result["alert_grade"], "C")
        self.assertIn("dual_side_material_50", result["score_flags"])
        self.assertIn("high_dual_side", result["score_flags"])

    def test_high_dual_side_ratio_is_capped_below_alert_grade(self):
        metrics = base_metrics()
        metrics["dual_side_buy_usdc_ratio"] = 0.35
        result = self.analyze.compute_scores_auto_v3(metrics, good_api_summary(), None, {}, 50.0, 60.0, None)
        self.assertLessEqual(result["final_score"], 45)
        self.assertEqual(result["alert_grade"], "none")
        self.assertIn("dual_side_high_45", result["score_flags"])
        self.assertIn("high_dual_side", result["score_flags"])

    def test_severe_dual_side_ratio_is_skipped(self):
        metrics = base_metrics()
        metrics["dual_side_buy_usdc_ratio"] = 0.50
        result = self.analyze.compute_scores_auto_v3(metrics, good_api_summary(), None, {}, 50.0, 60.0, None)
        self.assertLessEqual(result["final_score"], 39)
        self.assertEqual(result["decision"], "not_recommended")
        self.assertEqual(result["alert_grade"], "none")
        self.assertEqual(result["auto_action"], "skip")
        self.assertIn("dual_side_severe_39", result["score_flags"])
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
