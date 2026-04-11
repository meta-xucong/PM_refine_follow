# account_26 Polymarket Account Screening Report

## 1. Account Overview
- account_address: `0x30ceffb3ac4ea49881e271d5a69883b60e0dfdce`
- analysis_window: `2026-03-11 19:16:23 UTC -> 2026-04-10 03:10:47 UTC`
- trade_rows_used: `4373`
- total_buy_usdc: `350401.129641`
- total_sell_usdc: `283928.376464`
- traded_markets_count_api: `822`
- position_value_api: `24.949400`

## 2. Core Metrics
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

## 3. PnL Curve Evaluation
- all_time_shape: `volatile_up`
- all_time_score: `6`
- d30_shape: `insufficient_data`
- d30_score: `0`
- d7_shape: `insufficient_data`
- d7_score: `0`
- pnl_tag: `long_and_recent_weak`

## 4. Score Breakdown
- copyability_score: `0`
- deployability_score: `20`
- multi_market_structure_score: `4.210000`
- pnl_curve_stability_score: `3.650000`
- risk_penalty_adjustment: `-21.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`
- raw_score: `6.850000`
- anchored_score: `30.750000`
- delta_vs_anchor_60: `-29.250000`
- delta_vs_anchor_raw: `-29.250000`
- final_score: `6.850000`
- decision_score_basis: `raw_score`
- decision: `not_recommended`
- anchor_version: `anchor_v1`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 5. Sector Tags
- sports
- geopolitics

## 6. Whitelist Keywords
- france

## 7. Hard Blacklist Keywords
- win
- end
- draw
- chelsea
- barcelona
- sabres
- hurricanes
- united
- jackets
- blue
- red
- bruins

## 8. Soft Blacklist Keywords
- knights
- golden
- ecuador
- morocco

## 9. Narrative Conclusion
Final score is 6.85, decision: not_recommended. Strengths: deployable event breadth, contained multi-market weighted risk. Key risks: exclusive concurrent-leg risk, non-copyable token-fast exposure, dual-side condition buying. PnL curve tag: long_and_recent_weak. This account is not recommended as a primary copy-trading source under V2.2 rules.

## 10. Data Quality and Assumptions
- Hard exclusion triggered; decision forced to not_recommended
