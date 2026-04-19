# Digital-Bill

## Account Identity (Manual Verification First)
- Display name: `Digital-Bill`
- Account address: `0x9ba43501360dcacaca09caa523401c7447d8f8c2`
- Source pseudonym: `Digital-Bill`
- Source profile name: `BipBop`
- Source local name: `account_20`

## 1. Executive Conclusion
Calibrated decision score is 31.13 (anchor-referenced), decision: not_recommended. Primary sector exposure: us_politics, geopolitics. Strengths: contained multi-market weighted risk. Key risks: nested concurrent-ladder risk, non-copyable token-fast exposure. Hard blacklist themes: say, trump, during, march, week. Soft blacklist themes: questions, reform, minister, starmer, prime. Risk gate is active, so broad-copy mode is disabled. Severe-risk gate is active; low-score scenarios are forced to not_recommended. PnL curve tag: long_mid_short_strong. This account is not recommended as a primary copy-trading source; only rare manual picks may be considered.

## 2. Decision Snapshot
- decision: `not_recommended`
- final_score (decision basis): `31.130000`
- raw_score: `38.900000`
- anchored_score: `31.130000`
- delta_vs_anchor_60: `-28.870000`
- delta_vs_anchor_raw: `-44.420000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. Behavior Interpretation
- Observed 339 trades across 18 active trading days in the analysis window.
- Low-frequency cap is active at 56, reflecting constrained copy capacity.
- PnL curve shapes: all-time=smooth_up, 30d=smooth_up, 7d=smooth_up.
- Dominant sector themes: us_politics, geopolitics.

## 4. Copy-Trading Strengths
- Low dual-side condition exposure, indicating cleaner directional expression.
- Weighted multi-market structure risk is controlled.
- All-time PnL profile is smooth-up, supporting strategy consistency.
- Recent 30-day PnL remains constructive.

## 5. Copy-Trading Risks
- Elevated non-copyable token-fast BUY ratio, suggesting execution-dependent edge.
- Risk gate is triggered, so broad-copy mode is disabled and only strict filtering is allowed.
- Severe-risk gate is triggered; poor setups are automatically classified as not recommended.
- Frequency/deployability constraints limit practical copy capacity.
- Hard blacklist themes to avoid: say, trump, during, march, week, epic.
- Soft blacklist themes requiring stricter triggers: questions, reform, minister, starmer, prime.

## 6. Sector and Keyword Filters
### Sector Tags
- us_politics
- geopolitics

### Whitelist Keywords
- (none)

### Hard Blacklist Keywords
- say
- trump
- during
- march
- week
- epic
- fury
- times
- press
- next
- white
- house

### Soft Blacklist Keywords
- questions
- reform
- minister
- starmer
- prime

## 7. Account Overview
- analysis_window: `2026-03-12 20:37:57 UTC -> 2026-04-08 17:46:39 UTC`
- trade_rows_used: `339`
- total_buy_usdc: `36274.659083`
- total_sell_usdc: `44731.017876`
- traded_markets_count_api: `1181`
- position_value_api: `0.000000`

## 8. Core Metrics
- dual_side_buy_usdc_ratio: `0.00%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `92.58%`
- noncopyable_token_fast_buy_ratio: `86.48%`
- noncopyable_token_fast_sell_ratio: `86.69%`
- noncopyable_token_fast_token_ratio: `74.42%`
- event_rebalance_20m_event_ratio: `66.67%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `39.40%`
- weighted_multi_market_risk_ratio: `17.74%`
- deployable_event_equivalent: `4.000000`
- deployable_event_density: `0.148804`
- active_trading_days: `18.000000`
- trade_count: `339.000000`
- avg_trades_per_active_day: `18.833333`

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
- deployability_score: `13.620000`
- multi_market_structure_score: `9.280000`
- pnl_curve_stability_score: `28`
- risk_penalty_adjustment: `-12.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `56`

## 11. Data Quality and Assumptions
- Risk gate triggered; decision cannot be broad-copy and requires strict blacklist filtering
- Severe risk gate triggered; score threshold for not_recommended is tightened
- Severe risk gate + low calibrated score -> not_recommended
- Calibrated score below 32 -> not_recommended floor
