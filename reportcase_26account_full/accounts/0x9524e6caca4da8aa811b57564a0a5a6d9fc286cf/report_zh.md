# Crock95

## 账户身份（优先人工核对）
- 展示名称: `Crock95`
- 账户地址: `0x9524e6caca4da8aa811b57564a0a5a6d9fc286cf`
- 平台昵称: `Perfumed-Salmon`
- 平台名称: `Crock95`
- 本地名称: `account_7`

## 1. 执行结论
校准后决策分 68.52（锚点口径），结论：只适合筛着跟。主要板块暴露：sports、us_politics、geopolitics。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：存在同 condition 双边买入。硬黑名单主题（禁止跟）：win、election、seats、parliamentary、most。软黑名单主题（谨慎跟）：chamber、representatives、third、colombian、general。白名单主题（优先筛选）：league、premier、next、presidential、english。风险门槛已触发，宽跟模式自动关闭。重风险门槛已触发，低分情形会被强制判定为不值得跟。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `68.520000`
- raw_score: `60.410000`
- anchored_score: `68.520000`
- delta_vs_anchor_60: `8.520000`
- delta_vs_anchor_raw: `13.100000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 418 笔交易，覆盖 24 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： sports, us_politics, geopolitics.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 可执行白名单主题：league, premier, next, presidential, english, relegated.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 已触发重风险门槛，差质标的会被自动归为不值得跟。
- 硬黑名单主题（应避免）：win, election, seats, parliamentary, most, movement.
- 软黑名单主题（需更严格触发）：chamber, representatives, third, colombian, general, folketing.

## 6. 板块与关键词过滤
### 所属板块
- sports
- us_politics
- geopolitics

### 白名单关键词
- league
- premier
- next
- presidential
- english
- relegated
- forest
- season
- nottm
- denmark
- frederiksen
- elections

### 硬黑名单关键词
- win
- election
- seats
- parliamentary
- most
- movement
- slovenian
- freedom
- april
- russia
- ceasefire
- ukraine

### 软黑名单关键词
- chamber
- representatives
- third
- colombian
- general
- folketing
- danish
- second
- popular

## 7. 账户概览
- analysis_window: `2026-03-11 22:49:13 UTC -> 2026-04-10 16:59:51 UTC`
- trade_rows_used: `418`
- total_buy_usdc: `33418.598454`
- total_sell_usdc: `21605.810535`
- traded_markets_count_api: `401`
- position_value_api: `49111.486100`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `57.97%`
- dual_side_buy_usdc_ratio_1h: `53.73%`
- token_fast_20m_buy_usdc_ratio: `23.94%`
- noncopyable_token_fast_buy_ratio: `5.24%`
- noncopyable_token_fast_sell_ratio: `10.64%`
- noncopyable_token_fast_token_ratio: `2.13%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `1.42%`
- deployable_event_equivalent: `26.500000`
- deployable_event_density: `0.890535`
- active_trading_days: `24.000000`
- trade_count: `418.000000`
- avg_trades_per_active_day: `17.416667`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `19.420000`
- deployability_score: `20`
- multi_market_structure_score: `20`
- pnl_curve_stability_score: `9.990000`
- risk_penalty_adjustment: `-9.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
- 触发重风险门槛，不值得跟的判定阈值被收紧
