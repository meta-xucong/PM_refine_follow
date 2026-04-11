# account_4 Polymarket 账户筛选报告（中文版）

## 1. 账户概览
- account_address: `0x4df332e27f9ee3224f52ce30e3ce15c1075e788f`
- analysis_window: `2026-03-11 19:11:41 UTC -> 2026-04-10 18:25:15 UTC`
- trade_rows_used: `13509`
- total_buy_usdc: `2555234.489308`
- total_sell_usdc: `0`
- traded_markets_count_api: `8887`
- position_value_api: `48833.368900`

## 2. 核心指标
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

## 3. 收益曲线评估
- all_time_shape: `下行`
- all_time_score: `-10`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 4. 评分拆解
- copyability_score: `0`
- deployability_score: `20`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `-6.080000`
- risk_penalty_adjustment: `-29.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`
- raw_score: `0`
- anchored_score: `23.900000`
- delta_vs_anchor_60: `-36.100000`
- delta_vs_anchor_raw: `-36.100000`
- final_score: `0`
- decision_score_basis: `raw_score`
- decision: `不值得跟`
- anchor_version: `anchor_v1`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 5. 所属板块
- sports

## 6. 白名单关键词
- rajasthan
- royals
- lucknow
- giants
- hyderabad
- sunrisers
- madrid
- tico
- club
- atl
- bucharest
- daniel

## 7. 硬黑名单关键词
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
- spurs
- pelicans

## 8. 软黑名单关键词
- league
- premier
- indian
- titans
- gujarat
- royal
- challengers
- bangalore
- prix
- grand
- zverev
- women

## 9. 结论描述
最终分数 0.00，结论：不值得跟。优势：可利用事件覆盖广、不可复制快交易比例较低。风险点：互斥型并存腿风险较高、存在同 condition 双边买入。收益曲线标签：长期与近期均偏弱。不建议作为主跟单源。

## 10. 数据质量与假设
- 触发硬风控排除规则，结论被强制为不值得跟
- 未匹配到可用 SELL 库存，持仓时长指标不可用
