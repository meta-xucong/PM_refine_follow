# GoldmanSachs

## 账户身份（优先人工核对）
- 展示名称: `GoldmanSachs`
- 账户地址: `0x71dd2d539a793687451d4af8c43169369b47d61c`
- 平台昵称: `Knotty-Mud`
- 平台名称: `GoldmanSachs`
- 本地名称: `account_3`

## 1. 执行结论
校准后决策分 60.45（锚点口径），结论：只适合筛着跟。主要板块暴露：macro。优势：加权多子市场风险较低、不可复制快交易比例较低。软黑名单主题（谨慎跟）：chuck、warsh、federal、schumer、confirm。白名单主题（优先筛选）：change、rates、fed、interest、meeting。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `60.450000`
- raw_score: `48`
- anchored_score: `60.450000`
- delta_vs_anchor_60: `0.450000`
- delta_vs_anchor_raw: `0.690000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 15 笔交易，覆盖 7 个活跃交易日（分析窗口内）。
- 低频封顶已生效，封顶分数为 48, ，表明可跟单容量受限。
- 收益曲线形态： 全周期=smooth_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： macro.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 可执行白名单主题：change, rates, fed, interest, meeting, there.

## 5. 跟单风险
- 交易频次/可利用度约束限制了实盘跟单容量。
- 软黑名单主题（需更严格触发）：chuck, warsh, federal, schumer, confirm, chair.

## 6. 板块与关键词过滤
### 所属板块
- macro

### 白名单关键词
- change
- rates
- fed
- interest
- meeting
- there
- april
- march

### 硬黑名单关键词
- (none)

### 软黑名单关键词
- chuck
- warsh
- federal
- schumer
- confirm
- chair
- reserve
- vote
- kevin

## 7. 账户概览
- analysis_window: `2026-03-13 02:43:13 UTC -> 2026-04-03 13:23:21 UTC`
- trade_rows_used: `15`
- total_buy_usdc: `41191.958818`
- total_sell_usdc: `215.003199`
- traded_markets_count_api: `494`
- position_value_api: `21546.989300`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `0.00%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `0.00%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `0.00%`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `0.56%`
- deployable_event_equivalent: `5.500000`
- deployable_event_density: `0.256476`
- active_trading_days: `7.000000`
- trade_count: `15.000000`
- avg_trades_per_active_day: `2.142857`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `34.920000`
- deployability_score: `17.030000`
- multi_market_structure_score: `20`
- pnl_curve_stability_score: `9.990000`
- risk_penalty_adjustment: `-10.000000`
- concentration_penalty: `6.000000`
- low_frequency_cap: `48`

## 11. 数据质量与假设
- (none)
