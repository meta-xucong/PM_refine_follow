# Bleak-Full

## 账户身份（优先人工核对）
- 展示名称: `Bleak-Full`
- 账户地址: `0x6d9fc316c3b8377060a44b852ba664adbfd59790`
- 平台昵称: `Bleak-Full`
- 平台名称: `MEPP`
- 本地名称: `account_25`

## 1. 执行结论
校准后决策分 24.56（锚点口径），结论：不值得跟。主要板块暴露：geopolitics、us_politics、macro。优势：可利用事件覆盖广、不可复制快交易比例较低。风险点：递进型并存梯度风险偏高、存在同 condition 双边买入。硬黑名单主题（禁止跟）：iran、march、ceasefire、may、military。白名单主题（优先筛选）：iranian、regime、fall、june、invade。收益曲线标签：长期强但近期转弱。不建议作为主跟单源，仅可少量人工挑选。

## 2. 决策快照
- decision: `不值得跟`
- final_score（决策分）: `24.560000`
- raw_score: `28.790000`
- anchored_score: `24.560000`
- delta_vs_anchor_60: `-35.440000`
- delta_vs_anchor_raw: `-54.530000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 2982 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=volatile_up, 30d=down, 7d=down.
- 主要板块主题： geopolitics, us_politics, macro.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 可执行白名单主题：iranian, regime, fall, june, invade, strike.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 递进型并发梯度比例偏高，结构管理负担较重。
- 近 30 天收益下行，削弱短期跟单信心。
- 近 7 天收益动量为负，需要更严格入场过滤。
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
- china
- clash
- defense
- secretary
- pete

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
- traded_markets_count_api: `794`
- position_value_api: `565769.194500`

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
- d30_shape: `下行`
- d30_score: `-6`
- d7_shape: `下行`
- d7_score: `-2`
- pnl_tag: `长期强但近期转弱`

## 10. 评分拆解
- copyability_score: `12.200000`
- deployability_score: `20`
- multi_market_structure_score: `6.290000`
- pnl_curve_stability_score: `-3.700000`
- risk_penalty_adjustment: `-6.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 校准分低于 32，触发不值得跟底线
