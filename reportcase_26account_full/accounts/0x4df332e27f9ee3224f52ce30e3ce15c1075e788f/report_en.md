# Far-Precipitation

## Account Identity (Manual Verification First)
- Display name: `Far-Precipitation`
- Account address: `0x4df332e27f9ee3224f52ce30e3ce15c1075e788f`
- Source pseudonym: `Far-Precipitation`
- Source profile name: `SunlineTicker`
- Source local name: `account_4`

## 1. Executive Conclusion
Calibrated decision score is 29.25 (anchor-referenced), decision: not_recommended. Primary sector exposure: sports. Strengths: deployable event breadth, low non-copyable token-fast ratio. Key risks: exclusive concurrent-leg risk, dual-side condition buying. Hard blacklist themes: spread, pistons, rockets, knicks, warriors. Soft blacklist themes: gujarat, titans, grand, prix, city. Whitelist themes: rajasthan, royals, lucknow, giants, sunrisers. Risk gate is active, so broad-copy mode is disabled. Severe-risk gate is active; low-score scenarios are forced to not_recommended. PnL curve tag: long_and_recent_weak. This account is not recommended as a primary copy-trading source; only rare manual picks may be considered.

## 2. Decision Snapshot
- decision: `not_recommended`
- final_score (decision basis): `29.250000`
- raw_score: `0`
- anchored_score: `29.250000`
- delta_vs_anchor_60: `-30.750000`
- delta_vs_anchor_raw: `-47.310000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. Behavior Interpretation
- Observed 13509 trades across 30 active trading days in the analysis window.
- PnL curve shapes: all-time=down, 30d=insufficient_data, 7d=insufficient_data.
- Dominant sector themes: sports.

## 4. Copy-Trading Strengths
- Low non-copyable token-fast BUY ratio.
- Nested concurrent behavior remains relatively contained.
- Topic supply is broad enough for selective deployment.
- Operational whitelist themes: rajasthan, royals, lucknow, giants, sunrisers, hyderabad.

## 5. Copy-Trading Risks
- High dual-side condition activity, which is often difficult to mirror in copy-trading.
- Meaningful exclusive concurrent-leg behavior (multi-leg overlap in mutually exclusive markets).
- Weighted multi-market risk is elevated.
- Risk gate is triggered, so broad-copy mode is disabled and only strict filtering is allowed.
- Severe-risk gate is triggered; poor setups are automatically classified as not recommended.
- All-time PnL profile is not strongly upward, reducing confidence in persistent edge.
- Hard blacklist themes to avoid: spread, pistons, rockets, knicks, warriors, kings.
- Soft blacklist themes requiring stricter triggers: gujarat, titans, grand, prix, city, manchester.

## 6. Sector and Keyword Filters
### Sector Tags
- sports

### Whitelist Keywords
- rajasthan
- royals
- lucknow
- giants
- sunrisers
- hyderabad
- madrid
- club
- atl
- tico
- bucharest
- daniel

### Hard Blacklist Keywords
- spread
- pistons
- rockets
- knicks
- warriors
- kings
- hornets
- ers
- timberwolves
- lakers
- league
- spurs

### Soft Blacklist Keywords
- gujarat
- titans
- grand
- prix
- city
- manchester
- aberg
- ludvig
- glimt
- bod
- zverev
- women

## 7. Account Overview
- analysis_window: `2026-03-11 19:11:41 UTC -> 2026-04-10 18:25:15 UTC`
- trade_rows_used: `13509`
- total_buy_usdc: `2555234.489308`
- total_sell_usdc: `0`
- traded_markets_count_api: `8887`
- position_value_api: `48833.368900`

## 8. Core Metrics
- dual_side_buy_usdc_ratio: `67.59%`
- dual_side_buy_usdc_ratio_1h: `42.91%`
- token_fast_20m_buy_usdc_ratio: `0.00%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `n/a`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `90.90%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `82.08%`
- deployable_event_equivalent: `135.500000`
- deployable_event_density: `4.521527`
- active_trading_days: `30.000000`
- trade_count: `13509.000000`
- avg_trades_per_active_day: `450.300000`

## 9. PnL Curve Evaluation
- all_time_shape: `down`
- all_time_score: `-10`
- d30_shape: `insufficient_data`
- d30_score: `0`
- d7_shape: `insufficient_data`
- d7_score: `0`
- pnl_tag: `long_and_recent_weak`

## 10. Score Breakdown
- copyability_score: `0`
- deployability_score: `20`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `-8.330000`
- risk_penalty_adjustment: `-24.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. Data Quality and Assumptions
- Risk gate triggered; decision cannot be broad-copy and requires strict blacklist filtering
- Severe risk gate triggered; score threshold for not_recommended is tightened
- Severe risk gate + low calibrated score -> not_recommended
- Calibrated score below 32 -> not_recommended floor
- No matched SELL inventory found; holding-time metrics unavailable
