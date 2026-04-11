# slimjoe

## Account Identity (Manual Verification First)
- Display name: `slimjoe`
- Account address: `0x5e3040eb55cb0f4f86eb0af40cb84c9d3585acbf`
- Source pseudonym: `Gargantuan-Heater`
- Source profile name: `slimjoe`
- Source local name: `account_29`

## 1. Executive Conclusion
Calibrated decision score is 41.59 (anchor-referenced), decision: not_recommended. Primary sector exposure: sports. Strengths: deployable event breadth, low non-copyable token-fast ratio. Key risks: exclusive concurrent-leg risk, nested concurrent-ladder risk, dual-side condition buying. Hard blacklist themes: set, spread, handicap, moneyline, open. Soft blacklist themes: madrid, halftime, red, city, real. Whitelist themes: win, liverpool, club, sharks, end. Risk gate is active, so broad-copy mode is disabled. Severe-risk gate is active; low-score scenarios are forced to not_recommended. PnL curve tag: long_and_recent_weak. This account is not recommended as a primary copy-trading source; only rare manual picks may be considered.

## 2. Decision Snapshot
- decision: `not_recommended`
- final_score (decision basis): `41.590000`
- raw_score: `18.990000`
- anchored_score: `41.590000`
- delta_vs_anchor_60: `-18.410000`
- delta_vs_anchor_raw: `-28.320000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. Behavior Interpretation
- Observed 13787 trades across 31 active trading days in the analysis window.
- PnL curve shapes: all-time=smooth_up, 30d=insufficient_data, 7d=insufficient_data.
- Dominant sector themes: sports.

## 4. Copy-Trading Strengths
- Low non-copyable token-fast BUY ratio.
- Topic supply is broad enough for selective deployment.
- All-time PnL profile is smooth-up, supporting strategy consistency.
- Operational whitelist themes: win, liverpool, club, sharks, end, twins.

## 5. Copy-Trading Risks
- Meaningful exclusive concurrent-leg behavior (multi-leg overlap in mutually exclusive markets).
- High nested concurrent-ladder ratio, implying heavier structure management.
- Weighted multi-market risk is elevated.
- Risk gate is triggered, so broad-copy mode is disabled and only strict filtering is allowed.
- Severe-risk gate is triggered; poor setups are automatically classified as not recommended.
- Hard blacklist themes to avoid: set, spread, handicap, moneyline, open, miami.
- Soft blacklist themes requiring stricter triggers: madrid, halftime, red, city, real, one.

## 6. Sector and Keyword Filters
### Sector Tags
- sports

### Whitelist Keywords
- win
- liverpool
- club
- sharks
- end
- twins
- minnesota
- penguins
- brighton
- hove
- albion
- calcio

### Hard Blacklist Keywords
- set
- spread
- handicap
- moneyline
- open
- miami
- match
- sets
- total
- games
- winner
- rounds

### Soft Blacklist Keywords
- madrid
- halftime
- red
- city
- real
- one
- credit
- charleston
- leading
- new
- york
- chicago

## 7. Account Overview
- analysis_window: `2026-03-11 18:27:29 UTC -> 2026-04-10 18:21:57 UTC`
- trade_rows_used: `13787`
- total_buy_usdc: `1247861.585367`
- total_sell_usdc: `0`
- traded_markets_count_api: `12272`
- position_value_api: `32297.324600`

## 8. Core Metrics
- dual_side_buy_usdc_ratio: `26.62%`
- dual_side_buy_usdc_ratio_1h: `14.35%`
- token_fast_20m_buy_usdc_ratio: `0.00%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `n/a`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `69.73%`
- nested_concurrent_leg_ratio: `61.55%`
- weighted_multi_market_risk_ratio: `49.54%`
- deployable_event_equivalent: `1319.000000`
- deployable_event_density: `43.972299`
- active_trading_days: `31.000000`
- trade_count: `13787.000000`
- avg_trades_per_active_day: `444.741935`

## 9. PnL Curve Evaluation
- all_time_shape: `smooth_up`
- all_time_score: `12`
- d30_shape: `insufficient_data`
- d30_score: `0`
- d7_shape: `insufficient_data`
- d7_score: `0`
- pnl_tag: `long_and_recent_weak`

## 10. Score Breakdown
- copyability_score: `0`
- deployability_score: `20`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `9.990000`
- risk_penalty_adjustment: `-11.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. Data Quality and Assumptions
- Risk gate triggered; decision cannot be broad-copy and requires strict blacklist filtering
- Severe risk gate triggered; score threshold for not_recommended is tightened
- Severe risk gate + low calibrated score -> not_recommended
- No matched SELL inventory found; holding-time metrics unavailable
