# intrepid

## 账户身份（优先人工核对）
- 展示名称: `intrepid`
- 账户地址: `0xd66f79a8d19d4223b6c70dd4e620d4875501a19b`
- 平台昵称: `Harmonious-Witchhunt`
- 平台名称: `intrepid`
- 本地名称: `account_17`

## 1. 执行结论
校准后决策分 59.40（锚点口径），结论：只适合筛着跟。主要板块暴露：sports、geopolitics。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：存在同 condition 双边买入。硬黑名单主题（禁止跟）：win、united、madrid、real、manchester。软黑名单主题（谨慎跟）：villa、aston。白名单主题（优先筛选）：march。风险门槛已触发，宽跟模式自动关闭。重风险门槛已触发，低分情形会被强制判定为不值得跟。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `59.400000`
- raw_score: `46.390000`
- anchored_score: `59.400000`
- delta_vs_anchor_60: `-0.600000`
- delta_vs_anchor_raw: `-0.920000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 3671 笔交易，覆盖 18 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=volatile_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： sports, geopolitics.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可执行白名单主题：march.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 已触发重风险门槛，差质标的会被自动归为不值得跟。
- 硬黑名单主题（应避免）：win, united, madrid, real, manchester, liverpool.
- 软黑名单主题（需更严格触发）：villa, aston.

## 6. 板块与关键词过滤
### 所属板块
- sports
- geopolitics

### 白名单关键词
- march

### 硬黑名单关键词
- win
- united
- madrid
- real
- manchester
- liverpool
- forest
- nottingham
- arsenal
- city
- newcastle
- draw

### 软黑名单关键词
- villa
- aston

## 7. 账户概览
- analysis_window: `2026-03-11 18:49:19 UTC -> 2026-04-09 19:05:39 UTC`
- trade_rows_used: `3671`
- total_buy_usdc: `357851.317187`
- total_sell_usdc: `0`
- traded_markets_count_api: `1181`
- position_value_api: `0.000000`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `93.81%`
- dual_side_buy_usdc_ratio_1h: `92.21%`
- token_fast_20m_buy_usdc_ratio: `0.00%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `n/a`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `14.90%`
- deployable_event_equivalent: `10.000000`
- deployable_event_density: `0.344693`
- active_trading_days: `18.000000`
- trade_count: `3671.000000`
- avg_trades_per_active_day: `203.944444`

## 9. 收益曲线评估
- all_time_shape: `高波动上行`
- all_time_score: `6`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `10.400000`
- deployability_score: `20`
- multi_market_structure_score: `20`
- pnl_curve_stability_score: `5.000000`
- risk_penalty_adjustment: `-9.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
- 触发重风险门槛，不值得跟的判定阈值被收紧
- 未匹配到可用 SELL 库存，持仓时长指标不可用
