# Gloomy-Date

## 账户身份（优先人工核对）
- 展示名称: `Gloomy-Date`
- 账户地址: `0x30ceffb3ac4ea49881e271d5a69883b60e0dfdce`
- 平台昵称: `Gloomy-Date`
- 平台名称: `AshleySchaeffer`
- 本地名称: `account_26`

## 1. 执行结论
校准后决策分 39.28（锚点口径），结论：不值得跟。主要板块暴露：sports、geopolitics。优势：可利用事件覆盖广、加权多子市场风险较低。风险点：互斥型并存腿风险较高、存在不可复制的 token 快交易暴露、存在同 condition 双边买入。硬黑名单主题（禁止跟）：win、draw、end、chelsea、barcelona。软黑名单主题（谨慎跟）：golden、knights、morocco、ecuador、vit。白名单主题（优先筛选）：france。风险门槛已触发，宽跟模式自动关闭。重风险门槛已触发，低分情形会被强制判定为不值得跟。收益曲线标签：长期与近期均偏弱。不建议作为主跟单源，仅可少量人工挑选。

## 2. 决策快照
- decision: `不值得跟`
- final_score（决策分）: `39.280000`
- raw_score: `15.430000`
- anchored_score: `39.280000`
- delta_vs_anchor_60: `-20.720000`
- delta_vs_anchor_raw: `-31.880000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 4373 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=volatile_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： sports, geopolitics.

## 4. 跟单优势
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 可执行白名单主题：france.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 不可复制的 token 快交易（BUY）比例偏高，收益更依赖执行优势。
- 存在明显互斥市场并发多腿行为。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 已触发重风险门槛，差质标的会被自动归为不值得跟。
- 硬黑名单主题（应避免）：win, draw, end, chelsea, barcelona, sabres.
- 软黑名单主题（需更严格触发）：golden, knights, morocco, ecuador, vit, ria.

## 6. 板块与关键词过滤
### 所属板块
- sports
- geopolitics

### 白名单关键词
- france

### 硬黑名单关键词
- win
- draw
- end
- chelsea
- barcelona
- sabres
- hurricanes
- united
- jackets
- blue
- red
- bruins

### 软黑名单关键词
- golden
- knights
- morocco
- ecuador
- vit
- ria
- athletic

## 7. 账户概览
- analysis_window: `2026-03-11 19:16:23 UTC -> 2026-04-10 03:10:47 UTC`
- trade_rows_used: `4373`
- total_buy_usdc: `350401.129641`
- total_sell_usdc: `283928.376464`
- traded_markets_count_api: `822`
- position_value_api: `24.949400`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `88.48%`
- dual_side_buy_usdc_ratio_1h: `48.58%`
- token_fast_20m_buy_usdc_ratio: `69.63%`
- noncopyable_token_fast_buy_ratio: `48.71%`
- noncopyable_token_fast_sell_ratio: `64.99%`
- noncopyable_token_fast_token_ratio: `31.40%`
- event_rebalance_20m_event_ratio: `41.62%`
- exclusive_concurrent_leg_ratio: `32.34%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `11.53%`
- deployable_event_equivalent: `30.000000`
- deployable_event_density: `1.022863`
- active_trading_days: `31.000000`
- trade_count: `4373.000000`
- avg_trades_per_active_day: `141.064516`

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
- deployability_score: `20`
- multi_market_structure_score: `7.440000`
- pnl_curve_stability_score: `5.000000`
- risk_penalty_adjustment: `-17.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
- 触发重风险门槛，不值得跟的判定阈值被收紧
- 重风险门槛叠加低分，判定为不值得跟
