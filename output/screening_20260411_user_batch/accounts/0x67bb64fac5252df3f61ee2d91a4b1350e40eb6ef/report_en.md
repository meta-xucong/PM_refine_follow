# Ideal-Copying

## Account Identity (Manual Verification First)
- Display name: `Ideal-Copying`
- Account address: `0x67bb64fac5252df3f61ee2d91a4b1350e40eb6ef`
- Source pseudonym: `Ideal-Copying`
- Source profile name: `Blueberry1337`
- Source local name: `account_12`

## 1. Executive Conclusion
Calibrated decision score is 45.35 (anchor-referenced), decision: not_recommended. Primary sector exposure: sports. Strengths: deployable event breadth, low non-copyable token-fast ratio. Key risks: exclusive concurrent-leg risk. Hard blacklist themes: counter-strike, map, winner, bo3, themongolz. Soft blacklist themes: hawks, game. Whitelist themes: lakers, pistons, celtics, thunder, clippers. Risk gate is active, so broad-copy mode is disabled. Severe-risk gate is active; low-score scenarios are forced to not_recommended. PnL curve tag: long_and_recent_weak. This account is not recommended as a primary copy-trading source; only rare manual picks may be considered.

## 2. Decision Snapshot
- decision: `not_recommended`
- final_score (decision basis): `45.350000`
- raw_score: `24.770000`
- anchored_score: `45.350000`
- delta_vs_anchor_60: `-14.650000`
- delta_vs_anchor_raw: `-22.540000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. Behavior Interpretation
- Observed 7556 trades across 31 active trading days in the analysis window.
- PnL curve shapes: all-time=volatile_up, 30d=insufficient_data, 7d=insufficient_data.
- Dominant sector themes: sports.

## 4. Copy-Trading Strengths
- Low dual-side condition exposure, indicating cleaner directional expression.
- Low non-copyable token-fast BUY ratio.
- Nested concurrent behavior remains relatively contained.
- Topic supply is broad enough for selective deployment.
- Operational whitelist themes: lakers, pistons, celtics, thunder, clippers, timberwolves.

## 5. Copy-Trading Risks
- Meaningful exclusive concurrent-leg behavior (multi-leg overlap in mutually exclusive markets).
- Risk gate is triggered, so broad-copy mode is disabled and only strict filtering is allowed.
- Severe-risk gate is triggered; poor setups are automatically classified as not recommended.
- Hard blacklist themes to avoid: counter-strike, map, winner, bo3, themongolz, parivision.
- Soft blacklist themes requiring stricter triggers: hawks, game.

## 6. Sector and Keyword Filters
### Sector Tags
- sports

### Whitelist Keywords
- lakers
- pistons
- celtics
- thunder
- clippers
- timberwolves
- magic
- warriors
- rockets
- heat
- suns
- pacers

### Hard Blacklist Keywords
- counter-strike
- map
- winner
- bo3
- themongolz
- parivision
- vincere
- natus
- esports
- aurora
- gaming
- bucharest

### Soft Blacklist Keywords
- hawks
- game

## 7. Account Overview
- analysis_window: `2026-03-12 16:04:53 UTC -> 2026-04-11 14:55:09 UTC`
- trade_rows_used: `7556`
- total_buy_usdc: `2897312.275838`
- total_sell_usdc: `185698.113391`
- traded_markets_count_api: `787`
- position_value_api: `193196.346300`

## 8. Core Metrics
- dual_side_buy_usdc_ratio: `8.91%`
- dual_side_buy_usdc_ratio_1h: `0.52%`
- token_fast_20m_buy_usdc_ratio: `0.46%`
- noncopyable_token_fast_buy_ratio: `0.46%`
- noncopyable_token_fast_sell_ratio: `2.32%`
- noncopyable_token_fast_token_ratio: `0.47%`
- event_rebalance_20m_event_ratio: `3.94%`
- exclusive_concurrent_leg_ratio: `66.90%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `34.89%`
- deployable_event_equivalent: `77.000000`
- deployable_event_density: `2.570816`
- active_trading_days: `31.000000`
- trade_count: `7556.000000`
- avg_trades_per_active_day: `243.741935`

## 9. PnL Curve Evaluation
- all_time_shape: `volatile_up`
- all_time_score: `6`
- d30_shape: `insufficient_data`
- d30_score: `0`
- d7_shape: `insufficient_data`
- d7_score: `0`
- pnl_tag: `long_and_recent_weak`

## 10. Score Breakdown
- copyability_score: `7.780000`
- deployability_score: `20`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `5.000000`
- risk_penalty_adjustment: `-8.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. Data Quality and Assumptions
- Risk gate triggered; decision cannot be broad-copy and requires strict blacklist filtering
- Severe risk gate triggered; score threshold for not_recommended is tightened
- Severe risk gate + low calibrated score -> not_recommended
