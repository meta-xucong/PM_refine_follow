# Ideal-Copying

## 账户身份（优先人工核对）
- 展示名称: `Ideal-Copying`
- 账户地址: `0x67bb64fac5252df3f61ee2d91a4b1350e40eb6ef`
- 平台昵称: `Ideal-Copying`
- 平台名称: `Blueberry1337`
- 本地名称: `account_12`

## 1. 执行结论
校准后决策分 25.91（锚点口径），结论：不值得跟。主要板块暴露：sports。优势：可利用事件覆盖广、不可复制快交易比例较低。风险点：互斥型并存腿风险较高。硬黑名单主题（禁止跟）：counter-strike、map、winner、bo3、themongolz。软黑名单主题（谨慎跟）：hawks、game。白名单主题（优先筛选）：lakers、pistons、celtics、thunder、clippers。风险门槛已触发，宽跟模式自动关闭。重风险门槛已触发，低分情形会被强制判定为不值得跟。收益曲线标签：长期与近期均偏弱。不建议作为主跟单源，仅可少量人工挑选。

## 2. 决策快照
- decision: `不值得跟`
- final_score（决策分）: `25.910000`
- raw_score: `30.880000`
- anchored_score: `25.910000`
- delta_vs_anchor_60: `-34.090000`
- delta_vs_anchor_raw: `-52.440000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 7556 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=volatile_up, 30d=volatile_up, 7d=down.
- 主要板块主题： sports.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 可执行白名单主题：lakers, pistons, celtics, thunder, clippers, timberwolves.

## 5. 跟单风险
- 存在明显互斥市场并发多腿行为。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 已触发重风险门槛，差质标的会被自动归为不值得跟。
- 近 7 天收益动量为负，需要更严格入场过滤。
- 硬黑名单主题（应避免）：counter-strike, map, winner, bo3, themongolz, parivision.
- 软黑名单主题（需更严格触发）：hawks, game.

## 6. 板块与关键词过滤
### 所属板块
- sports

### 白名单关键词
- lakers
- pistons
- celtics
- thunder
- clippers
- timberwolves
- magic
- warriors
- rockets
- heat
- suns
- pacers

### 硬黑名单关键词
- counter-strike
- map
- winner
- bo3
- themongolz
- parivision
- natus
- vincere
- esports
- aurora
- gaming
- bucharest

### 软黑名单关键词
- hawks
- game

## 7. 账户概览
- analysis_window: `2026-03-12 16:04:53 UTC -> 2026-04-11 14:55:09 UTC`
- trade_rows_used: `7556`
- total_buy_usdc: `2897312.275838`
- total_sell_usdc: `185698.113391`
- traded_markets_count_api: `854`
- position_value_api: `87964.235900`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `8.91%`
- dual_side_buy_usdc_ratio_1h: `0.52%`
- token_fast_20m_buy_usdc_ratio: `0.46%`
- noncopyable_token_fast_buy_ratio: `0.46%`
- noncopyable_token_fast_sell_ratio: `2.32%`
- noncopyable_token_fast_token_ratio: `0.47%`
- event_rebalance_20m_event_ratio: `3.94%`
- exclusive_concurrent_leg_ratio: `66.90%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `34.89%`
- deployable_event_equivalent: `77.000000`
- deployable_event_density: `2.570816`
- active_trading_days: `31.000000`
- trade_count: `7556.000000`
- avg_trades_per_active_day: `243.741935`

## 9. 收益曲线评估
- all_time_shape: `高波动上行`
- all_time_score: `6`
- d30_shape: `高波动上行`
- d30_score: `2`
- d7_shape: `下行`
- d7_score: `-2`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `7.780000`
- deployability_score: `20`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `11.100000`
- risk_penalty_adjustment: `-8.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
- 触发重风险门槛，不值得跟的判定阈值被收紧
- 重风险门槛叠加低分，判定为不值得跟
- 校准分低于 32，触发不值得跟底线
