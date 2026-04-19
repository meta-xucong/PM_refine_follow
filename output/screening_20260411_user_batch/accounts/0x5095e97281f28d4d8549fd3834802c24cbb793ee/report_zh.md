# Insignificant-Affair

## 账户身份（优先人工核对）
- 展示名称: `Insignificant-Affair`
- 账户地址: `0x5095e97281f28d4d8549fd3834802c24cbb793ee`
- 平台昵称: `Insignificant-Affair`
- 平台名称: `0x5095e97281f28d4d8549fd3834802c24cbb793e`
- 本地名称: `account_41`

## 1. 执行结论
校准后决策分 42.24（锚点口径），结论：只适合筛着跟。主要板块暴露：entertainment。优势：加权多子市场风险较低、不可复制快交易比例较低。风险点：存在同 condition 双边买入。硬黑名单主题（禁止跟）：weekend、box、office、opening、greater。软黑名单主题（谨慎跟）：reminders、him、come、here、ready。风险门槛已触发，宽跟模式自动关闭。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `42.240000`
- raw_score: `56`
- anchored_score: `42.240000`
- delta_vs_anchor_60: `-17.760000`
- delta_vs_anchor_raw: `-27.320000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 911 笔交易，覆盖 25 个活跃交易日（分析窗口内）。
- 低频封顶已生效，封顶分数为 56, ，表明可跟单容量受限。
- 收益曲线形态： 全周期=smooth_up, 30d=smooth_up, 7d=flat.
- 主要板块主题： entertainment.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 近 30 天收益曲线表现仍偏正向。

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 交易频次/可利用度约束限制了实盘跟单容量。
- 硬黑名单主题（应避免）：weekend, box, office, opening, greater, between.
- 软黑名单主题（需更严格触发）：reminders, him, come, here, ready, not.

## 6. 板块与关键词过滤
### 所属板块
- entertainment

### 白名单关键词
- (none)

### 硬黑名单关键词
- weekend
- box
- office
- opening
- greater
- between
- project
- mary
- hail
- less
- hoppers
- galaxy

### 软黑名单关键词
- reminders
- him
- come
- here
- ready
- not

## 7. 账户概览
- analysis_window: `2026-03-12 15:19:41 UTC -> 2026-04-11 08:06:53 UTC`
- trade_rows_used: `911`
- total_buy_usdc: `71073.813590`
- total_sell_usdc: `33556.024241`
- traded_markets_count_api: `357`
- position_value_api: `10634.817800`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `60.47%`
- dual_side_buy_usdc_ratio_1h: `8.98%`
- token_fast_20m_buy_usdc_ratio: `0.24%`
- noncopyable_token_fast_buy_ratio: `0.24%`
- noncopyable_token_fast_sell_ratio: `0.19%`
- noncopyable_token_fast_token_ratio: `1.89%`
- event_rebalance_20m_event_ratio: `30.77%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `15.00%`
- deployable_event_equivalent: `3.500000`
- deployable_event_density: `0.117847`
- active_trading_days: `25.000000`
- trade_count: `911.000000`
- avg_trades_per_active_day: `36.440000`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `平滑上行`
- d30_score: `6`
- d7_shape: `走平`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `18.320000`
- deployability_score: `12.110000`
- multi_market_structure_score: `17.500000`
- pnl_curve_stability_score: `28`
- risk_penalty_adjustment: `-5.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `56`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
