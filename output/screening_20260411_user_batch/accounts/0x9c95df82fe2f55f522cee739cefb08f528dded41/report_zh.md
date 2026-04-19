# Miserable-Blizzard

## 账户身份（优先人工核对）
- 展示名称: `Miserable-Blizzard`
- 账户地址: `0x9c95df82fe2f55f522cee739cefb08f528dded41`
- 平台昵称: `Miserable-Blizzard`
- 平台名称: `ben1243`
- 本地名称: `account_4`

## 1. 执行结论
校准后决策分 31.84（锚点口径），结论：不值得跟。主要板块暴露：sports。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：互斥型并存腿风险较高、存在同 condition 双边买入。硬黑名单主题（禁止跟）：win、heavyweight、milan、prelims、madrid。软黑名单主题（谨慎跟）：bayern、nchen。白名单主题（优先筛选）：arsenal、flyers、blackhawks、barcelona、utah。风险门槛已触发，宽跟模式自动关闭。重风险门槛已触发，低分情形会被强制判定为不值得跟。收益曲线标签：长期/中期/短期均偏强。不建议作为主跟单源，仅可少量人工挑选。

## 2. 决策快照
- decision: `不值得跟`
- final_score（决策分）: `31.840000`
- raw_score: `40.000000`
- anchored_score: `31.840000`
- delta_vs_anchor_60: `-28.160000`
- delta_vs_anchor_raw: `-43.320000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 1188 笔交易，覆盖 26 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=smooth_up, 7d=smooth_up.
- 主要板块主题： sports.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 近 30 天收益曲线表现仍偏正向。
- 可执行白名单主题：arsenal, flyers, blackhawks, barcelona, utah, kings.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 存在明显互斥市场并发多腿行为。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 已触发重风险门槛，差质标的会被自动归为不值得跟。
- 硬黑名单主题（应避免）：win, heavyweight, milan, prelims, madrid, warriors.
- 软黑名单主题（需更严格触发）：bayern, nchen.

## 6. 板块与关键词过滤
### 所属板块
- sports

### 白名单关键词
- arsenal
- flyers
- blackhawks
- barcelona
- utah
- kings
- lakers
- rockets
- roma
- milano
- internazionale
- petrino

### 硬黑名单关键词
- win
- heavyweight
- milan
- prelims
- madrid
- warriors
- real
- timberwolves
- spurs
- nuggets
- pistons
- hawks

### 软黑名单关键词
- bayern
- nchen

## 7. 账户概览
- analysis_window: `2026-03-12 16:42:59 UTC -> 2026-04-11 10:52:23 UTC`
- trade_rows_used: `1188`
- total_buy_usdc: `237909.133938`
- total_sell_usdc: `142213.014615`
- traded_markets_count_api: `604`
- position_value_api: `959.822600`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `42.01%`
- dual_side_buy_usdc_ratio_1h: `9.18%`
- token_fast_20m_buy_usdc_ratio: `3.90%`
- noncopyable_token_fast_buy_ratio: `0.87%`
- noncopyable_token_fast_sell_ratio: `1.12%`
- noncopyable_token_fast_token_ratio: `3.95%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `96.66%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `2.43%`
- deployable_event_equivalent: `48.000000`
- deployable_event_density: `1.613091`
- active_trading_days: `26.000000`
- trade_count: `1188.000000`
- avg_trades_per_active_day: `45.692308`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `平滑上行`
- d30_score: `6`
- d7_shape: `平滑上行`
- d7_score: `2`
- pnl_tag: `长期/中期/短期均偏强`

## 10. 评分拆解
- copyability_score: `0`
- deployability_score: `20`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `28`
- risk_penalty_adjustment: `-8.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
- 触发重风险门槛，不值得跟的判定阈值被收紧
- 重风险门槛叠加低分，判定为不值得跟
- 校准分低于 32，触发不值得跟底线
