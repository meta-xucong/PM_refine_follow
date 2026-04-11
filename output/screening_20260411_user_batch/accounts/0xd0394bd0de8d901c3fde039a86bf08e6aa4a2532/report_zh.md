# Closed-Application

## 账户身份（优先人工核对）
- 展示名称: `Closed-Application`
- 账户地址: `0xd0394bd0de8d901c3fde039a86bf08e6aa4a2532`
- 平台昵称: `Closed-Application`
- 平台名称: `pantomime`
- 本地名称: `account_53`

## 1. 执行结论
校准后决策分 49.60（锚点口径），结论：不值得跟。主要板块暴露：geopolitics、us_politics、sports。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：互斥型并存腿风险较高、递进型并存梯度风险偏高、存在同 condition 双边买入。硬黑名单主题（禁止跟）：march、netanyahu、out、iran、april。软黑名单主题（谨慎跟）：weekend、opening、office、box、greater。白名单主题（优先筛选）：officially、war、declare、say、during。风险门槛已触发，宽跟模式自动关闭。重风险门槛已触发，低分情形会被强制判定为不值得跟。收益曲线标签：长期与近期均偏弱。不建议作为主跟单源，仅可少量人工挑选。

## 2. 决策快照
- decision: `不值得跟`
- final_score（决策分）: `49.600000`
- raw_score: `31.310000`
- anchored_score: `49.600000`
- delta_vs_anchor_60: `-10.400000`
- delta_vs_anchor_raw: `-16.000000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 1178 笔交易，覆盖 28 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： geopolitics, us_politics, sports.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 可执行白名单主题：officially, war, declare, say, during, devils.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 存在明显互斥市场并发多腿行为。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 已触发重风险门槛，差质标的会被自动归为不值得跟。
- 硬黑名单主题（应避免）：march, netanyahu, out, iran, april, enter.
- 软黑名单主题（需更严格触发）：weekend, opening, office, box, greater, election.

## 6. 板块与关键词过滤
### 所属板块
- geopolitics
- us_politics
- sports

### 白名单关键词
- officially
- war
- declare
- say
- during
- devils
- awards
- academy
- best
- blackhawks
- flyers
- senators

### 硬黑名单关键词
- march
- netanyahu
- out
- iran
- april
- enter
- forces
- ceasefire
- trump
- win
- texas
- republican

### 软黑名单关键词
- weekend
- opening
- office
- box
- greater
- election

## 7. 账户概览
- analysis_window: `2026-03-12 16:59:03 UTC -> 2026-04-10 18:25:35 UTC`
- trade_rows_used: `1178`
- total_buy_usdc: `645505.616090`
- total_sell_usdc: `139472.287674`
- traded_markets_count_api: `2525`
- position_value_api: `16812.246000`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `80.75%`
- dual_side_buy_usdc_ratio_1h: `15.00%`
- token_fast_20m_buy_usdc_ratio: `1.34%`
- noncopyable_token_fast_buy_ratio: `0.67%`
- noncopyable_token_fast_sell_ratio: `3.08%`
- noncopyable_token_fast_token_ratio: `5.06%`
- event_rebalance_20m_event_ratio: `1.79%`
- exclusive_concurrent_leg_ratio: `33.48%`
- nested_concurrent_leg_ratio: `29.22%`
- weighted_multi_market_risk_ratio: `6.01%`
- deployable_event_equivalent: `44.500000`
- deployable_event_density: `1.531310`
- active_trading_days: `28.000000`
- trade_count: `1178.000000`
- avg_trades_per_active_day: `42.071429`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `1.040000`
- deployability_score: `20`
- multi_market_structure_score: `5.280000`
- pnl_curve_stability_score: `9.990000`
- risk_penalty_adjustment: `-5.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
- 触发重风险门槛，不值得跟的判定阈值被收紧
- 重风险门槛叠加低分，判定为不值得跟
