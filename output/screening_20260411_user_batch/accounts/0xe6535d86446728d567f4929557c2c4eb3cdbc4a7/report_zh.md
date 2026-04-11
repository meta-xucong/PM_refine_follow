# Medical-Fund

## 账户身份（优先人工核对）
- 展示名称: `Medical-Fund`
- 账户地址: `0xe6535d86446728d567f4929557c2c4eb3cdbc4a7`
- 平台昵称: `Medical-Fund`
- 平台名称: `Kluivert9`
- 本地名称: `account_42`

## 1. 执行结论
校准后决策分 42.52（锚点口径），结论：只适合筛着跟。主要板块暴露：sports。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：互斥型并存腿风险较高。硬黑名单主题（禁止跟）：rockets、pacers、lakers、magic、knicks。白名单主题（优先筛选）：win、newcastle、united、clippers、hawks。风险门槛已触发，宽跟模式自动关闭。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `42.520000`
- raw_score: `20.420000`
- anchored_score: `42.520000`
- delta_vs_anchor_60: `-17.480000`
- delta_vs_anchor_raw: `-26.890000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 997 笔交易，覆盖 17 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=down, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： sports.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 可执行白名单主题：win, newcastle, united, clippers, hawks, suns.

## 5. 跟单风险
- 存在明显互斥市场并发多腿行为。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 全周期收益并非明显上行，持续优势可信度下降。
- 硬黑名单主题（应避免）：rockets, pacers, lakers, magic, knicks, warriors.

## 6. 板块与关键词过滤
### 所属板块
- sports

### 白名单关键词
- win
- newcastle
- united
- clippers
- hawks
- suns
- nuggets
- mavericks
- ers
- pelicans
- timberwolves
- wizards

### 硬黑名单关键词
- rockets
- pacers
- lakers
- magic
- knicks
- warriors

### 软黑名单关键词
- (none)

## 7. 账户概览
- analysis_window: `2026-03-15 22:54:35 UTC -> 2026-04-08 03:17:11 UTC`
- trade_rows_used: `997`
- total_buy_usdc: `726931.365364`
- total_sell_usdc: `0`
- traded_markets_count_api: `428`
- position_value_api: `0.000000`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `19.42%`
- dual_side_buy_usdc_ratio_1h: `13.96%`
- token_fast_20m_buy_usdc_ratio: `0.00%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `n/a`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `55.23%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `3.21%`
- deployable_event_equivalent: `35.000000`
- deployable_event_density: `1.509769`
- active_trading_days: `17.000000`
- trade_count: `997.000000`
- avg_trades_per_active_day: `58.647059`

## 9. 收益曲线评估
- all_time_shape: `下行`
- all_time_score: `-10`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `13.320000`
- deployability_score: `20`
- multi_market_structure_score: `3.430000`
- pnl_curve_stability_score: `-8.330000`
- risk_penalty_adjustment: `-8.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
- 未匹配到可用 SELL 库存，持仓时长指标不可用
