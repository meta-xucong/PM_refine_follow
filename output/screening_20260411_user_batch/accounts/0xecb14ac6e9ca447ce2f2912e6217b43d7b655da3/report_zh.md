# Loathsome-Decade

## 账户身份（优先人工核对）
- 展示名称: `Loathsome-Decade`
- 账户地址: `0xecb14ac6e9ca447ce2f2912e6217b43d7b655da3`
- 平台昵称: `Loathsome-Decade`
- 平台名称: `SaylorMoon`
- 本地名称: `account_37`

## 1. 执行结论
校准后决策分 29.02（锚点口径），结论：不值得跟。主要板块暴露：geopolitics、sports、us_politics。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：互斥型并存腿风险较高、递进型并存梯度风险偏高、存在同 condition 双边买入。硬黑名单主题（禁止跟）：miami、march、iran、forces、enter。软黑名单主题（谨慎跟）：rams、vcu、week、album、sales。白名单主题（优先筛选）：netanyahu、out、duke、devils、blue。风险门槛已触发，宽跟模式自动关闭。收益曲线标签：长期/中期/短期均偏强。不建议作为主跟单源，仅可少量人工挑选。

## 2. 决策快照
- decision: `不值得跟`
- final_score（决策分）: `29.020000`
- raw_score: `35.660000`
- anchored_score: `29.020000`
- delta_vs_anchor_60: `-30.980000`
- delta_vs_anchor_raw: `-47.660000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 2201 笔交易，覆盖 25 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=volatile_up, 30d=smooth_up, 7d=smooth_up.
- 主要板块主题： geopolitics, sports, us_politics.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 近 30 天收益曲线表现仍偏正向。
- 可执行白名单主题：netanyahu, out, duke, devils, blue, red.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 存在明显互斥市场并发多腿行为。
- 递进型并发梯度比例偏高，结构管理负担较重。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 硬黑名单主题（应避免）：miami, march, iran, forces, enter, michigan.
- 软黑名单主题（需更严格触发）：rams, vcu, week, album, sales, debut.

## 6. 板块与关键词过滤
### 所属板块
- geopolitics
- sports
- us_politics

### 白名单关键词
- netanyahu
- out
- duke
- devils
- blue
- red
- raiders
- tech
- siena
- saints
- cardinals
- louisville

### 硬黑名单关键词
- miami
- march
- iran
- forces
- enter
- michigan
- wolverines
- state
- huskies
- connecticut
- hurricanes
- redhawks

### 软黑名单关键词
- rams
- vcu
- week
- album
- sales
- debut

## 7. 账户概览
- analysis_window: `2026-03-12 23:05:39 UTC -> 2026-04-11 02:54:01 UTC`
- trade_rows_used: `2201`
- total_buy_usdc: `542518.133405`
- total_sell_usdc: `212401.296081`
- traded_markets_count_api: `2074`
- position_value_api: `114448.434300`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `37.91%`
- dual_side_buy_usdc_ratio_1h: `15.42%`
- token_fast_20m_buy_usdc_ratio: `8.48%`
- noncopyable_token_fast_buy_ratio: `6.49%`
- noncopyable_token_fast_sell_ratio: `8.87%`
- noncopyable_token_fast_token_ratio: `6.09%`
- event_rebalance_20m_event_ratio: `3.85%`
- exclusive_concurrent_leg_ratio: `46.72%`
- nested_concurrent_leg_ratio: `69.67%`
- weighted_multi_market_risk_ratio: `6.74%`
- deployable_event_equivalent: `51.500000`
- deployable_event_density: `1.766203`
- active_trading_days: `25.000000`
- trade_count: `2201.000000`
- avg_trades_per_active_day: `88.040000`

## 9. 收益曲线评估
- all_time_shape: `高波动上行`
- all_time_score: `6`
- d30_shape: `平滑上行`
- d30_score: `6`
- d7_shape: `平滑上行`
- d7_score: `2`
- pnl_tag: `长期/中期/短期均偏强`

## 10. 评分拆解
- copyability_score: `0.760000`
- deployability_score: `20`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `25.900000`
- risk_penalty_adjustment: `-11.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
- 校准分低于 32，触发不值得跟底线
