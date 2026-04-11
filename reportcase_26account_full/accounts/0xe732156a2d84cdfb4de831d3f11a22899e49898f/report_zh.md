# Nostdam

## 账户身份（优先人工核对）
- 展示名称: `Nostdam`
- 账户地址: `0xe732156a2d84cdfb4de831d3f11a22899e49898f`
- 平台昵称: `Glossy-Statute`
- 平台名称: `Nostdam`
- 本地名称: `account_21`

## 1. 执行结论
校准后决策分 32.80（锚点口径），结论：不值得跟。主要板块暴露：sports、geopolitics、us_politics。优势：可利用事件覆盖广、加权多子市场风险较低。风险点：互斥型并存腿风险较高、递进型并存梯度风险偏高、存在不可复制的 token 快交易暴露、存在同 condition 双边买入。硬黑名单主题（禁止跟）：oilers、state、north、carolina、spread。软黑名单主题（谨慎跟）：open、bully、volunteers、tennessee。白名单主题（优先筛选）：out、netanyahu、trump、sinners、swift。风险门槛已触发，宽跟模式自动关闭。重风险门槛已触发，低分情形会被强制判定为不值得跟。收益曲线标签：长期与近期均偏弱。不建议作为主跟单源，仅可少量人工挑选。

## 2. 决策快照
- decision: `不值得跟`
- final_score（决策分）: `32.800000`
- raw_score: `5.470000`
- anchored_score: `32.800000`
- delta_vs_anchor_60: `-27.200000`
- delta_vs_anchor_raw: `-41.840000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 3394 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=flat, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： sports, geopolitics, us_politics.

## 4. 跟单优势
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 可执行白名单主题：out, netanyahu, trump, sinners, swift, taylor.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 不可复制的 token 快交易（BUY）比例偏高，收益更依赖执行优势。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 已触发重风险门槛，差质标的会被自动归为不值得跟。
- 全周期收益并非明显上行，持续优势可信度下降。
- 硬黑名单主题（应避免）：oilers, state, north, carolina, spread, texas.
- 软黑名单主题（需更严格触发）：open, bully, volunteers, tennessee.

## 6. 板块与关键词过滤
### 所属板块
- sports
- geopolitics
- us_politics

### 白名单关键词
- out
- netanyahu
- trump
- sinners
- swift
- taylor
- june
- khamenei
- public
- houston
- cougars
- hit

### 硬黑名单关键词
- oilers
- state
- north
- carolina
- spread
- texas
- longhorns
- wolfpack
- between
- panthers
- blues
- miami

### 软黑名单关键词
- open
- bully
- volunteers
- tennessee

## 7. 账户概览
- analysis_window: `2026-03-11 21:57:51 UTC -> 2026-04-10 16:05:01 UTC`
- trade_rows_used: `3394`
- total_buy_usdc: `154867.816093`
- total_sell_usdc: `146358.132716`
- traded_markets_count_api: `2466`
- position_value_api: `928.242900`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `47.39%`
- dual_side_buy_usdc_ratio_1h: `36.92%`
- token_fast_20m_buy_usdc_ratio: `67.98%`
- noncopyable_token_fast_buy_ratio: `55.10%`
- noncopyable_token_fast_sell_ratio: `59.28%`
- noncopyable_token_fast_token_ratio: `29.94%`
- event_rebalance_20m_event_ratio: `16.15%`
- exclusive_concurrent_leg_ratio: `21.68%`
- nested_concurrent_leg_ratio: `43.12%`
- weighted_multi_market_risk_ratio: `19.80%`
- deployable_event_equivalent: `77.000000`
- deployable_event_density: `2.587802`
- active_trading_days: `31.000000`
- trade_count: `3394.000000`
- avg_trades_per_active_day: `109.483871`

## 9. 收益曲线评估
- all_time_shape: `走平`
- all_time_score: `1`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `0`
- deployability_score: `20`
- multi_market_structure_score: `1.640000`
- pnl_curve_stability_score: `0.830000`
- risk_penalty_adjustment: `-17.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
- 触发重风险门槛，不值得跟的判定阈值被收紧
- 重风险门槛叠加低分，判定为不值得跟
