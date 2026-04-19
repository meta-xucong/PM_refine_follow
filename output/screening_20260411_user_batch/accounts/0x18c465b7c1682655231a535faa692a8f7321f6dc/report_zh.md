# Sinful-Gasp

## 账户身份（优先人工核对）
- 展示名称: `Sinful-Gasp`
- 账户地址: `0x18c465b7c1682655231a535faa692a8f7321f6dc`
- 平台昵称: `Sinful-Gasp`
- 平台名称: `memento-mori`
- 本地名称: `account_35`

## 1. 执行结论
校准后决策分 49.91（锚点口径），结论：只适合筛着跟。主要板块暴露：sports、geopolitics、us_politics。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：互斥型并存腿风险较高。硬黑名单主题（禁止跟）：poland、sweden。软黑名单主题（谨慎跟）：nba。白名单主题（优先筛选）：win、madrid、real、tico、atl。收益曲线标签：长期/中期/短期均偏强。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `49.910000`
- raw_score: `67.800000`
- anchored_score: `49.910000`
- delta_vs_anchor_60: `-10.090000`
- delta_vs_anchor_raw: `-15.520000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 1675 笔交易，覆盖 23 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=volatile_up, 30d=volatile_up, 7d=smooth_up.
- 主要板块主题： sports, geopolitics, us_politics.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 可执行白名单主题：win, madrid, real, tico, atl, club.

## 5. 跟单风险
- 存在明显互斥市场并发多腿行为。
- 硬黑名单主题（应避免）：poland, sweden.
- 软黑名单主题（需更严格触发）：nba.

## 6. 板块与关键词过滤
### 所属板块
- sports
- geopolitics
- us_politics

### 白名单关键词
- win
- madrid
- real
- tico
- atl
- club
- barcelona
- sociedad
- tbol
- germany
- united
- bournemouth

### 硬黑名单关键词
- poland
- sweden

### 软黑名单关键词
- nba

## 7. 账户概览
- analysis_window: `2026-03-14 16:12:41 UTC -> 2026-04-11 13:27:35 UTC`
- trade_rows_used: `1675`
- total_buy_usdc: `295336.989903`
- total_sell_usdc: `124756.457204`
- traded_markets_count_api: `157`
- position_value_api: `30769.253200`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `0.00%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `1.97%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `0.00%`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `42.25%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `2.54%`
- deployable_event_equivalent: `54.500000`
- deployable_event_density: `1.954431`
- active_trading_days: `23.000000`
- trade_count: `1675.000000`
- avg_trades_per_active_day: `72.826087`

## 9. 收益曲线评估
- all_time_shape: `高波动上行`
- all_time_score: `6`
- d30_shape: `高波动上行`
- d30_score: `2`
- d7_shape: `平滑上行`
- d7_score: `2`
- pnl_tag: `长期/中期/短期均偏强`

## 10. 评分拆解
- copyability_score: `21.970000`
- deployability_score: `20`
- multi_market_structure_score: `7.330000`
- pnl_curve_stability_score: `18.500000`
- risk_penalty_adjustment: `0`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
