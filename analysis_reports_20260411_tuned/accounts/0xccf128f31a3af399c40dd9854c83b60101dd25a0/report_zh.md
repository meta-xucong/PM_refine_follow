# account_30 Polymarket 账户筛选报告（中文版）

## 1. 账户概览
- account_address: `0xccf128f31a3af399c40dd9854c83b60101dd25a0`
- analysis_window: `2026-03-11 23:47:11 UTC -> 2026-04-10 03:33:11 UTC`
- trade_rows_used: `1231`
- total_buy_usdc: `382573.105110`
- total_sell_usdc: `0`
- traded_markets_count_api: `1972`
- position_value_api: `66994.565100`

## 2. 核心指标
- dual_side_buy_usdc_ratio: `20.06%`
- dual_side_buy_usdc_ratio_1h: `14.72%`
- token_fast_20m_buy_usdc_ratio: `0.00%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `n/a`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `61.30%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `55.86%`
- deployable_event_equivalent: `90.000000`
- deployable_event_density: `3.086743`
- active_trading_days: `30.000000`
- trade_count: `1231.000000`
- avg_trades_per_active_day: `41.033333`

## 3. 收益曲线评估
- all_time_shape: `走平`
- all_time_score: `1`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 4. 评分拆解
- copyability_score: `0`
- deployability_score: `20`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `0.610000`
- risk_penalty_adjustment: `-10.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`
- raw_score: `10.610000`
- anchored_score: `34.510000`
- delta_vs_anchor_60: `-25.490000`
- delta_vs_anchor_raw: `-25.490000`
- final_score: `10.610000`
- decision_score_basis: `raw_score`
- decision: `不值得跟`
- anchor_version: `anchor_v1`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 5. 所属板块
- sports

## 6. 白名单关键词
- cornhuskers
- nebraska
- flyers
- bruins
- bears
- auburn
- islanders
- seattle
- senators
- sharks
- golden
- tulsa

## 7. 硬黑名单关键词
- spread
- pacers
- heat
- cavaliers
- suns
- trail
- blazers
- bulls
- magic
- pistons
- thunder
- clippers

## 8. 软黑名单关键词
- spurs
- raptors
- nets
- wildcats

## 9. 结论描述
最终分数 10.61，结论：不值得跟。优势：可利用事件覆盖广、不可复制快交易比例较低。风险点：互斥型并存腿风险较高、存在同 condition 双边买入。收益曲线标签：长期与近期均偏弱。不建议作为主跟单源。

## 10. 数据质量与假设
- 触发硬风控排除规则，结论被强制为不值得跟
- 未匹配到可用 SELL 库存，持仓时长指标不可用
