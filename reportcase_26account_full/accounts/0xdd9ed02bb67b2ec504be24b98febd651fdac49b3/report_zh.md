# Mamaozinho

## 账户身份（优先人工核对）
- 展示名称: `Mamaozinho`
- 账户地址: `0xdd9ed02bb67b2ec504be24b98febd651fdac49b3`
- 平台昵称: `Dry-Legislature`
- 平台名称: `Mamaozinho`
- 本地名称: `account_10`

## 1. 执行结论
校准后决策分 54.24（锚点口径），结论：只适合筛着跟。主要板块暴露：sports、us_politics、geopolitics。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：递进型并存梯度风险偏高、存在同 condition 双边买入。硬黑名单主题（禁止跟）：win、election、presidential、brazilian、vio。软黑名单主题（谨慎跟）：peruvian、rafael、aliaga、pez。风险门槛已触发，宽跟模式自动关闭。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `54.240000`
- raw_score: `38.450000`
- anchored_score: `54.240000`
- delta_vs_anchor_60: `-5.760000`
- delta_vs_anchor_raw: `-8.860000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 6914 笔交易，覆盖 24 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=volatile_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： sports, us_politics, geopolitics.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 加权多子市场结构风险整体可控。

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 递进型并发梯度比例偏高，结构管理负担较重。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 硬黑名单主题（应避免）：win, election, presidential, brazilian, vio, bolsonaro.
- 软黑名单主题（需更严格触发）：peruvian, rafael, aliaga, pez.

## 6. 板块与关键词过滤
### 所属板块
- sports
- us_politics
- geopolitics

### 白名单关键词
- (none)

### 硬黑名单关键词
- win
- election
- presidential
- brazilian
- vio
- bolsonaro
- world
- iran
- cup
- fifa
- abelardo
- colombian

### 软黑名单关键词
- peruvian
- rafael
- aliaga
- pez

## 7. 账户概览
- analysis_window: `2026-03-13 04:33:45 UTC -> 2026-04-10 18:15:13 UTC`
- trade_rows_used: `6914`
- total_buy_usdc: `51856.950056`
- total_sell_usdc: `36874.476680`
- traded_markets_count_api: `924`
- position_value_api: `14230.098400`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `36.71%`
- dual_side_buy_usdc_ratio_1h: `6.51%`
- token_fast_20m_buy_usdc_ratio: `6.62%`
- noncopyable_token_fast_buy_ratio: `0.82%`
- noncopyable_token_fast_sell_ratio: `2.23%`
- noncopyable_token_fast_token_ratio: `4.20%`
- event_rebalance_20m_event_ratio: `28.57%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `63.68%`
- weighted_multi_market_risk_ratio: `15.50%`
- deployable_event_equivalent: `9.000000`
- deployable_event_density: `0.315011`
- active_trading_days: `24.000000`
- trade_count: `6914.000000`
- avg_trades_per_active_day: `288.083333`

## 9. 收益曲线评估
- all_time_shape: `高波动上行`
- all_time_score: `6`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `16.150000`
- deployability_score: `20`
- multi_market_structure_score: `7.310000`
- pnl_curve_stability_score: `5.000000`
- risk_penalty_adjustment: `-10.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
