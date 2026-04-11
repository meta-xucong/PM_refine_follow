# Corrupt-Apartment

## 账户身份（优先人工核对）
- 展示名称: `Corrupt-Apartment`
- 账户地址: `0x48e7ca9d4754021dc8b32adcaec0234dd6c9d5f8`
- 平台昵称: `Corrupt-Apartment`
- 平台名称: `Zippy`
- 本地名称: `account_20`

## 1. 执行结论
校准后决策分 55.91（锚点口径），结论：只适合筛着跟。主要板块暴露：entertainment。优势：加权多子市场风险较低、不可复制快交易比例较低。风险点：存在同 condition 双边买入。硬黑名单主题（禁止跟）：grossing、top、movie、jumanji。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `55.910000`
- raw_score: `41.020000`
- anchored_score: `55.910000`
- delta_vs_anchor_60: `-4.090000`
- delta_vs_anchor_raw: `-6.290000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 674 笔交易，覆盖 30 个活跃交易日（分析窗口内）。
- 低频封顶已生效，封顶分数为 48, ，表明可跟单容量受限。
- 收益曲线形态： 全周期=smooth_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： entertainment.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 全周期收益曲线为平滑上行，策略一致性较好。

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 交易频次/可利用度约束限制了实盘跟单容量。
- 硬黑名单主题（应避免）：grossing, top, movie, jumanji.

## 6. 板块与关键词过滤
### 所属板块
- entertainment

### 白名单关键词
- (none)

### 硬黑名单关键词
- grossing
- top
- movie
- jumanji

### 软黑名单关键词
- (none)

## 7. 账户概览
- analysis_window: `2026-03-11 18:31:33 UTC -> 2026-04-10 15:30:39 UTC`
- trade_rows_used: `674`
- total_buy_usdc: `7037.874812`
- total_sell_usdc: `3969.088767`
- traded_markets_count_api: `362`
- position_value_api: `6580.370500`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `38.97%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `0.00%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `0.00%`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `50.00%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `15.00%`
- deployable_event_equivalent: `0.500000`
- deployable_event_density: `0.016737`
- active_trading_days: `30.000000`
- trade_count: `674.000000`
- avg_trades_per_active_day: `22.466667`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `23.550000`
- deployability_score: `4.980000`
- multi_market_structure_score: `17.500000`
- pnl_curve_stability_score: `9.990000`
- risk_penalty_adjustment: `0`
- concentration_penalty: `15.000000`
- low_frequency_cap: `48`

## 11. 数据质量与假设
- (none)
