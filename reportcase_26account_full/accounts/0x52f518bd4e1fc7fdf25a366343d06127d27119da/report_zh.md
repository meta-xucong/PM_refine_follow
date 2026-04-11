# png1024

## 账户身份（优先人工核对）
- 展示名称: `png1024`
- 账户地址: `0x52f518bd4e1fc7fdf25a366343d06127d27119da`
- 平台昵称: `Unhealthy-Standing`
- 平台名称: `png1024`
- 本地名称: `account_16`

## 1. 执行结论
校准后决策分 60.88（锚点口径），结论：只适合筛着跟。主要板块暴露：geopolitics、sports、us_politics。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：递进型并存梯度风险偏高。硬黑名单主题（禁止跟）：israel、ends、may、conflict、iran。软黑名单主题（谨慎跟）：next、ter、hungary、minister、magyar。白名单主题（优先筛选）：invade、april、ceasefire、win、against。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `60.880000`
- raw_score: `48.660000`
- anchored_score: `60.880000`
- delta_vs_anchor_60: `0.880000`
- delta_vs_anchor_raw: `1.350000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 276 笔交易，覆盖 19 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： geopolitics, sports, us_politics.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 可执行白名单主题：invade, april, ceasefire, win, against, military.

## 5. 跟单风险
- 递进型并发梯度比例偏高，结构管理负担较重。
- 硬黑名单主题（应避免）：israel, ends, may, conflict, iran, israeli.
- 软黑名单主题（需更严格触发）：next, ter, hungary, minister, magyar, prime.

## 6. 板块与关键词过滤
### 所属板块
- geopolitics
- sports
- us_politics

### 白名单关键词
- invade
- april
- ceasefire
- win
- against
- military
- action
- election
- through
- continues
- parliamentary
- hungarian

### 硬黑名单关键词
- israel
- ends
- may
- conflict
- iran
- israeli
- march
- parliament
- dissolved

### 软黑名单关键词
- next
- ter
- hungary
- minister
- magyar
- prime
- tournament
- fabiano
- caruana
- fide
- candidates

## 7. 账户概览
- analysis_window: `2026-03-14 13:13:21 UTC -> 2026-04-10 17:17:59 UTC`
- trade_rows_used: `276`
- total_buy_usdc: `55408.059450`
- total_sell_usdc: `49174.061600`
- traded_markets_count_api: `294`
- position_value_api: `87219.402600`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `3.44%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `3.49%`
- noncopyable_token_fast_buy_ratio: `1.49%`
- noncopyable_token_fast_sell_ratio: `1.70%`
- noncopyable_token_fast_token_ratio: `3.70%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `96.29%`
- weighted_multi_market_risk_ratio: `15.17%`
- deployable_event_equivalent: `16.000000`
- deployable_event_density: `0.588887`
- active_trading_days: `19.000000`
- trade_count: `276.000000`
- avg_trades_per_active_day: `14.526316`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `20.080000`
- deployability_score: `20`
- multi_market_structure_score: `4.590000`
- pnl_curve_stability_score: `9.990000`
- risk_penalty_adjustment: `-6.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
