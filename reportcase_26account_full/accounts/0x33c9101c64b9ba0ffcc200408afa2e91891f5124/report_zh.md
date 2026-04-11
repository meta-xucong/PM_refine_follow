# Long-Guitar

## 账户身份（优先人工核对）
- 展示名称: `Long-Guitar`
- 账户地址: `0x33c9101c64b9ba0ffcc200408afa2e91891f5124`
- 平台昵称: `Long-Guitar`
- 平台名称: `0x33c9101c64b9ba0fFCC200408afA2e91891f5124-1768236962087`
- 本地名称: `account_6`

## 1. 执行结论
校准后决策分 54.51（锚点口径），结论：只适合筛着跟。主要板块暴露：crypto、sports。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：互斥型并存腿风险较高。硬黑名单主题（禁止跟）：bitcoin、down、march、nuggets、warriors。软黑名单主题（谨慎跟）：heat、wizards、celtics、bulls、pistons。白名单主题（优先筛选）：bitcoin、down、march、am-5、am-4。风险门槛已触发，宽跟模式自动关闭。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `54.510000`
- raw_score: `38.860000`
- anchored_score: `54.510000`
- delta_vs_anchor_60: `-5.490000`
- delta_vs_anchor_raw: `-8.450000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 869 笔交易，覆盖 29 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=volatile_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： crypto, sports.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 可执行白名单主题：bitcoin, down, march, am-5, am-4, am-3.

## 5. 跟单风险
- 存在明显互斥市场并发多腿行为。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 硬黑名单主题（应避免）：bitcoin, down, march, nuggets, warriors, am-5.
- 软黑名单主题（需更严格触发）：heat, wizards, celtics, bulls, pistons, win.

## 6. 板块与关键词过滤
### 所属板块
- crypto
- sports

### 白名单关键词
- bitcoin
- down
- march
- am-5
- am-4
- am-3
- pm-6
- am-2
- pm-5
- pm-10
- clippers
- grizzlies

### 硬黑名单关键词
- bitcoin
- down
- march
- nuggets
- warriors
- am-5
- am-1
- am-3
- pm-3
- am-7
- am-6
- am-4

### 软黑名单关键词
- heat
- wizards
- celtics
- bulls
- pistons
- win
- nba
- angeles
- los
- jazz
- lightning
- avalanche

## 7. 账户概览
- analysis_window: `2026-03-11 19:11:19 UTC -> 2026-04-10 11:23:39 UTC`
- trade_rows_used: `869`
- total_buy_usdc: `107080.946301`
- total_sell_usdc: `20884.803765`
- traded_markets_count_api: `1056`
- position_value_api: `200.097900`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `15.66%`
- dual_side_buy_usdc_ratio_1h: `15.12%`
- token_fast_20m_buy_usdc_ratio: `6.64%`
- noncopyable_token_fast_buy_ratio: `1.81%`
- noncopyable_token_fast_sell_ratio: `9.31%`
- noncopyable_token_fast_token_ratio: `1.14%`
- event_rebalance_20m_event_ratio: `0.53%`
- exclusive_concurrent_leg_ratio: `46.96%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `4.99%`
- deployable_event_equivalent: `261.500000`
- deployable_event_density: `8.812063`
- active_trading_days: `29.000000`
- trade_count: `869.000000`
- avg_trades_per_active_day: `29.965517`

## 9. 收益曲线评估
- all_time_shape: `高波动上行`
- all_time_score: `6`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `15.950000`
- deployability_score: `20`
- multi_market_structure_score: `5.910000`
- pnl_curve_stability_score: `5.000000`
- risk_penalty_adjustment: `-8.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
