# Rare-Growth

## 账户身份（优先人工核对）
- 展示名称: `Rare-Growth`
- 账户地址: `0x0f9bf99cb7f86d70704edab6c7a234bc09bf7829`
- 平台昵称: `Rare-Growth`
- 平台名称: `linghujunlan`
- 本地名称: `account_2`

## 1. 执行结论
校准后决策分 27.73（锚点口径），结论：不值得跟。主要板块暴露：geopolitics、sports。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：互斥型并存腿风险较高。硬黑名单主题（禁止跟）：lol、esports、bo5、stand、first。软黑名单主题（谨慎跟）：win、nba、shai、mvp、gilgeous-alexander。白名单主题（优先筛选）：invade、china、taiwan、end、lyon。风险门槛已触发，宽跟模式自动关闭。重风险门槛已触发，低分情形会被强制判定为不值得跟。收益曲线标签：长期与近期均偏弱。不建议作为主跟单源，仅可少量人工挑选。

## 2. 决策快照
- decision: `不值得跟`
- final_score（决策分）: `27.730000`
- raw_score: `33.680000`
- anchored_score: `27.730000`
- delta_vs_anchor_60: `-32.270000`
- delta_vs_anchor_raw: `-49.640000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 166 笔交易，覆盖 17 个活跃交易日（分析窗口内）。
- 低频封顶已生效，封顶分数为 64, ，表明可跟单容量受限。
- 收益曲线形态： 全周期=volatile_up, 30d=volatile_up, 7d=flat.
- 主要板块主题： geopolitics, sports.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可执行白名单主题：invade, china, taiwan, end, lyon.

## 5. 跟单风险
- 存在明显互斥市场并发多腿行为。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 已触发重风险门槛，差质标的会被自动归为不值得跟。
- 交易频次/可利用度约束限制了实盘跟单容量。
- 硬黑名单主题（应避免）：lol, esports, bo5, stand, first, bnk.
- 软黑名单主题（需更严格触发）：win, nba, shai, mvp, gilgeous-alexander.

## 6. 板块与关键词过滤
### 所属板块
- geopolitics
- sports

### 白名单关键词
- invade
- china
- taiwan
- end
- lyon

### 硬黑名单关键词
- lol
- esports
- bo5
- stand
- first
- bnk
- fearx
- group
- bilibili
- game
- gaming
- winner

### 软黑名单关键词
- win
- nba
- shai
- mvp
- gilgeous-alexander

## 7. 账户概览
- analysis_window: `2026-03-13 06:49:37 UTC -> 2026-04-09 04:02:07 UTC`
- trade_rows_used: `166`
- total_buy_usdc: `38847.159899`
- total_sell_usdc: `18910.264120`
- traded_markets_count_api: `281`
- position_value_api: `52766.236400`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `14.91%`
- dual_side_buy_usdc_ratio_1h: `0.79%`
- token_fast_20m_buy_usdc_ratio: `0.75%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `0.00%`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `7.14%`
- exclusive_concurrent_leg_ratio: `76.64%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `11.04%`
- deployable_event_equivalent: `9.500000`
- deployable_event_density: `0.353374`
- active_trading_days: `17.000000`
- trade_count: `166.000000`
- avg_trades_per_active_day: `9.764706`

## 9. 收益曲线评估
- all_time_shape: `高波动上行`
- all_time_score: `6`
- d30_shape: `高波动上行`
- d30_score: `2`
- d7_shape: `走平`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `6.880000`
- deployability_score: `20`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `14.800000`
- risk_penalty_adjustment: `-8.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `64`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
- 触发重风险门槛，不值得跟的判定阈值被收紧
- 重风险门槛叠加低分，判定为不值得跟
- 校准分低于 32，触发不值得跟底线
