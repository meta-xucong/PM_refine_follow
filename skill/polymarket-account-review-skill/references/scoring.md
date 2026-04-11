# Scoring Rules (V2.2 Operational)

This file converts `polymarket_account_screening_standard_V2_2.md` into deterministic scoring logic.

## 1) Score Dimensions

Use the following five components:
- `copyability_score`: `0..35`
- `deployability_score`: `0..20`
- `multi_market_structure_score`: `0..20`
- `pnl_curve_stability_score`: `-22..+22` (scaled 3-window PnL component)
- `risk_penalty_adjustment`: `-30..0`

Raw total:
`raw_score = copyability + deployability + structure + pnl_curve + risk_penalty - concentration_penalty`

Clamp raw total to `0..100` before low-frequency caps.

## 2) Hard Exclusion Conditions

If any condition is true, decision cannot exceed `not_recommended` unless user explicitly requests manual override:
- `exclusive_concurrent_leg_ratio > 0.45`
- `nested_concurrent_leg_ratio > 0.60` and `event_rebalance_20m_event_ratio >= 0.20`
- `weighted_multi_market_risk_ratio > 0.60` and (`exclusive_concurrent_leg_ratio > 0.25` or `nested_concurrent_leg_ratio > 0.35`)
- `noncopyable_token_fast_buy_ratio > 0.30`
- `noncopyable_token_fast_sell_ratio > 0.70`
- `dual_side_buy_usdc_ratio > 0.45`
- `dual_side_buy_usdc_ratio_1h > 0.25`

## 3) Concentration Penalties

Apply after raw score computation:
- if `top1_event_buy_ratio > 0.50` and `deployable_event_equivalent < 5`: `+5` penalty
- if `top3_event_buy_ratio > 0.80` and `deployable_event_equivalent < 8`: `+5` penalty

`concentration_penalty` is subtracted from raw score.

## 4) Low-Frequency Caps

After penalties, apply minimum of relevant caps:
- if `deployable_event_equivalent < 3` OR `deployable_event_density < 0.10` OR `active_trading_days < 4` OR `trade_count < 40`: cap `50`
- else if `< 5` OR `< 0.17` OR `active_trading_days < 8` OR `trade_count < 100`: cap `58`
- else if `< 8` OR `< 0.26` OR `active_trading_days < 12` OR `trade_count < 180`: cap `66`

## 5) Decision Mapping

- Raw decision score (`final_score = raw_score`) is used for threshold mapping:
  - `>= 75`: `relative_copyable`
  - `60..74.99`: `selective_copying_only`
  - `< 60`: `not_recommended`

Anchor benchmark (reference-only):
- `60` equals frozen anchor account baseline:
  - `anchor_account = 0x39d0f1dca6fb7e5514858c1a337724a426764fe8`
  - `anchored_score = clamp(raw_score + score_offset, 0, 100)`
  - `score_offset = 60 - anchor_raw_base_score` (from frozen anchor file)
- `anchored_score` and `delta_vs_anchor_60` are for cross-run comparability, not for overriding low-frequency caps or decision thresholds.

## 5.2) PnL Confidence Scaling

PnL adjustment uses confidence scaling by available windows:
- available windows count excludes `unknown` and `insufficient_data`
- confidence factors:
  - `3 windows`: `1.00`
  - `2 windows`: `0.75`
  - `1 window`: `0.45`
  - `0 window`: `0.00`

Formula:
- `pnl_score = clamp((all_time_score + d30_score + d7_score) * 1.35 * pnl_confidence, -22, +22)`

## 5.1) Anchor Freeze Policy

- Anchor config is stored in `baseline/baseline_anchor.json`.
- Do not regenerate anchor by default.
- Regenerate only with explicit `--rebuild-anchor`.
- Every report must show:
  - `raw_score`
  - `anchored_score`
  - `delta_vs_anchor_60`
  - `anchor_version`

## 6) Missing Data Degrade Rules

- Missing SELL activity:
  - holding metrics become `null`
  - reduce `copyability_score` upper bound by `5`
- Missing token key (`asset` and no reliable fallback):
  - do not compute token-fast metrics
  - set `noncopyable_*` ratios to `null`
  - apply conservative `risk_penalty_adjustment -= 3`
- Missing API summary (value/traded/closed positions):
  - set `pnl_curve_stability_score = 0`
  - add caveat in report

## 7) Required Metrics for Final Score

Minimum required for final numeric score:
- `dual_side_buy_usdc_ratio`
- `exclusive_concurrent_leg_ratio`
- `nested_concurrent_leg_ratio`
- `weighted_multi_market_risk_ratio`
- `noncopyable_token_fast_buy_ratio`
- `deployable_event_equivalent`
- `deployable_event_density`

If fewer than 5 of these are available, output only qualitative decision.
