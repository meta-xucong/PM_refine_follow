# Tired-Webinar

## 账户身份（优先人工核对）
- 展示名称: `Tired-Webinar`
- 账户地址: `0xc86ada240605f98e885b8aaaf591fa56d6ddbcab`
- 平台昵称: `Tired-Webinar`
- 平台名称: `oreo142`
- 本地名称: `account_24`

## 1. 执行结论
校准后决策分 47.44（锚点口径），结论：只适合筛着跟。主要板块暴露：sports。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。白名单主题（优先筛选）：nuggets、hawks、spurs、pistons、wizards。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `47.440000`
- raw_score: `64`
- anchored_score: `47.440000`
- delta_vs_anchor_60: `-12.560000`
- delta_vs_anchor_raw: `-19.320000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 120 笔交易，覆盖 15 个活跃交易日（分析窗口内）。
- 低频封顶已生效，封顶分数为 64, ，表明可跟单容量受限。
- 收益曲线形态： 全周期=smooth_up, 30d=smooth_up, 7d=insufficient_data.
- 主要板块主题： sports.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 近 30 天收益曲线表现仍偏正向。
- 可执行白名单主题：nuggets, hawks, spurs, pistons, wizards, nets.

## 5. 跟单风险
- 交易频次/可利用度约束限制了实盘跟单容量。

## 6. 板块与关键词过滤
### 所属板块
- sports

### 白名单关键词
- nuggets
- hawks
- spurs
- pistons
- wizards
- nets
- celtics
- raptors
- bulls
- lakers
- hornets
- suns

### 硬黑名单关键词
- (none)

### 软黑名单关键词
- (none)

## 7. 账户概览
- analysis_window: `2026-03-26 18:55:19 UTC -> 2026-04-09 00:40:45 UTC`
- trade_rows_used: `120`
- total_buy_usdc: `64445.710421`
- total_sell_usdc: `105.385000`
- traded_markets_count_api: `36`
- position_value_api: `19.470500`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `0.00%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `0.08%`
- noncopyable_token_fast_buy_ratio: `0.06%`
- noncopyable_token_fast_sell_ratio: `48.01%`
- noncopyable_token_fast_token_ratio: `5.26%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `0.00%`
- deployable_event_equivalent: `18.000000`
- deployable_event_density: `1.359529`
- active_trading_days: `15.000000`
- trade_count: `120.000000`
- avg_trades_per_active_day: `8.000000`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `平滑上行`
- d30_score: `6`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `33.940000`
- deployability_score: `20`
- multi_market_structure_score: `20`
- pnl_curve_stability_score: `24.980000`
- risk_penalty_adjustment: `0`
- concentration_penalty: `0.000000`
- low_frequency_cap: `64`

## 11. 数据质量与假设
- (none)
