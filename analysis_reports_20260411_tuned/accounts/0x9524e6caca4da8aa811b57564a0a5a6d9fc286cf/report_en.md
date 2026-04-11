# account_7 Polymarket Account Screening Report

## 1. Account Overview
- account_address: `0x9524e6caca4da8aa811b57564a0a5a6d9fc286cf`
- analysis_window: `2026-03-11 22:49:13 UTC -> 2026-04-10 16:59:51 UTC`
- trade_rows_used: `418`
- total_buy_usdc: `33418.598454`
- total_sell_usdc: `21605.810535`
- traded_markets_count_api: `401`
- position_value_api: `49111.486100`

## 2. Core Metrics
- dual_side_buy_usdc_ratio: `57.97%`
- dual_side_buy_usdc_ratio_1h: `53.73%`
- token_fast_20m_buy_usdc_ratio: `23.94%`
- noncopyable_token_fast_buy_ratio: `5.24%`
- noncopyable_token_fast_sell_ratio: `10.64%`
- noncopyable_token_fast_token_ratio: `2.13%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `1.42%`
- deployable_event_equivalent: `26.500000`
- deployable_event_density: `0.890535`
- active_trading_days: `24.000000`
- trade_count: `418.000000`
- avg_trades_per_active_day: `17.416667`

## 3. PnL Curve Evaluation
- all_time_shape: `smooth_up`
- all_time_score: `12`
- d30_shape: `insufficient_data`
- d30_score: `0`
- d7_shape: `insufficient_data`
- d7_score: `0`
- pnl_tag: `long_and_recent_weak`

## 4. Score Breakdown
- copyability_score: `15.570000`
- deployability_score: `20`
- multi_market_structure_score: `20`
- pnl_curve_stability_score: `7.290000`
- risk_penalty_adjustment: `-11.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`
- raw_score: `51.860000`
- anchored_score: `75.760000`
- delta_vs_anchor_60: `15.760000`
- delta_vs_anchor_raw: `15.760000`
- final_score: `51.860000`
- decision_score_basis: `raw_score`
- decision: `not_recommended`
- anchor_version: `anchor_v1`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 5. Sector Tags
- sports
- us_politics
- geopolitics

## 6. Whitelist Keywords
- league
- premier
- next
- presidential
- denmark
- ocasio-cortez
- alexandria
- democratic
- iran
- party
- miami
- open

## 7. Hard Blacklist Keywords
- election
- seats
- parliamentary
- most
- movement
- slovenian
- april
- russia

## 8. Soft Blacklist Keywords
- win
- popular

## 9. Narrative Conclusion
Final score is 51.86, decision: not_recommended. Strengths: deployable event breadth, contained multi-market weighted risk, low non-copyable token-fast ratio. Key risks: dual-side condition buying. PnL curve tag: long_and_recent_weak. This account is not recommended as a primary copy-trading source under V2.2 rules.

## 10. Data Quality and Assumptions
- Hard exclusion triggered; decision forced to not_recommended
