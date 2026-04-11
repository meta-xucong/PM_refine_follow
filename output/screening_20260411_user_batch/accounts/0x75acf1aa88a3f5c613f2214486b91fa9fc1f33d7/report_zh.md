# Massive-Attainment

## 账户身份（优先人工核对）
- 展示名称: `Massive-Attainment`
- 账户地址: `0x75acf1aa88a3f5c613f2214486b91fa9fc1f33d7`
- 平台昵称: `Massive-Attainment`
- 平台名称: `badatthis`
- 本地名称: `account_23`

## 1. 执行结论
校准后决策分 64.91（锚点口径），结论：只适合筛着跟。主要板块暴露：us_politics、geopolitics、sports。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：递进型并存梯度风险偏高、存在同 condition 双边买入。硬黑名单主题（禁止跟）：trump、say、during、iran、march。软黑名单主题（谨慎跟）：strait、oil。白名单主题（优先筛选）：ukraine、russia、us-iran、nuclear、deal。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `64.910000`
- raw_score: `54.860000`
- anchored_score: `64.910000`
- delta_vs_anchor_60: `4.910000`
- delta_vs_anchor_raw: `7.550000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 4988 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： us_politics, geopolitics, sports.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 可执行白名单主题：ukraine, russia, us-iran, nuclear, deal, traffic.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 递进型并发梯度比例偏高，结构管理负担较重。
- 硬黑名单主题（应避免）：trump, say, during, iran, march, israel.
- 软黑名单主题（需更严格触发）：strait, oil.

## 6. 板块与关键词过滤
### 所属板块
- us_politics
- geopolitics
- sports

### 白名单关键词
- ukraine
- russia
- us-iran
- nuclear
- deal
- traffic
- normal
- returns
- another
- impeached
- meeting
- approval

### 硬黑名单关键词
- trump
- say
- during
- iran
- march
- israel
- april
- times
- announces
- end
- military
- against

### 软黑名单关键词
- strait
- oil

## 7. 账户概览
- analysis_window: `2026-03-12 15:10:19 UTC -> 2026-04-11 15:35:33 UTC`
- trade_rows_used: `4988`
- total_buy_usdc: `47801.389366`
- total_sell_usdc: `53066.616409`
- traded_markets_count_api: `3910`
- position_value_api: `2719.337700`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `35.63%`
- dual_side_buy_usdc_ratio_1h: `5.20%`
- token_fast_20m_buy_usdc_ratio: `18.27%`
- noncopyable_token_fast_buy_ratio: `6.74%`
- noncopyable_token_fast_sell_ratio: `7.65%`
- noncopyable_token_fast_token_ratio: `5.81%`
- event_rebalance_20m_event_ratio: `28.92%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `46.20%`
- weighted_multi_market_risk_ratio: `19.28%`
- deployable_event_equivalent: `40.500000`
- deployable_event_density: `1.349212`
- active_trading_days: `31.000000`
- trade_count: `4988.000000`
- avg_trades_per_active_day: `160.903226`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `16.320000`
- deployability_score: `20`
- multi_market_structure_score: `8.550000`
- pnl_curve_stability_score: `9.990000`
- risk_penalty_adjustment: `0`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
