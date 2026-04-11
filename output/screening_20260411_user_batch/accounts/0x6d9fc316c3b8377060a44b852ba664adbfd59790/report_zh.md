# Bleak-Full

## 账户身份（优先人工核对）
- 展示名称: `Bleak-Full`
- 账户地址: `0x6d9fc316c3b8377060a44b852ba664adbfd59790`
- 平台昵称: `Bleak-Full`
- 平台名称: `MEPP`
- 本地名称: `account_25`

## 1. 执行结论
校准后决策分 53.62（锚点口径），结论：只适合筛着跟。主要板块暴露：geopolitics、us_politics、macro。优势：可利用事件覆盖广、不可复制快交易比例较低。风险点：递进型并存梯度风险偏高、存在同 condition 双边买入。硬黑名单主题（禁止跟）：iran、march、ceasefire、may、military。白名单主题（优先筛选）：iranian、regime、fall、june、invade。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `53.620000`
- raw_score: `37.490000`
- anchored_score: `53.620000`
- delta_vs_anchor_60: `-6.380000`
- delta_vs_anchor_raw: `-9.820000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 2982 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=volatile_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： geopolitics, us_politics, macro.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 可执行白名单主题：iranian, regime, fall, june, invade, strike.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 递进型并发梯度比例偏高，结构管理负担较重。
- 硬黑名单主题（应避免）：iran, march, ceasefire, may, military, end.

## 6. 板块与关键词过滤
### 所属板块
- geopolitics
- us_politics
- macro

### 白名单关键词
- iranian
- regime
- fall
- june
- invade
- strike
- taiwan
- clash
- china
- hegseth
- pete
- defense

### 硬黑名单关键词
- iran
- march
- ceasefire
- may
- military
- end
- announces
- trump
- against
- operations
- forces
- enter

### 软黑名单关键词
- (none)

## 7. 账户概览
- analysis_window: `2026-03-12 17:23:31 UTC -> 2026-04-11 11:48:29 UTC`
- trade_rows_used: `2982`
- total_buy_usdc: `794765.998878`
- total_sell_usdc: `576061.871657`
- traded_markets_count_api: `768`
- position_value_api: `537973.793000`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `32.43%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `0.34%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `0.00%`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `1.64%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `84.20%`
- weighted_multi_market_risk_ratio: `35.07%`
- deployable_event_equivalent: `46.000000`
- deployable_event_density: `1.545318`
- active_trading_days: `31.000000`
- trade_count: `2982.000000`
- avg_trades_per_active_day: `96.193548`

## 9. 收益曲线评估
- all_time_shape: `高波动上行`
- all_time_score: `6`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `12.200000`
- deployability_score: `20`
- multi_market_structure_score: `6.290000`
- pnl_curve_stability_score: `5.000000`
- risk_penalty_adjustment: `-6.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
