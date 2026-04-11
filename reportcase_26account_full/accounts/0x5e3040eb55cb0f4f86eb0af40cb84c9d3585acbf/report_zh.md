# slimjoe

## 账户身份（优先人工核对）
- 展示名称: `slimjoe`
- 账户地址: `0x5e3040eb55cb0f4f86eb0af40cb84c9d3585acbf`
- 平台昵称: `Gargantuan-Heater`
- 平台名称: `slimjoe`
- 本地名称: `account_29`

## 1. 执行结论
校准后决策分 41.59（锚点口径），结论：不值得跟。主要板块暴露：sports。优势：可利用事件覆盖广、不可复制快交易比例较低。风险点：互斥型并存腿风险较高、递进型并存梯度风险偏高、存在同 condition 双边买入。硬黑名单主题（禁止跟）：set、spread、handicap、moneyline、open。软黑名单主题（谨慎跟）：madrid、halftime、red、city、real。白名单主题（优先筛选）：win、liverpool、club、sharks、end。风险门槛已触发，宽跟模式自动关闭。重风险门槛已触发，低分情形会被强制判定为不值得跟。收益曲线标签：长期与近期均偏弱。不建议作为主跟单源，仅可少量人工挑选。

## 2. 决策快照
- decision: `不值得跟`
- final_score（决策分）: `41.590000`
- raw_score: `18.990000`
- anchored_score: `41.590000`
- delta_vs_anchor_60: `-18.410000`
- delta_vs_anchor_raw: `-28.320000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 13787 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： sports.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 可执行白名单主题：win, liverpool, club, sharks, end, twins.

## 5. 跟单风险
- 存在明显互斥市场并发多腿行为。
- 递进型并发梯度比例偏高，结构管理负担较重。
- 加权多子市场风险偏高。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 已触发重风险门槛，差质标的会被自动归为不值得跟。
- 硬黑名单主题（应避免）：set, spread, handicap, moneyline, open, miami.
- 软黑名单主题（需更严格触发）：madrid, halftime, red, city, real, one.

## 6. 板块与关键词过滤
### 所属板块
- sports

### 白名单关键词
- win
- liverpool
- club
- sharks
- end
- twins
- minnesota
- penguins
- brighton
- hove
- albion
- calcio

### 硬黑名单关键词
- set
- spread
- handicap
- moneyline
- open
- miami
- match
- sets
- total
- games
- winner
- rounds

### 软黑名单关键词
- madrid
- halftime
- red
- city
- real
- one
- credit
- charleston
- leading
- new
- york
- chicago

## 7. 账户概览
- analysis_window: `2026-03-11 18:27:29 UTC -> 2026-04-10 18:21:57 UTC`
- trade_rows_used: `13787`
- total_buy_usdc: `1247861.585367`
- total_sell_usdc: `0`
- traded_markets_count_api: `12272`
- position_value_api: `32297.324600`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `26.62%`
- dual_side_buy_usdc_ratio_1h: `14.35%`
- token_fast_20m_buy_usdc_ratio: `0.00%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `n/a`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `69.73%`
- nested_concurrent_leg_ratio: `61.55%`
- weighted_multi_market_risk_ratio: `49.54%`
- deployable_event_equivalent: `1319.000000`
- deployable_event_density: `43.972299`
- active_trading_days: `31.000000`
- trade_count: `13787.000000`
- avg_trades_per_active_day: `444.741935`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `0`
- deployability_score: `20`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `9.990000`
- risk_penalty_adjustment: `-11.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
- 触发重风险门槛，不值得跟的判定阈值被收紧
- 重风险门槛叠加低分，判定为不值得跟
- 未匹配到可用 SELL 库存，持仓时长指标不可用
