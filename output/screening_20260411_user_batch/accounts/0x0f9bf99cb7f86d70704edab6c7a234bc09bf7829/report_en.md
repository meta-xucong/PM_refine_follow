# Rare-Growth

## Account Identity (Manual Verification First)
- Display name: `Rare-Growth`
- Account address: `0x0f9bf99cb7f86d70704edab6c7a234bc09bf7829`
- Source pseudonym: `Rare-Growth`
- Source profile name: `linghujunlan`
- Source local name: `account_2`

## 1. Executive Conclusion
Calibrated decision score is 48.01 (anchor-referenced), decision: not_recommended. Primary sector exposure: geopolitics, sports. Strengths: deployable event breadth, contained multi-market weighted risk, low non-copyable token-fast ratio. Key risks: exclusive concurrent-leg risk. Hard blacklist themes: lol, esports, bo5, first, stand. Soft blacklist themes: win, nba, mvp, gilgeous-alexander, shai. Whitelist themes: taiwan, invade, china, end, lyon. Risk gate is active, so broad-copy mode is disabled. Severe-risk gate is active; low-score scenarios are forced to not_recommended. PnL curve tag: long_and_recent_weak. This account is not recommended as a primary copy-trading source; only rare manual picks may be considered.

## 2. Decision Snapshot
- decision: `not_recommended`
- final_score (decision basis): `48.010000`
- raw_score: `28.870000`
- anchored_score: `48.010000`
- delta_vs_anchor_60: `-11.990000`
- delta_vs_anchor_raw: `-18.440000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. Behavior Interpretation
- Observed 166 trades across 17 active trading days in the analysis window.
- Low-frequency cap is active at 64, reflecting constrained copy capacity.
- PnL curve shapes: all-time=smooth_up, 30d=insufficient_data, 7d=insufficient_data.
- Dominant sector themes: geopolitics, sports.

## 4. Copy-Trading Strengths
- Low non-copyable token-fast BUY ratio.
- Nested concurrent behavior remains relatively contained.
- Weighted multi-market structure risk is controlled.
- All-time PnL profile is smooth-up, supporting strategy consistency.
- Operational whitelist themes: taiwan, invade, china, end, lyon.

## 5. Copy-Trading Risks
- Meaningful exclusive concurrent-leg behavior (multi-leg overlap in mutually exclusive markets).
- Risk gate is triggered, so broad-copy mode is disabled and only strict filtering is allowed.
- Severe-risk gate is triggered; poor setups are automatically classified as not recommended.
- Frequency/deployability constraints limit practical copy capacity.
- Hard blacklist themes to avoid: lol, esports, bo5, first, stand, bnk.
- Soft blacklist themes requiring stricter triggers: win, nba, mvp, gilgeous-alexander, shai.

## 6. Sector and Keyword Filters
### Sector Tags
- geopolitics
- sports

### Whitelist Keywords
- taiwan
- invade
- china
- end
- lyon

### Hard Blacklist Keywords
- lol
- esports
- bo5
- first
- stand
- bnk
- fearx
- group
- bilibili
- game
- gaming
- winner

### Soft Blacklist Keywords
- win
- nba
- mvp
- gilgeous-alexander
- shai

## 7. Account Overview
- analysis_window: `2026-03-13 06:49:37 UTC -> 2026-04-09 04:02:07 UTC`
- trade_rows_used: `166`
- total_buy_usdc: `38847.159899`
- total_sell_usdc: `18910.264120`
- traded_markets_count_api: `261`
- position_value_api: `49368.274100`

## 8. Core Metrics
- dual_side_buy_usdc_ratio: `14.91%`
- dual_side_buy_usdc_ratio_1h: `0.79%`
- token_fast_20m_buy_usdc_ratio: `0.75%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `0.00%`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `7.14%`
- exclusive_concurrent_leg_ratio: `76.64%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `11.04%`
- deployable_event_equivalent: `9.500000`
- deployable_event_density: `0.353374`
- active_trading_days: `17.000000`
- trade_count: `166.000000`
- avg_trades_per_active_day: `9.764706`

## 9. PnL Curve Evaluation
- all_time_shape: `smooth_up`
- all_time_score: `12`
- d30_shape: `insufficient_data`
- d30_score: `0`
- d7_shape: `insufficient_data`
- d7_score: `0`
- pnl_tag: `long_and_recent_weak`

## 10. Score Breakdown
- copyability_score: `6.880000`
- deployability_score: `20`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `9.990000`
- risk_penalty_adjustment: `-8.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `64`

## 11. Data Quality and Assumptions
- Risk gate triggered; decision cannot be broad-copy and requires strict blacklist filtering
- Severe risk gate triggered; score threshold for not_recommended is tightened
- Severe risk gate + low calibrated score -> not_recommended
