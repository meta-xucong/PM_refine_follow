# account_17 Polymarket Account Screening Report

## 1. Account Overview
- account_address: `0xd66f79a8d19d4223b6c70dd4e620d4875501a19b`
- analysis_window: `2026-03-11 18:49:19 UTC -> 2026-04-09 19:05:39 UTC`
- trade_rows_used: `3671`
- total_buy_usdc: `357851.317187`
- total_sell_usdc: `0`
- traded_markets_count_api: `1181`
- position_value_api: `0.000000`

## 2. Core Metrics
- dual_side_buy_usdc_ratio: `93.81%`
- dual_side_buy_usdc_ratio_1h: `92.21%`
- token_fast_20m_buy_usdc_ratio: `0.00%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `n/a`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `14.90%`
- deployable_event_equivalent: `10.000000`
- deployable_event_density: `0.344693`
- active_trading_days: `18.000000`
- trade_count: `3671.000000`
- avg_trades_per_active_day: `203.944444`

## 3. PnL Curve Evaluation
- all_time_shape: `volatile_up`
- all_time_score: `6`
- d30_shape: `insufficient_data`
- d30_score: `0`
- d7_shape: `insufficient_data`
- d7_score: `0`
- pnl_tag: `long_and_recent_weak`

## 4. Score Breakdown
- copyability_score: `4.180000`
- deployability_score: `20`
- multi_market_structure_score: `20`
- pnl_curve_stability_score: `3.650000`
- risk_penalty_adjustment: `-11.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`
- raw_score: `36.820000`
- anchored_score: `60.720000`
- delta_vs_anchor_60: `0.720000`
- delta_vs_anchor_raw: `0.720000`
- final_score: `36.820000`
- decision_score_basis: `raw_score`
- decision: `not_recommended`
- anchor_version: `anchor_v1`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 5. Sector Tags
- sports
- geopolitics

## 6. Whitelist Keywords
- march

## 7. Hard Blacklist Keywords
- win
- united
- madrid
- real
- manchester
- liverpool
- forest
- nottingham
- arsenal
- city
- newcastle
- draw

## 8. Soft Blacklist Keywords
- aston
- villa
- mallorca
- rcd

## 9. Narrative Conclusion
Final score is 36.82, decision: not_recommended. Strengths: deployable event breadth, contained multi-market weighted risk, low non-copyable token-fast ratio. Key risks: dual-side condition buying. PnL curve tag: long_and_recent_weak. This account is not recommended as a primary copy-trading source under V2.2 rules.

## 10. Data Quality and Assumptions
- Hard exclusion triggered; decision forced to not_recommended
- No matched SELL inventory found; holding-time metrics unavailable
