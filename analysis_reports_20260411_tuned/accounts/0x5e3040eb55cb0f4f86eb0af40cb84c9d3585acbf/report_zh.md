# account_29 Polymarket 账户筛选报告（中文版）

## 1. 账户概览
- account_address: `0x5e3040eb55cb0f4f86eb0af40cb84c9d3585acbf`
- analysis_window: `2026-03-11 18:27:29 UTC -> 2026-04-10 18:21:57 UTC`
- trade_rows_used: `13787`
- total_buy_usdc: `1247861.585367`
- total_sell_usdc: `0`
- traded_markets_count_api: `12272`
- position_value_api: `32297.324600`

## 2. 核心指标
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

## 3. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 4. 评分拆解
- copyability_score: `0`
- deployability_score: `20`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `7.290000`
- risk_penalty_adjustment: `-14.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`
- raw_score: `13.290000`
- anchored_score: `37.190000`
- delta_vs_anchor_60: `-22.810000`
- delta_vs_anchor_raw: `-22.810000`
- final_score: `13.290000`
- decision_score_basis: `raw_score`
- decision: `不值得跟`
- anchor_version: `anchor_v1`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 5. 所属板块
- sports

## 6. 白名单关键词
- win
- liverpool
- club
- sharks
- end
- twins
- minnesota
- albion
- hove
- brighton
- calcio
- ducks

## 7. 硬黑名单关键词
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

## 8. 软黑名单关键词
- red
- city
- real
- credit
- one
- charleston
- new
- york
- chicago
- devils
- hurricanes
- utah

## 9. 结论描述
最终分数 13.29，结论：不值得跟。优势：可利用事件覆盖广、不可复制快交易比例较低。风险点：互斥型并存腿风险较高、递进型并存梯度风险偏高、存在同 condition 双边买入。收益曲线标签：长期与近期均偏弱。不建议作为主跟单源。

## 10. 数据质量与假设
- 触发硬风控排除规则，结论被强制为不值得跟
- 未匹配到可用 SELL 库存，持仓时长指标不可用
