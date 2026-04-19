# Musty-Instructor

## 账户身份（优先人工核对）
- 展示名称: `Musty-Instructor`
- 账户地址: `0xeafc14c8639ef6fbf882b74c3e6de2fe72d10d5c`
- 平台昵称: `Musty-Instructor`
- 平台名称: `quvbmnv`
- 本地名称: `account_10`

## 1. 执行结论
校准后决策分 61.67（锚点口径），结论：只适合筛着跟。主要板块暴露：geopolitics、us_politics、macro。优势：可利用事件覆盖广、加权多子市场风险较低。风险点：存在不可复制的 token 快交易暴露。硬黑名单主题（禁止跟）：iran、march、april、ceasefire、trump。软黑名单主题（谨慎跟）：countries、israel、strike、yemen、action。白名单主题（优先筛选）：hormuz、through、commercial、escorts、ship。收益曲线标签：长期/中期/短期均偏强。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `61.670000`
- raw_score: `85.890000`
- anchored_score: `61.670000`
- delta_vs_anchor_60: `1.670000`
- delta_vs_anchor_raw: `2.570000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 515 笔交易，覆盖 29 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=smooth_up, 7d=smooth_up.
- 主要板块主题： geopolitics, us_politics, macro.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 近 30 天收益曲线表现仍偏正向。
- 可执行白名单主题：hormuz, through, commercial, escorts, ship, ends.

## 5. 跟单风险
- 不可复制的 token 快交易（BUY）比例偏高，收益更依赖执行优势。
- 硬黑名单主题（应避免）：iran, march, april, ceasefire, trump, forces.
- 软黑名单主题（需更严格触发）：countries, israel, strike, yemen, action, jinping.

## 6. 板块与关键词过滤
### 所属板块
- geopolitics
- us_politics
- macro

### 白名单关键词
- hormuz
- through
- commercial
- escorts
- ship
- ends
- conflict
- country
- another
- may
- obtains
- uranium

### 硬黑名单关键词
- iran
- march
- april
- ceasefire
- trump
- forces
- enter
- visit
- china
- meeting
- week
- say

### 软黑名单关键词
- countries
- israel
- strike
- yemen
- action
- jinping

## 7. 账户概览
- analysis_window: `2026-03-12 16:14:27 UTC -> 2026-04-11 12:44:45 UTC`
- trade_rows_used: `515`
- total_buy_usdc: `22777.652069`
- total_sell_usdc: `27928.501351`
- traded_markets_count_api: `859`
- position_value_api: `0.000000`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `0.77%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `89.66%`
- noncopyable_token_fast_buy_ratio: `28.87%`
- noncopyable_token_fast_sell_ratio: `37.40%`
- noncopyable_token_fast_token_ratio: `39.51%`
- event_rebalance_20m_event_ratio: `23.40%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `17.87%`
- weighted_multi_market_risk_ratio: `8.27%`
- deployable_event_equivalent: `23.500000`
- deployable_event_density: `0.787154`
- active_trading_days: `29.000000`
- trade_count: `515.000000`
- avg_trades_per_active_day: `17.758621`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `平滑上行`
- d30_score: `6`
- d7_shape: `平滑上行`
- d7_score: `2`
- pnl_tag: `长期/中期/短期均偏强`

## 10. 评分拆解
- copyability_score: `22.670000`
- deployability_score: `20`
- multi_market_structure_score: `15.220000`
- pnl_curve_stability_score: `28`
- risk_penalty_adjustment: `0`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
