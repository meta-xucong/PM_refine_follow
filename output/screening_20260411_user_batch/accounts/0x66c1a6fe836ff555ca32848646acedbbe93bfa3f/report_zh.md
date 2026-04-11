# Fearless-Aggression

## 账户身份（优先人工核对）
- 展示名称: `Fearless-Aggression`
- 账户地址: `0x66c1a6fe836ff555ca32848646acedbbe93bfa3f`
- 平台昵称: `Fearless-Aggression`
- 平台名称: `Vermin-Supreme`
- 本地名称: `account_30`

## 1. 执行结论
校准后决策分 40.40（锚点口径），结论：不值得跟。主要板块暴露：us_politics、geopolitics、crypto。优势：可利用事件覆盖广、不可复制快交易比例较低。风险点：递进型并存梯度风险偏高、存在同 condition 双边买入。硬黑名单主题（禁止跟）：trump、say、march、during、visit。软黑名单主题（谨慎跟）：state、news、monday、behind、left。白名单主题（优先筛选）：donald、vance。风险门槛已触发，宽跟模式自动关闭。重风险门槛已触发，低分情形会被强制判定为不值得跟。收益曲线标签：长期与近期均偏弱。不建议作为主跟单源，仅可少量人工挑选。

## 2. 决策快照
- decision: `不值得跟`
- final_score（决策分）: `40.400000`
- raw_score: `17.160000`
- anchored_score: `40.400000`
- delta_vs_anchor_60: `-19.600000`
- delta_vs_anchor_raw: `-30.150000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 1720 笔交易，覆盖 30 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=down, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： us_politics, geopolitics, crypto.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 可执行白名单主题：donald, vance.

## 5. 跟单风险
- 递进型并发梯度比例偏高，结构管理负担较重。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 已触发重风险门槛，差质标的会被自动归为不值得跟。
- 全周期收益并非明显上行，持续优势可信度下降。
- 硬黑名单主题（应避免）：trump, say, march, during, visit, china.
- 软黑名单主题（需更严格触发）：state, news, monday, behind, left, strait.

## 6. 板块与关键词过滤
### 所属板块
- us_politics
- geopolitics
- crypto

### 白名单关键词
- donald
- vance

### 硬黑名单关键词
- trump
- say
- march
- during
- visit
- china
- white
- house
- iran
- april
- week
- events

### 软黑名单关键词
- state
- news
- monday
- behind
- left
- strait
- hormuz
- order
- executive
- signing
- episode
- all-in

## 7. 账户概览
- analysis_window: `2026-03-12 17:19:33 UTC -> 2026-04-10 18:10:41 UTC`
- trade_rows_used: `1720`
- total_buy_usdc: `105190.529253`
- total_sell_usdc: `73564.102803`
- traded_markets_count_api: `1977`
- position_value_api: `77201.951000`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `21.31%`
- dual_side_buy_usdc_ratio_1h: `0.58%`
- token_fast_20m_buy_usdc_ratio: `6.78%`
- noncopyable_token_fast_buy_ratio: `4.76%`
- noncopyable_token_fast_sell_ratio: `7.68%`
- noncopyable_token_fast_token_ratio: `6.23%`
- event_rebalance_20m_event_ratio: `38.10%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `81.93%`
- weighted_multi_market_risk_ratio: `33.04%`
- deployable_event_equivalent: `21.000000`
- deployable_event_density: `0.723252`
- active_trading_days: `30.000000`
- trade_count: `1720.000000`
- avg_trades_per_active_day: `57.333333`

## 9. 收益曲线评估
- all_time_shape: `下行`
- all_time_score: `-10`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `14.100000`
- deployability_score: `20`
- multi_market_structure_score: `4.390000`
- pnl_curve_stability_score: `-8.330000`
- risk_penalty_adjustment: `-13.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
- 触发重风险门槛，不值得跟的判定阈值被收紧
- 重风险门槛叠加低分，判定为不值得跟
