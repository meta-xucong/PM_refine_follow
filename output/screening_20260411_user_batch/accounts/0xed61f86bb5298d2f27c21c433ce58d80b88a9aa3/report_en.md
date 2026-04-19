# Burdensome-Piracy

## Account Identity (Manual Verification First)
- Display name: `Burdensome-Piracy`
- Account address: `0xed61f86bb5298d2f27c21c433ce58d80b88a9aa3`
- Source pseudonym: `Burdensome-Piracy`
- Source profile name: `ewww1`
- Source local name: `account_27`

## 1. Executive Conclusion
Calibrated decision score is 33.12 (anchor-referenced), decision: not_recommended. Primary sector exposure: sports. Strengths: deployable event breadth, contained multi-market weighted risk. Key risks: exclusive concurrent-leg risk, non-copyable token-fast exposure. Hard blacklist themes: win, end, draw, real, madrid. Soft blacklist themes: wrexham. Risk gate is active, so broad-copy mode is disabled. Severe-risk gate is active; low-score scenarios are forced to not_recommended. PnL curve tag: long_mid_short_strong. This account is not recommended as a primary copy-trading source; only rare manual picks may be considered.

## 2. Decision Snapshot
- decision: `not_recommended`
- final_score (decision basis): `33.120000`
- raw_score: `41.960000`
- anchored_score: `33.120000`
- delta_vs_anchor_60: `-26.880000`
- delta_vs_anchor_raw: `-41.360000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. Behavior Interpretation
- Observed 1040 trades across 19 active trading days in the analysis window.
- PnL curve shapes: all-time=smooth_up, 30d=smooth_up, 7d=smooth_up.
- Dominant sector themes: sports.

## 4. Copy-Trading Strengths
- Nested concurrent behavior remains relatively contained.
- Weighted multi-market structure risk is controlled.
- Topic supply is broad enough for selective deployment.
- All-time PnL profile is smooth-up, supporting strategy consistency.
- Recent 30-day PnL remains constructive.

## 5. Copy-Trading Risks
- Elevated non-copyable token-fast BUY ratio, suggesting execution-dependent edge.
- Meaningful exclusive concurrent-leg behavior (multi-leg overlap in mutually exclusive markets).
- Risk gate is triggered, so broad-copy mode is disabled and only strict filtering is allowed.
- Severe-risk gate is triggered; poor setups are automatically classified as not recommended.
- Hard blacklist themes to avoid: win, end, draw, real, madrid, paris.
- Soft blacklist themes requiring stricter triggers: wrexham.

## 6. Sector and Keyword Filters
### Sector Tags
- sports

### Whitelist Keywords
- (none)

### Hard Blacklist Keywords
- win
- end
- draw
- real
- madrid
- paris
- both
- teams
- score
- senators
- city
- united

### Soft Blacklist Keywords
- wrexham

## 7. Account Overview
- analysis_window: `2026-03-15 15:10:19 UTC -> 2026-04-10 20:23:17 UTC`
- trade_rows_used: `1040`
- total_buy_usdc: `80242.928383`
- total_sell_usdc: `89524.866726`
- traded_markets_count_api: `3171`
- position_value_api: `15.000000`

## 8. Core Metrics
- dual_side_buy_usdc_ratio: `17.18%`
- dual_side_buy_usdc_ratio_1h: `16.50%`
- token_fast_20m_buy_usdc_ratio: `98.85%`
- noncopyable_token_fast_buy_ratio: `95.87%`
- noncopyable_token_fast_sell_ratio: `97.13%`
- noncopyable_token_fast_token_ratio: `72.85%`
- event_rebalance_20m_event_ratio: `25.53%`
- exclusive_concurrent_leg_ratio: `36.06%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `9.70%`
- deployable_event_equivalent: `21.000000`
- deployable_event_density: `0.800997`
- active_trading_days: `19.000000`
- trade_count: `1040.000000`
- avg_trades_per_active_day: `54.736842`

## 9. PnL Curve Evaluation
- all_time_shape: `smooth_up`
- all_time_score: `12`
- d30_shape: `smooth_up`
- d30_score: `6`
- d7_shape: `smooth_up`
- d7_score: `2`
- pnl_tag: `long_mid_short_strong`

## 10. Score Breakdown
- copyability_score: `0`
- deployability_score: `20`
- multi_market_structure_score: `5.960000`
- pnl_curve_stability_score: `28`
- risk_penalty_adjustment: `-12.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. Data Quality and Assumptions
- Risk gate triggered; decision cannot be broad-copy and requires strict blacklist filtering
- Severe risk gate triggered; score threshold for not_recommended is tightened
- Severe risk gate + low calibrated score -> not_recommended
