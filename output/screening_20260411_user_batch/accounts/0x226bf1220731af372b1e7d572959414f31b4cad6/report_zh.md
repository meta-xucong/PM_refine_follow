# Shocking-Survey

## 账户身份（优先人工核对）
- 展示名称: `Shocking-Survey`
- 账户地址: `0x226bf1220731af372b1e7d572959414f31b4cad6`
- 平台昵称: `Shocking-Survey`
- 平台名称: `botbot`
- 本地名称: `account_40`

## 1. 执行结论
校准后决策分 63.76（锚点口径），结论：只适合筛着跟。主要板块暴露：sports、crypto。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。硬黑名单主题（禁止跟）：blue、duke、devils、state、siena。软黑名单主题（谨慎跟）：mets。白名单主题（优先筛选）：michigan、wolverines、carolina、north、heels。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `63.760000`
- raw_score: `89.110000`
- anchored_score: `63.760000`
- delta_vs_anchor_60: `3.760000`
- delta_vs_anchor_raw: `5.790000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 2972 笔交易，覆盖 23 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=smooth_up, 7d=insufficient_data.
- 主要板块主题： sports, crypto.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 近 30 天收益曲线表现仍偏正向。
- 可执行白名单主题：michigan, wolverines, carolina, north, heels, tar.

## 5. 跟单风险
- 硬黑名单主题（应避免）：blue, duke, devils, state, siena, saints.
- 软黑名单主题（需更严格触发）：mets.

## 6. 板块与关键词过滤
### 所属板块
- sports
- crypto

### 白名单关键词
- michigan
- wolverines
- carolina
- north
- heels
- tar
- rams
- vcu
- connecticut
- huskies
- alabama
- tide

### 硬黑名单关键词
- blue
- duke
- devils
- state
- siena
- saints
- texas
- longhorns
- carolina
- north
- wolfpack
- connecticut

### 软黑名单关键词
- mets

## 7. 账户概览
- analysis_window: `2026-03-12 15:17:31 UTC -> 2026-04-11 01:24:29 UTC`
- trade_rows_used: `2972`
- total_buy_usdc: `1037268.903122`
- total_sell_usdc: `661068.449447`
- traded_markets_count_api: `999`
- position_value_api: `1576.042700`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `2.71%`
- dual_side_buy_usdc_ratio_1h: `0.83%`
- token_fast_20m_buy_usdc_ratio: `1.00%`
- noncopyable_token_fast_buy_ratio: `0.80%`
- noncopyable_token_fast_sell_ratio: `1.31%`
- noncopyable_token_fast_token_ratio: `7.59%`
- event_rebalance_20m_event_ratio: `1.69%`
- exclusive_concurrent_leg_ratio: `14.01%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `10.01%`
- deployable_event_equivalent: `44.000000`
- deployable_event_density: `1.495505`
- active_trading_days: `23.000000`
- trade_count: `2972.000000`
- avg_trades_per_active_day: `129.217391`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `平滑上行`
- d30_score: `6`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `28.520000`
- deployability_score: `20`
- multi_market_structure_score: `15.620000`
- pnl_curve_stability_score: `24.980000`
- risk_penalty_adjustment: `0`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
