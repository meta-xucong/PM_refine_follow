# Testy-Operator

## 账户身份（优先人工核对）
- 展示名称: `Testy-Operator`
- 账户地址: `0x80a4552cdcde3b861b8adc146ab1fbd4711022cc`
- 平台昵称: `Testy-Operator`
- 平台名称: `puravida`
- 本地名称: `account_14`

## 1. 执行结论
校准后决策分 35.82（锚点口径），结论：不值得跟。主要板块暴露：geopolitics、macro、sports。优势：可利用事件覆盖广、加权多子市场风险较低。风险点：互斥型并存腿风险较高、存在不可复制的 token 快交易暴露、存在同 condition 双边买入。硬黑名单主题（禁止跟）：iran、april、ceasefire、december、enter。软黑名单主题（谨慎跟）：world、cup、fifa、brazil、trump。白名单主题（优先筛选）：iranian、regime、fall、june、end。风险门槛已触发，宽跟模式自动关闭。收益曲线标签：长期/中期/短期均偏强。不建议作为主跟单源，仅可少量人工挑选。

## 2. 决策快照
- decision: `不值得跟`
- final_score（决策分）: `35.820000`
- raw_score: `46.120000`
- anchored_score: `35.820000`
- delta_vs_anchor_60: `-24.180000`
- delta_vs_anchor_raw: `-37.200000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 1360 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=smooth_up, 7d=smooth_up.
- 主要板块主题： geopolitics, macro, sports.

## 4. 跟单优势
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 近 30 天收益曲线表现仍偏正向。
- 可执行白名单主题：iranian, regime, fall, june, end, illinois.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 不可复制的 token 快交易（BUY）比例偏高，收益更依赖执行优势。
- 存在明显互斥市场并发多腿行为。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 硬黑名单主题（应避免）：iran, april, ceasefire, december, enter, forces.
- 软黑名单主题（需更严格触发）：world, cup, fifa, brazil, trump, inflation.

## 6. 板块与关键词过滤
### 所属板块
- geopolitics
- macro
- sports

### 白名单关键词
- iranian
- regime
- fall
- june
- end
- illinois
- illini
- fighting
- win
- march
- iowa
- hawkeyes

### 硬黑名单关键词
- iran
- april
- ceasefire
- december
- enter
- forces
- fed
- spread
- bound
- parliamentary
- duke
- devils

### 软黑名单关键词
- world
- cup
- fifa
- brazil
- trump
- inflation
- increase
- july

## 7. 账户概览
- analysis_window: `2026-03-12 16:21:07 UTC -> 2026-04-11 15:26:33 UTC`
- trade_rows_used: `1360`
- total_buy_usdc: `50021.292998`
- total_sell_usdc: `38509.659160`
- traded_markets_count_api: `1429`
- position_value_api: `30738.730400`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `30.99%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `34.39%`
- noncopyable_token_fast_buy_ratio: `21.48%`
- noncopyable_token_fast_sell_ratio: `24.84%`
- noncopyable_token_fast_token_ratio: `5.61%`
- event_rebalance_20m_event_ratio: `2.78%`
- exclusive_concurrent_leg_ratio: `49.05%`
- nested_concurrent_leg_ratio: `15.10%`
- weighted_multi_market_risk_ratio: `11.80%`
- deployable_event_equivalent: `57.500000`
- deployable_event_density: `1.919091`
- active_trading_days: `31.000000`
- trade_count: `1360.000000`
- avg_trades_per_active_day: `43.870968`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `平滑上行`
- d30_score: `6`
- d7_shape: `平滑上行`
- d7_score: `2`
- pnl_tag: `长期/中期/短期均偏强`

## 10. 评分拆解
- copyability_score: `3.370000`
- deployability_score: `20`
- multi_market_structure_score: `2.750000`
- pnl_curve_stability_score: `28`
- risk_penalty_adjustment: `-8.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
