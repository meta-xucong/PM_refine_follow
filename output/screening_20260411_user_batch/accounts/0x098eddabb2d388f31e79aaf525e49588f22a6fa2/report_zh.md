# Youthful-Target

## 账户身份（优先人工核对）
- 展示名称: `Youthful-Target`
- 账户地址: `0x098eddabb2d388f31e79aaf525e49588f22a6fa2`
- 平台昵称: `Youthful-Target`
- 平台名称: `FreeCityIndividual`
- 本地名称: `account_17`

## 1. 执行结论
校准后决策分 58.24（锚点口径），结论：只适合筛着跟。主要板块暴露：sports、us_politics、macro。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：递进型并存梯度风险偏高。硬黑名单主题（禁止跟）：fed、win、michigan、tournament、league。软黑名单主题（谨慎跟）：presidential、nomination、republican、tucker、carlson。白名单主题（优先筛选）：chong、seoul、mayoral、won-oh、primary。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `58.240000`
- raw_score: `44.610000`
- anchored_score: `58.240000`
- delta_vs_anchor_60: `-1.760000`
- delta_vs_anchor_raw: `-2.700000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 852 笔交易，覆盖 30 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=volatile_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： sports, us_politics, macro.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 可执行白名单主题：chong, seoul, mayoral, won-oh, primary, march.

## 5. 跟单风险
- 递进型并发梯度比例偏高，结构管理负担较重。
- 硬黑名单主题（应避免）：fed, win, michigan, tournament, league, premier.
- 软黑名单主题（需更严格触发）：presidential, nomination, republican, tucker, carlson, democratic.

## 6. 板块与关键词过滤
### 所属板块
- sports
- us_politics
- macro

### 白名单关键词
- chong
- seoul
- mayoral
- won-oh
- primary
- march
- nominee
- december
- fall
- regime
- iranian
- day

### 硬黑名单关键词
- fed
- win
- michigan
- tournament
- league
- premier
- english
- ncaa
- devils
- duke
- blue
- scorer

### 软黑名单关键词
- presidential
- nomination
- republican
- tucker
- carlson
- democratic
- newsom
- gavin
- cuts
- happen
- rate
- eurovision

## 7. 账户概览
- analysis_window: `2026-03-13 00:16:37 UTC -> 2026-04-11 15:37:55 UTC`
- trade_rows_used: `852`
- total_buy_usdc: `21359.830014`
- total_sell_usdc: `4920.615642`
- traded_markets_count_api: `3805`
- position_value_api: `18746.968800`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `16.71%`
- dual_side_buy_usdc_ratio_1h: `14.28%`
- token_fast_20m_buy_usdc_ratio: `8.34%`
- noncopyable_token_fast_buy_ratio: `3.70%`
- noncopyable_token_fast_sell_ratio: `22.58%`
- noncopyable_token_fast_token_ratio: `2.75%`
- event_rebalance_20m_event_ratio: `5.00%`
- exclusive_concurrent_leg_ratio: `1.31%`
- nested_concurrent_leg_ratio: `75.79%`
- weighted_multi_market_risk_ratio: `15.36%`
- deployable_event_equivalent: `53.000000`
- deployable_event_density: `1.788137`
- active_trading_days: `30.000000`
- trade_count: `852.000000`
- avg_trades_per_active_day: `28.400000`

## 9. 收益曲线评估
- all_time_shape: `高波动上行`
- all_time_score: `6`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `18.320000`
- deployability_score: `20`
- multi_market_structure_score: `7.300000`
- pnl_curve_stability_score: `5.000000`
- risk_penalty_adjustment: `-6.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
