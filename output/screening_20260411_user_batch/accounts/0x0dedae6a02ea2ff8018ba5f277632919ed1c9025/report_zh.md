# Eminent-Pepper

## 账户身份（优先人工核对）
- 展示名称: `Eminent-Pepper`
- 账户地址: `0x0dedae6a02ea2ff8018ba5f277632919ed1c9025`
- 平台昵称: `Eminent-Pepper`
- 平台名称: `jcharger`
- 本地名称: `account_44`

## 1. 执行结论
校准后决策分 68.89（锚点口径），结论：只适合筛着跟。主要板块暴露：us_politics、entertainment、geopolitics。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：递进型并存梯度风险偏高。硬黑名单主题（禁止跟）：say、during、april、median、home。软黑名单主题（谨慎跟）：easter、bts、sales、album、debut。白名单主题（优先筛选）：francisco、san、number、tsa、total。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `68.890000`
- raw_score: `60.980000`
- anchored_score: `68.890000`
- delta_vs_anchor_60: `8.890000`
- delta_vs_anchor_raw: `13.670000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 464 笔交易，覆盖 25 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： us_politics, entertainment, geopolitics.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 可执行白名单主题：francisco, san, number, tsa, total, passengers.

## 5. 跟单风险
- 递进型并发梯度比例偏高，结构管理负担较重。
- 硬黑名单主题（应避免）：say, during, april, median, home, value.
- 软黑名单主题（需更严格触发）：easter, bts, sales, album, debut, arirang.

## 6. 板块与关键词过滤
### 所属板块
- us_politics
- entertainment
- geopolitics

### 白名单关键词
- francisco
- san
- number
- tsa
- total
- passengers
- new
- york
- city
- less
- chicago
- posts

### 硬黑名单关键词
- say
- during
- april
- median
- home
- value
- week
- between
- conference
- house
- white
- press

### 软黑名单关键词
- easter
- bts
- sales
- album
- debut
- arirang
- lunch
- iran
- wednesday
- roll
- egg
- beautiful

## 7. 账户概览
- analysis_window: `2026-03-12 23:31:39 UTC -> 2026-04-11 10:33:03 UTC`
- trade_rows_used: `464`
- total_buy_usdc: `5495.459735`
- total_sell_usdc: `1695.322612`
- traded_markets_count_api: `1773`
- position_value_api: `1511.348400`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `1.13%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `0.86%`
- noncopyable_token_fast_buy_ratio: `0.86%`
- noncopyable_token_fast_sell_ratio: `0.84%`
- noncopyable_token_fast_token_ratio: `0.63%`
- event_rebalance_20m_event_ratio: `3.45%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `63.74%`
- weighted_multi_market_risk_ratio: `18.91%`
- deployable_event_equivalent: `43.500000`
- deployable_event_density: `1.476613`
- active_trading_days: `25.000000`
- trade_count: `464.000000`
- avg_trades_per_active_day: `18.560000`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `24.190000`
- deployability_score: `20`
- multi_market_structure_score: `9.800000`
- pnl_curve_stability_score: `9.990000`
- risk_penalty_adjustment: `-3.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
