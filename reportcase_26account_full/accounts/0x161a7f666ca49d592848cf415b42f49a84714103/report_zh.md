# torta.tech

## 账户身份（优先人工核对）
- 展示名称: `torta.tech`
- 账户地址: `0x161a7f666ca49d592848cf415b42f49a84714103`
- 平台昵称: `Imaginary-Gallery`
- 平台名称: `torta.tech`
- 本地名称: `account_1`

## 1. 执行结论
校准后决策分 50.56（锚点口径），结论：只适合筛着跟。主要板块暴露：sports。优势：可利用事件覆盖广、不可复制快交易比例较低。风险点：互斥型并存腿风险较高。硬黑名单主题（禁止跟）：spread、state、cavaliers、hawks、kings。软黑名单主题（谨慎跟）：win、ducks、rebels、green、missouri。白名单主题（优先筛选）：open、zhejiang、flames、beijing、nanjing。风险门槛已触发，宽跟模式自动关闭。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `50.560000`
- raw_score: `32.790000`
- anchored_score: `50.560000`
- delta_vs_anchor_60: `-9.440000`
- delta_vs_anchor_raw: `-14.520000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 13890 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： sports.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 可执行白名单主题：open, zhejiang, flames, beijing, nanjing, monkey.

## 5. 跟单风险
- 存在明显互斥市场并发多腿行为。
- 加权多子市场风险偏高。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 硬黑名单主题（应避免）：spread, state, cavaliers, hawks, kings, michigan.
- 软黑名单主题（需更严格触发）：win, ducks, rebels, green, missouri, bison.

## 6. 板块与关键词过滤
### 所属板块
- sports

### 白名单关键词
- open
- zhejiang
- flames
- beijing
- nanjing
- monkey
- king
- flying
- northeast
- jilin
- adelaide
- phoenix

### 硬黑名单关键词
- spread
- state
- cavaliers
- hawks
- kings
- michigan
- texas
- rockets
- ers
- raptors
- clippers
- blue

### 软黑名单关键词
- win
- ducks
- rebels
- green
- missouri
- bison
- gators
- redhawks
- unlv
- runnin
- austin
- stephen

## 7. 账户概览
- analysis_window: `2026-03-11 18:33:09 UTC -> 2026-04-10 18:24:37 UTC`
- trade_rows_used: `13890`
- total_buy_usdc: `1548259.408372`
- total_sell_usdc: `177662.092119`
- traded_markets_count_api: `9021`
- position_value_api: `37097.276100`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `9.57%`
- dual_side_buy_usdc_ratio_1h: `6.79%`
- token_fast_20m_buy_usdc_ratio: `5.80%`
- noncopyable_token_fast_buy_ratio: `1.87%`
- noncopyable_token_fast_sell_ratio: `13.12%`
- noncopyable_token_fast_token_ratio: `2.06%`
- event_rebalance_20m_event_ratio: `9.51%`
- exclusive_concurrent_leg_ratio: `57.39%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `44.43%`
- deployable_event_equivalent: `723.500000`
- deployable_event_density: `24.121431`
- active_trading_days: `31.000000`
- trade_count: `13890.000000`
- avg_trades_per_active_day: `448.064516`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `8.740000`
- deployability_score: `20`
- multi_market_structure_score: `2.060000`
- pnl_curve_stability_score: `9.990000`
- risk_penalty_adjustment: `-8.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
