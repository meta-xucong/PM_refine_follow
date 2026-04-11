# Sentimental-Wash

## 账户身份（优先人工核对）
- 展示名称: `Sentimental-Wash`
- 账户地址: `0x2d40ca3ab44c1cf56677c85919a815bbf59cec52`
- 平台昵称: `Sentimental-Wash`
- 平台名称: `kingsirpredictionconnoisseur`
- 本地名称: `account_36`

## 1. 执行结论
校准后决策分 67.32（锚点口径），结论：只适合筛着跟。主要板块暴露：sports、us_politics、macro。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：互斥型并存腿风险较高。硬黑名单主题（禁止跟）：playoffs、counter-strike、bo5、vincere、natus。软黑名单主题（谨慎跟）：next、hungary、orb、prime、viktor。白名单主题（优先筛选）：bo3、group、fall、regime、iranian。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `67.320000`
- raw_score: `58.570000`
- anchored_score: `67.320000`
- delta_vs_anchor_60: `7.320000`
- delta_vs_anchor_raw: `11.260000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 443 笔交易，覆盖 24 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=volatile_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： sports, us_politics, macro.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 可执行白名单主题：bo3, group, fall, regime, iranian, parivision.

## 5. 跟单风险
- 存在明显互斥市场并发多腿行为。
- 硬黑名单主题（应避免）：playoffs, counter-strike, bo5, vincere, natus, vitality.
- 软黑名单主题（需更严格触发）：next, hungary, orb, prime, viktor, minister.

## 6. 板块与关键词过滤
### 所属板块
- sports
- us_politics
- macro

### 白名单关键词
- bo3
- group
- fall
- regime
- iranian
- parivision
- win
- march
- april
- seats
- parliamentary
- election

### 硬黑名单关键词
- playoffs
- counter-strike
- bo5
- vincere
- natus
- vitality
- rotterdam
- open
- blast
- esports
- fut
- pgl

### 软黑名单关键词
- next
- hungary
- orb
- prime
- viktor
- minister
- gaming
- aurora
- themongolz
- bo3
- astralis
- mibr

## 7. 账户概览
- analysis_window: `2026-03-13 01:54:29 UTC -> 2026-04-11 14:42:55 UTC`
- trade_rows_used: `443`
- total_buy_usdc: `78772.677214`
- total_sell_usdc: `2805.636177`
- traded_markets_count_api: `413`
- position_value_api: `29237.655300`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `0.00%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `0.00%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `0.00%`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `33.84%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `8.05%`
- deployable_event_equivalent: `55.500000`
- deployable_event_density: `1.879213`
- active_trading_days: `24.000000`
- trade_count: `443.000000`
- avg_trades_per_active_day: `18.458333`

## 9. 收益曲线评估
- all_time_shape: `高波动上行`
- all_time_score: `6`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `23.720000`
- deployability_score: `20`
- multi_market_structure_score: `9.850000`
- pnl_curve_stability_score: `5.000000`
- risk_penalty_adjustment: `0`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
