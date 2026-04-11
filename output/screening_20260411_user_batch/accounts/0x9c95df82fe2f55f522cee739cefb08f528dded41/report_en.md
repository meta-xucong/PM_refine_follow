# Miserable-Blizzard

## Account Identity (Manual Verification First)
- Display name: `Miserable-Blizzard`
- Account address: `0x9c95df82fe2f55f522cee739cefb08f528dded41`
- Source pseudonym: `Miserable-Blizzard`
- Source profile name: `ben1243`
- Source local name: `account_4`

## 1. Executive Conclusion
Calibrated decision score is 37.59 (anchor-referenced), decision: not_recommended. Primary sector exposure: sports. Strengths: deployable event breadth, contained multi-market weighted risk, low non-copyable token-fast ratio. Key risks: exclusive concurrent-leg risk, dual-side condition buying. Hard blacklist themes: win, heavyweight, milan, prelims, madrid. Soft blacklist themes: bayern, nchen. Whitelist themes: arsenal, flyers, blackhawks, barcelona, utah. Risk gate is active, so broad-copy mode is disabled. Severe-risk gate is active; low-score scenarios are forced to not_recommended. PnL curve tag: long_and_recent_weak. This account is not recommended as a primary copy-trading source; only rare manual picks may be considered.

## 2. Decision Snapshot
- decision: `not_recommended`
- final_score (decision basis): `37.590000`
- raw_score: `12.830000`
- anchored_score: `37.590000`
- delta_vs_anchor_60: `-22.410000`
- delta_vs_anchor_raw: `-34.480000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. Behavior Interpretation
- Observed 1188 trades across 26 active trading days in the analysis window.
- PnL curve shapes: all-time=flat, 30d=insufficient_data, 7d=insufficient_data.
- Dominant sector themes: sports.

## 4. Copy-Trading Strengths
- Low non-copyable token-fast BUY ratio.
- Nested concurrent behavior remains relatively contained.
- Weighted multi-market structure risk is controlled.
- Topic supply is broad enough for selective deployment.
- Operational whitelist themes: arsenal, flyers, blackhawks, barcelona, utah, kings.

## 5. Copy-Trading Risks
- High dual-side condition activity, which is often difficult to mirror in copy-trading.
- Meaningful exclusive concurrent-leg behavior (multi-leg overlap in mutually exclusive markets).
- Risk gate is triggered, so broad-copy mode is disabled and only strict filtering is allowed.
- Severe-risk gate is triggered; poor setups are automatically classified as not recommended.
- All-time PnL profile is not strongly upward, reducing confidence in persistent edge.
- Hard blacklist themes to avoid: win, heavyweight, milan, prelims, madrid, warriors.
- Soft blacklist themes requiring stricter triggers: bayern, nchen.

## 6. Sector and Keyword Filters
### Sector Tags
- sports

### Whitelist Keywords
- arsenal
- flyers
- blackhawks
- barcelona
- utah
- kings
- lakers
- rockets
- roma
- milano
- internazionale
- vitor

### Hard Blacklist Keywords
- win
- heavyweight
- milan
- prelims
- madrid
- warriors
- real
- timberwolves
- nuggets
- spurs
- pistons
- hawks

### Soft Blacklist Keywords
- bayern
- nchen

## 7. Account Overview
- analysis_window: `2026-03-12 16:42:59 UTC -> 2026-04-11 10:52:23 UTC`
- trade_rows_used: `1188`
- total_buy_usdc: `237909.133938`
- total_sell_usdc: `142213.014615`
- traded_markets_count_api: `591`
- position_value_api: `6556.680100`

## 8. Core Metrics
- dual_side_buy_usdc_ratio: `42.01%`
- dual_side_buy_usdc_ratio_1h: `9.18%`
- token_fast_20m_buy_usdc_ratio: `3.90%`
- noncopyable_token_fast_buy_ratio: `0.87%`
- noncopyable_token_fast_sell_ratio: `1.12%`
- noncopyable_token_fast_token_ratio: `3.95%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `96.66%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `2.43%`
- deployable_event_equivalent: `48.000000`
- deployable_event_density: `1.613091`
- active_trading_days: `26.000000`
- trade_count: `1188.000000`
- avg_trades_per_active_day: `45.692308`

## 9. PnL Curve Evaluation
- all_time_shape: `flat`
- all_time_score: `1`
- d30_shape: `insufficient_data`
- d30_score: `0`
- d7_shape: `insufficient_data`
- d7_score: `0`
- pnl_tag: `long_and_recent_weak`

## 10. Score Breakdown
- copyability_score: `0`
- deployability_score: `20`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `0.830000`
- risk_penalty_adjustment: `-8.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. Data Quality and Assumptions
- Risk gate triggered; decision cannot be broad-copy and requires strict blacklist filtering
- Severe risk gate triggered; score threshold for not_recommended is tightened
- Severe risk gate + low calibrated score -> not_recommended
