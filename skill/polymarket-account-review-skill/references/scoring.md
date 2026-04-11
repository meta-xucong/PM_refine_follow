# Scoring Rules (V2.2 Operational, Anchored + Risk-Gated)

This file defines deterministic scoring logic for the skill.

## 1) Score Dimensions

Use five additive components plus concentration penalty:
- `copyability_score`: `0..35`
- `deployability_score`: `0..20`
- `multi_market_structure_score`: `0..20`
- `pnl_curve_stability_score`: `-28..+28`
- `risk_penalty_adjustment`: `-34..0`
- `concentration_penalty`: `0..15` (subtracted)

Raw total:
`raw_before_cap = copyability + deployability + structure + pnl_curve + risk_penalty - concentration_penalty`

Then clamp `raw_before_cap` to `0..100`.

## 2) Low-Frequency Caps

After raw total, apply cap tiers:
- tier 1 (`cap=48`): if `deployable_event_equivalent < 3` OR `deployable_event_density < 0.10` OR `active_trading_days < 4` OR `trade_count < 40`
- tier 2 (`cap=56`): else if `deployable_event_equivalent < 5` OR `deployable_event_density < 0.17` OR `active_trading_days < 8` OR `trade_count < 100`
- tier 3 (`cap=64`): else if `deployable_event_equivalent < 8` OR `deployable_event_density < 0.26` OR `active_trading_days < 12` OR `trade_count < 180`

`raw_score = min(raw_before_cap, low_frequency_cap)` when any cap applies.

## 3) Concentration Penalties

Apply after core scoring and before low-frequency caps:
- if `top1_event_buy_ratio > 0.50` and `deployable_event_equivalent < 5`: `+6` penalty
- if `top3_event_buy_ratio > 0.80` and `deployable_event_equivalent < 8`: `+6` penalty
- if `top1_event_buy_ratio > 0.65` and `deployable_event_equivalent < 8`: additional `+3` penalty

## 4) PnL Confidence Scaling

PnL contribution is confidence-weighted by available windows (`all_time`, `d30`, `d7`):
- available windows exclude `unknown` and `insufficient_data`
- confidence factors:
  - `3 windows`: `1.00`
  - `2 windows`: `0.75`
  - `1 window`: `0.45`
  - `0 window`: `0.00`

Formula:
`pnl_curve_stability_score = clamp((all_time_score + d30_score + d7_score) * 1.85 * pnl_confidence, -28, +28)`

## 5) Anchor Baseline Calibration

Anchor account:
- `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

Calibrated score:
- `anchored_score = clamp(60 + (raw_score - anchor_raw_base_score) * calibration_scale, 0, 100)`
- default `calibration_scale = 0.65` (stored in `baseline/baseline_anchor.json`)

Decision basis:
- `final_score = anchored_score`

## 6) Risk Gates (No Single Hard-Force Rule)

The system uses two risk gates:

### 6.1 Caution Risk Gate
Triggered when any is true:
- `exclusive_concurrent_leg_ratio > 0.45`
- `nested_concurrent_leg_ratio > 0.60` and `event_rebalance_20m_event_ratio >= 0.20`
- `weighted_multi_market_risk_ratio > 0.60` and (`exclusive_concurrent_leg_ratio > 0.25` or `nested_concurrent_leg_ratio > 0.35`)
- `noncopyable_token_fast_buy_ratio > 0.30`
- `noncopyable_token_fast_sell_ratio > 0.70`
- `dual_side_buy_usdc_ratio > 0.45`
- `dual_side_buy_usdc_ratio_1h > 0.25`

Effect:
- cannot remain in broad-copy mode; `relative_copyable` is downgraded to `selective_copying_only`.

### 6.2 Severe Risk Gate
Triggered when any is true:
- `exclusive_concurrent_leg_ratio > 0.62`
- `nested_concurrent_leg_ratio > 0.75` and `event_rebalance_20m_event_ratio >= 0.25`
- `weighted_multi_market_risk_ratio > 0.75` and (`exclusive_concurrent_leg_ratio > 0.35` or `nested_concurrent_leg_ratio > 0.50`)
- `noncopyable_token_fast_buy_ratio > 0.50`
- `noncopyable_token_fast_sell_ratio > 0.82`
- `dual_side_buy_usdc_ratio > 0.62`
- `dual_side_buy_usdc_ratio_1h > 0.38`

Effect:
- if `final_score < 55`, force `not_recommended`.

## 7) Decision Mapping

1. Initial mapping:
- `relative_copyable` if `final_score >= 78` and no caution gate and `pnl_curve_stability_score >= 2` and no strict low-frequency cap (`None` or `>=64`)
- `selective_copying_only` if `40 <= final_score < 78`
- `not_recommended` if `final_score < 40`

2. Gate/floor adjustments:
- caution gate downgrades `relative_copyable` to `selective_copying_only`
- severe gate + `final_score < 55` => `not_recommended`
- global floor: `final_score < 32` => `not_recommended`

Interpretation:
- `60` is baseline reference, not automatic "recommended".
- Most `40+` accounts should be operated in selective-copy mode with strict keyword filtering.

## 8) Keyword Blacklist Strengthening

Keyword classification uses weighted dirty ratio:
- `dirty_like_ratio = (dirty + 0.60 * semiclean) / total`
- `clean_like_ratio = (clean + 0.30 * semiclean) / total`

Rules:
- whitelist: `clean_like_ratio >= 0.68` and `dirty_like_ratio <= 0.22`
- hard blacklist: `dirty_like_ratio >= 0.62` OR (`dirty_ratio >= 0.50` and high importance)
- soft blacklist: `dirty_like_ratio >= 0.38`

Extra booster:
- keywords appearing in dirty events receive direct hard-blacklist boost.
- keywords appearing in semiclean events receive soft-blacklist boost.

## 9) Missing Data Degrade Rules

- Missing SELL matching:
  - holding-time metrics become `null`
  - report must state limitation
- Missing/incomplete API summary:
  - analysis first uses prefetched summary
  - if incomplete and live fallback enabled, fetch once live
  - if still missing, PnL contribution goes neutral and assumption is recorded
