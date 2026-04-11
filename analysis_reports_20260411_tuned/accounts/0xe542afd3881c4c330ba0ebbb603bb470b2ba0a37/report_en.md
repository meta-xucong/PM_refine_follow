# account_8 Polymarket Account Screening Report

## 1. Account Overview
- account_address: `0xe542afd3881c4c330ba0ebbb603bb470b2ba0a37`
- analysis_window: `2026-03-11 18:44:05 UTC -> 2026-04-10 18:26:17 UTC`
- trade_rows_used: `22151`
- total_buy_usdc: `266478.891238`
- total_sell_usdc: `263625.779700`
- traded_markets_count_api: `5011`
- position_value_api: `111557.571200`

## 2. Core Metrics
- dual_side_buy_usdc_ratio: `8.60%`
- dual_side_buy_usdc_ratio_1h: `4.03%`
- token_fast_20m_buy_usdc_ratio: `30.16%`
- noncopyable_token_fast_buy_ratio: `21.17%`
- noncopyable_token_fast_sell_ratio: `24.95%`
- noncopyable_token_fast_token_ratio: `10.56%`
- event_rebalance_20m_event_ratio: `16.50%`
- exclusive_concurrent_leg_ratio: `56.52%`
- nested_concurrent_leg_ratio: `86.32%`
- weighted_multi_market_risk_ratio: `12.71%`
- deployable_event_equivalent: `119.000000`
- deployable_event_density: `3.968302`
- active_trading_days: `31.000000`
- trade_count: `22151.000000`
- avg_trades_per_active_day: `714.548387`

## 3. PnL Curve Evaluation
- all_time_shape: `smooth_up`
- all_time_score: `12`
- d30_shape: `insufficient_data`
- d30_score: `0`
- d7_shape: `insufficient_data`
- d7_score: `0`
- pnl_tag: `long_and_recent_weak`

## 4. Score Breakdown
- copyability_score: `0`
- deployability_score: `20`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `7.290000`
- risk_penalty_adjustment: `-17.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`
- raw_score: `10.290000`
- anchored_score: `34.190000`
- delta_vs_anchor_60: `-25.810000`
- delta_vs_anchor_raw: `-25.810000`
- final_score: `10.290000`
- decision_score_basis: `raw_score`
- decision: `not_recommended`
- anchor_version: `anchor_v1`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 5. Sector Tags
- sports
- us_politics
- geopolitics

## 6. Whitelist Keywords
- barcelona
- rybakina
- elena
- bahrain
- lakers
- ufc
- card
- main
- night
- featherweight
- club
- stage

## 7. Hard Blacklist Keywords
- win
- league
- nba
- cup
- world
- finals
- top
- champions
- magic
- chelsea
- fifa
- premier

## 8. Soft Blacklist Keywords
- city
- arsenal
- miami
- grand
- prix
- singles
- mavericks
- lead
- during
- denmark

## 9. Narrative Conclusion
Final score is 10.29, decision: not_recommended. Strengths: deployable event breadth, contained multi-market weighted risk. Key risks: exclusive concurrent-leg risk, nested concurrent-ladder risk, non-copyable token-fast exposure. PnL curve tag: long_and_recent_weak. This account is not recommended as a primary copy-trading source under V2.2 rules.

## 10. Data Quality and Assumptions
- Hard exclusion triggered; decision forced to not_recommended
