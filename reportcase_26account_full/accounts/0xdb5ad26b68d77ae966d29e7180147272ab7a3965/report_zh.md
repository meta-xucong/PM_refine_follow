# 0xDB5

## 账户身份（优先人工核对）
- 展示名称: `0xDB5`
- 账户地址: `0xdb5ad26b68d77ae966d29e7180147272ab7a3965`
- 平台昵称: `Intelligent-Length`
- 平台名称: `0xDB5`
- 本地名称: `account_25`

## 1. 执行结论
校准后决策分 29.25（锚点口径），结论：不值得跟。主要板块暴露：crypto。优势：不可复制快交易比例较低。风险点：递进型并存梯度风险偏高、存在同 condition 双边买入。硬黑名单主题（禁止跟）：price、above、march、bitcoin、ethereum。风险门槛已触发，宽跟模式自动关闭。重风险门槛已触发，低分情形会被强制判定为不值得跟。收益曲线标签：长期与近期均偏弱。不建议作为主跟单源，仅可少量人工挑选。

## 2. 决策快照
- decision: `不值得跟`
- final_score（决策分）: `29.250000`
- raw_score: `0`
- anchored_score: `29.250000`
- delta_vs_anchor_60: `-30.750000`
- delta_vs_anchor_raw: `-47.310000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 54793 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 低频封顶已生效，封顶分数为 48, ，表明可跟单容量受限。
- 收益曲线形态： 全周期=volatile_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： crypto.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 递进型并发梯度比例偏高，结构管理负担较重。
- 加权多子市场风险偏高。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 已触发重风险门槛，差质标的会被自动归为不值得跟。
- 交易频次/可利用度约束限制了实盘跟单容量。
- 硬黑名单主题（应避免）：price, above, march, bitcoin, ethereum, april.

## 6. 板块与关键词过滤
### 所属板块
- crypto

### 白名单关键词
- (none)

### 硬黑名单关键词
- price
- above
- march
- bitcoin
- ethereum
- april
- between
- dip
- reach
- greater
- less

### 软黑名单关键词
- (none)

## 7. 账户概览
- analysis_window: `2026-03-11 18:27:43 UTC -> 2026-04-10 18:26:11 UTC`
- trade_rows_used: `54793`
- total_buy_usdc: `2355327.289125`
- total_sell_usdc: `1772584.381055`
- traded_markets_count_api: `6729`
- position_value_api: `39958.246700`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `91.03%`
- dual_side_buy_usdc_ratio_1h: `21.13%`
- token_fast_20m_buy_usdc_ratio: `16.10%`
- noncopyable_token_fast_buy_ratio: `9.72%`
- noncopyable_token_fast_sell_ratio: `14.14%`
- noncopyable_token_fast_token_ratio: `26.91%`
- event_rebalance_20m_event_ratio: `95.97%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `86.45%`
- weighted_multi_market_risk_ratio: `47.54%`
- deployable_event_equivalent: `0.000000`
- deployable_event_density: `0.000000`
- active_trading_days: `31.000000`
- trade_count: `54793.000000`
- avg_trades_per_active_day: `1767.516129`

## 9. 收益曲线评估
- all_time_shape: `高波动上行`
- all_time_score: `6`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `0`
- deployability_score: `3.800000`
- multi_market_structure_score: `3.670000`
- pnl_curve_stability_score: `5.000000`
- risk_penalty_adjustment: `-18.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `48`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
- 触发重风险门槛，不值得跟的判定阈值被收紧
- 重风险门槛叠加低分，判定为不值得跟
- 校准分低于 32，触发不值得跟底线
