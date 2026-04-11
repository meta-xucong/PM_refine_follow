# Wide-Prospect

## 账户身份（优先人工核对）
- 展示名称: `Wide-Prospect`
- 账户地址: `0xcbb5623096b78505a26524e642c5c9066e585ed9`
- 平台昵称: `Wide-Prospect`
- 平台名称: `Nicksypoo`
- 本地名称: `account_5`

## 1. 执行结论
校准后决策分 39.47（锚点口径），结论：不值得跟。主要板块暴露：sports。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：互斥型并存腿风险较高。硬黑名单主题（禁止跟）：winner、game、duty、call、gaming。软黑名单主题（谨慎跟）：nba、win、spurs、finals、san。白名单主题（优先筛选）：bo3、group、team、bo5、league。风险门槛已触发，宽跟模式自动关闭。重风险门槛已触发，低分情形会被强制判定为不值得跟。收益曲线标签：长期与近期均偏弱。不建议作为主跟单源，仅可少量人工挑选。

## 2. 决策快照
- decision: `不值得跟`
- final_score（决策分）: `39.470000`
- raw_score: `15.730000`
- anchored_score: `39.470000`
- delta_vs_anchor_60: `-20.530000`
- delta_vs_anchor_raw: `-31.580000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 235 笔交易，覆盖 30 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=down, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： sports.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 可执行白名单主题：bo3, group, team, bo5, league, stage.

## 5. 跟单风险
- 存在明显互斥市场并发多腿行为。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 已触发重风险门槛，差质标的会被自动归为不值得跟。
- 全周期收益并非明显上行，持续优势可信度下降。
- 硬黑名单主题（应避免）：winner, game, duty, call, gaming, lol.
- 软黑名单主题（需更严格触发）：nba, win, spurs, finals, san, antonio.

## 6. 板块与关键词过滤
### 所属板块
- sports

### 白名单关键词
- bo3
- group
- team
- bo5
- league
- stage
- esports
- season
- regular
- valorant
- vcl
- counter-strike

### 硬黑名单关键词
- winner
- game
- duty
- call
- gaming
- lol
- masters
- emea
- falcons
- giantx
- playoffs
- riyadh

### 软黑名单关键词
- nba
- win
- spurs
- finals
- san
- antonio
- suns
- make
- phoenix
- cloud
- dawning
- candidates

## 7. 账户概览
- analysis_window: `2026-03-12 03:11:55 UTC -> 2026-04-10 12:23:23 UTC`
- trade_rows_used: `235`
- total_buy_usdc: `96787.201531`
- total_sell_usdc: `31324.545927`
- traded_markets_count_api: `995`
- position_value_api: `21395.676500`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `1.92%`
- dual_side_buy_usdc_ratio_1h: `0.40%`
- token_fast_20m_buy_usdc_ratio: `1.21%`
- noncopyable_token_fast_buy_ratio: `0.13%`
- noncopyable_token_fast_sell_ratio: `0.33%`
- noncopyable_token_fast_token_ratio: `0.70%`
- event_rebalance_20m_event_ratio: `0.86%`
- exclusive_concurrent_leg_ratio: `69.05%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `12.33%`
- deployable_event_equivalent: `104.000000`
- deployable_event_density: `3.539466`
- active_trading_days: `30.000000`
- trade_count: `235.000000`
- avg_trades_per_active_day: `7.833333`

## 9. 收益曲线评估
- all_time_shape: `下行`
- all_time_score: `-10`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `12.060000`
- deployability_score: `20`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `-8.330000`
- risk_penalty_adjustment: `-8.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
- 触发重风险门槛，不值得跟的判定阈值被收紧
- 重风险门槛叠加低分，判定为不值得跟
