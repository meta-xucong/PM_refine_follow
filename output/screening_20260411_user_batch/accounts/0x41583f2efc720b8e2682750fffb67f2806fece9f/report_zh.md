# Pale-Semicolon

## 账户身份（优先人工核对）
- 展示名称: `Pale-Semicolon`
- 账户地址: `0x41583f2efc720b8e2682750fffb67f2806fece9f`
- 平台昵称: `Pale-Semicolon`
- 平台名称: `Toncar16`
- 本地名称: `account_16`

## 1. 执行结论
校准后决策分 57.56（锚点口径），结论：只适合筛着跟。主要板块暴露：geopolitics、us_politics、sports。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：递进型并存梯度风险偏高、存在同 condition 双边买入。硬黑名单主题（禁止跟）：iran、april、israel、election、ceasefire。软黑名单主题（谨慎跟）：china、trump。白名单主题（优先筛选）：military、against、announces、end、operations。收益曲线标签：长期/中期/短期均偏强。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `57.560000`
- raw_score: `79.560000`
- anchored_score: `57.560000`
- delta_vs_anchor_60: `-2.440000`
- delta_vs_anchor_raw: `-3.760000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 628 笔交易，覆盖 30 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=smooth_up, 7d=smooth_up.
- 主要板块主题： geopolitics, us_politics, sports.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 近 30 天收益曲线表现仍偏正向。
- 可执行白名单主题：military, against, announces, end, operations, cuba.

## 5. 跟单风险
- 递进型并发梯度比例偏高，结构管理负担较重。
- 硬黑名单主题（应避免）：iran, april, israel, election, ceasefire, paris.
- 软黑名单主题（需更严格触发）：china, trump.

## 6. 板块与关键词过滤
### 所属板块
- geopolitics
- us_politics
- sports

### 白名单关键词
- military
- against
- announces
- end
- operations
- cuba
- kharg
- iranian
- longer
- island
- control
- az-canel

### 硬黑名单关键词
- iran
- april
- israel
- election
- ceasefire
- paris
- municipal
- advance
- second
- sophia
- chikirou
- round

### 软黑名单关键词
- china
- trump

## 7. 账户概览
- analysis_window: `2026-03-13 08:03:57 UTC -> 2026-04-11 09:15:33 UTC`
- trade_rows_used: `628`
- total_buy_usdc: `31037.288488`
- total_sell_usdc: `47139.343353`
- traded_markets_count_api: `1410`
- position_value_api: `4534.973400`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `23.52%`
- dual_side_buy_usdc_ratio_1h: `3.65%`
- token_fast_20m_buy_usdc_ratio: `18.85%`
- noncopyable_token_fast_buy_ratio: `6.61%`
- noncopyable_token_fast_sell_ratio: `4.99%`
- noncopyable_token_fast_token_ratio: `7.95%`
- event_rebalance_20m_event_ratio: `11.76%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `45.43%`
- weighted_multi_market_risk_ratio: `16.17%`
- deployable_event_equivalent: `34.500000`
- deployable_event_density: `1.187619`
- active_trading_days: `30.000000`
- trade_count: `628.000000`
- avg_trades_per_active_day: `20.933333`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `平滑上行`
- d30_score: `6`
- d7_shape: `平滑上行`
- d7_score: `2`
- pnl_tag: `长期/中期/短期均偏强`

## 10. 评分拆解
- copyability_score: `19.790000`
- deployability_score: `20`
- multi_market_structure_score: `11.770000`
- pnl_curve_stability_score: `28`
- risk_penalty_adjustment: `0`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
