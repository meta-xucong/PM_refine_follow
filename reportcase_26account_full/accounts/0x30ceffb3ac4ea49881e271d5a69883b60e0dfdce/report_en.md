# AshleySchaeffer

## Account Identity (Manual Verification First)
- Display name: `AshleySchaeffer`
- Account address: `0x30ceffb3ac4ea49881e271d5a69883b60e0dfdce`
- Source pseudonym: `Gloomy-Date`
- Source profile name: `AshleySchaeffer`
- Source local name: `account_26`

## 1. Executive Conclusion
Calibrated decision score is 39.28 (anchor-referenced), decision: not_recommended. Primary sector exposure: sports, geopolitics. Strengths: deployable event breadth, contained multi-market weighted risk. Key risks: exclusive concurrent-leg risk, non-copyable token-fast exposure, dual-side condition buying. Hard blacklist themes: win, draw, end, chelsea, barcelona. Soft blacklist themes: golden, knights, morocco, ecuador, vit. Whitelist themes: france. Risk gate is active, so broad-copy mode is disabled. Severe-risk gate is active; low-score scenarios are forced to not_recommended. PnL curve tag: long_and_recent_weak. This account is not recommended as a primary copy-trading source; only rare manual picks may be considered.

## 2. Decision Snapshot
- decision: `not_recommended`
- final_score (decision basis): `39.280000`
- raw_score: `15.430000`
- anchored_score: `39.280000`
- delta_vs_anchor_60: `-20.720000`
- delta_vs_anchor_raw: `-31.880000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. Behavior Interpretation
- Observed 4373 trades across 31 active trading days in the analysis window.
- PnL curve shapes: all-time=volatile_up, 30d=insufficient_data, 7d=insufficient_data.
- Dominant sector themes: sports, geopolitics.

## 4. Copy-Trading Strengths
- Nested concurrent behavior remains relatively contained.
- Weighted multi-market structure risk is controlled.
- Topic supply is broad enough for selective deployment.
- Operational whitelist themes: france.

## 5. Copy-Trading Risks
- High dual-side condition activity, which is often difficult to mirror in copy-trading.
- Elevated non-copyable token-fast BUY ratio, suggesting execution-dependent edge.
- Meaningful exclusive concurrent-leg behavior (multi-leg overlap in mutually exclusive markets).
- Risk gate is triggered, so broad-copy mode is disabled and only strict filtering is allowed.
- Severe-risk gate is triggered; poor setups are automatically classified as not recommended.
- Hard blacklist themes to avoid: win, draw, end, chelsea, barcelona, sabres.
- Soft blacklist themes requiring stricter triggers: golden, knights, morocco, ecuador, vit, ria.

## 6. Sector and Keyword Filters
### Sector Tags
- sports
- geopolitics

### Whitelist Keywords
- france

### Hard Blacklist Keywords
- win
- draw
- end
- chelsea
- barcelona
- sabres
- hurricanes
- united
- blue
- jackets
- red
- bruins

### Soft Blacklist Keywords
- golden
- knights
- morocco
- ecuador
- vit
- ria
- athletic

## 7. Account Overview
- analysis_window: `2026-03-11 19:16:23 UTC -> 2026-04-10 03:10:47 UTC`
- trade_rows_used: `4373`
- total_buy_usdc: `350401.129641`
- total_sell_usdc: `283928.376464`
- traded_markets_count_api: `822`
- position_value_api: `24.949400`

## 8. Core Metrics
- dual_side_buy_usdc_ratio: `88.48%`
- dual_side_buy_usdc_ratio_1h: `48.58%`
- token_fast_20m_buy_usdc_ratio: `69.63%`
- noncopyable_token_fast_buy_ratio: `48.71%`
- noncopyable_token_fast_sell_ratio: `64.99%`
- noncopyable_token_fast_token_ratio: `31.40%`
- event_rebalance_20m_event_ratio: `41.62%`
- exclusive_concurrent_leg_ratio: `32.34%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `11.53%`
- deployable_event_equivalent: `30.000000`
- deployable_event_density: `1.022863`
- active_trading_days: `31.000000`
- trade_count: `4373.000000`
- avg_trades_per_active_day: `141.064516`

## 9. PnL Curve Evaluation
- all_time_shape: `volatile_up`
- all_time_score: `6`
- d30_shape: `insufficient_data`
- d30_score: `0`
- d7_shape: `insufficient_data`
- d7_score: `0`
- pnl_tag: `long_and_recent_weak`

## 10. Score Breakdown
- copyability_score: `0`
- deployability_score: `20`
- multi_market_structure_score: `7.440000`
- pnl_curve_stability_score: `5.000000`
- risk_penalty_adjustment: `-17.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. Data Quality and Assumptions
- Risk gate triggered; decision cannot be broad-copy and requires strict blacklist filtering
- Severe risk gate triggered; score threshold for not_recommended is tightened
- Severe risk gate + low calibrated score -> not_recommended
