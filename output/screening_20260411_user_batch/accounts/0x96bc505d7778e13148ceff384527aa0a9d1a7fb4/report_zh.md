# Extraneous-Sauerkraut

## 账户身份（优先人工核对）
- 展示名称: `Extraneous-Sauerkraut`
- 账户地址: `0x96bc505d7778e13148ceff384527aa0a9d1a7fb4`
- 平台昵称: `Extraneous-Sauerkraut`
- 平台名称: `greninja`
- 本地名称: `account_6`

## 1. 执行结论
校准后决策分 55.18（锚点口径），结论：只适合筛着跟。主要板块暴露：sports、geopolitics。优势：可利用事件覆盖广、不可复制快交易比例较低。风险点：互斥型并存腿风险较高。硬黑名单主题（禁止跟）：lol、winner、gaming、group、bo5。白名单主题（优先筛选）：bo3、open、valorant、masters、blast。风险门槛已触发，宽跟模式自动关闭。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `55.180000`
- raw_score: `39.890000`
- anchored_score: `55.180000`
- delta_vs_anchor_60: `-4.820000`
- delta_vs_anchor_raw: `-7.420000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 365 笔交易，覆盖 14 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： sports, geopolitics.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 可执行白名单主题：bo3, open, valorant, masters, blast, rotterdam.

## 5. 跟单风险
- 存在明显互斥市场并发多腿行为。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 硬黑名单主题（应避免）：lol, winner, gaming, group, bo5, game.

## 6. 板块与关键词过滤
### 所属板块
- sports
- geopolitics

### 白名单关键词
- bo3
- open
- valorant
- masters
- blast
- rotterdam
- hawks
- vct
- santiago
- dota
- pistons
- spurs

### 硬黑名单关键词
- lol
- winner
- gaming
- group
- bo5
- game
- stand
- first
- bilibili
- lyon
- esports
- team

### 软黑名单关键词
- (none)

## 7. 账户概览
- analysis_window: `2026-03-12 18:11:53 UTC -> 2026-03-25 18:01:37 UTC`
- trade_rows_used: `365`
- total_buy_usdc: `33763.331594`
- total_sell_usdc: `1528.999700`
- traded_markets_count_api: `940`
- position_value_api: `89.043800`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `0.00%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `1.51%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `0.00%`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `56.54%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `22.69%`
- deployable_event_equivalent: `57.000000`
- deployable_event_density: `4.387021`
- active_trading_days: `14.000000`
- trade_count: `365.000000`
- avg_trades_per_active_day: `26.071429`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `14.860000`
- deployability_score: `20`
- multi_market_structure_score: `3.040000`
- pnl_curve_stability_score: `9.990000`
- risk_penalty_adjustment: `-8.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
