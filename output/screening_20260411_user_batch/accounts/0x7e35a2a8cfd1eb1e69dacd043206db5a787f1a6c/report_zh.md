# Unfit-Hardboard

## 账户身份（优先人工核对）
- 展示名称: `Unfit-Hardboard`
- 账户地址: `0x7e35a2a8cfd1eb1e69dacd043206db5a787f1a6c`
- 平台昵称: `Unfit-Hardboard`
- 平台名称: `buoys`
- 本地名称: `account_18`

## 1. 执行结论
校准后决策分 54.59（锚点口径），结论：只适合筛着跟。主要板块暴露：us_politics、geopolitics、sports。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：递进型并存梯度风险偏高。硬黑名单主题（禁止跟）：april、iran、trump、march、military。软黑名单主题（谨慎跟）：top、presidential、mario、galaxy、super。白名单主题（优先筛选）：june、primary、canada、out、governor。收益曲线标签：长期/中期/短期均偏强。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `54.590000`
- raw_score: `75.000000`
- anchored_score: `54.590000`
- delta_vs_anchor_60: `-5.410000`
- delta_vs_anchor_raw: `-8.320000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 1977 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=smooth_up, 7d=smooth_up.
- 主要板块主题： us_politics, geopolitics, sports.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 近 30 天收益曲线表现仍偏正向。
- 可执行白名单主题：june, primary, canada, out, governor, republican.

## 5. 跟单风险
- 递进型并发梯度比例偏高，结构管理负担较重。
- 硬黑名单主题（应避免）：april, iran, trump, march, military, against.
- 软黑名单主题（需更严格触发）：top, presidential, mario, galaxy, super, movie.

## 6. 板块与关键词过滤
### 所属板块
- us_politics
- geopolitics
- sports

### 白名单关键词
- june
- primary
- canada
- out
- governor
- republican
- minister
- province
- leave
- schedule
- seats
- most

### 硬黑名单关键词
- april
- iran
- trump
- march
- military
- against
- leadership
- change
- talk
- end
- corina
- machado

### 软黑名单关键词
- top
- presidential
- mario
- galaxy
- super
- movie
- grossing
- philippe
- french
- douard
- apple
- app

## 7. 账户概览
- analysis_window: `2026-03-12 15:34:13 UTC -> 2026-04-11 13:50:45 UTC`
- trade_rows_used: `1977`
- total_buy_usdc: `39635.096468`
- total_sell_usdc: `30112.339496`
- traded_markets_count_api: `1404`
- position_value_api: `55955.836700`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `11.48%`
- dual_side_buy_usdc_ratio_1h: `1.02%`
- token_fast_20m_buy_usdc_ratio: `1.35%`
- noncopyable_token_fast_buy_ratio: `0.49%`
- noncopyable_token_fast_sell_ratio: `1.60%`
- noncopyable_token_fast_token_ratio: `0.59%`
- event_rebalance_20m_event_ratio: `1.46%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `71.78%`
- weighted_multi_market_risk_ratio: `13.50%`
- deployable_event_equivalent: `165.000000`
- deployable_event_density: `5.513204`
- active_trading_days: `31.000000`
- trade_count: `1977.000000`
- avg_trades_per_active_day: `63.774194`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `平滑上行`
- d30_score: `6`
- d7_shape: `平滑上行`
- d7_score: `2`
- pnl_tag: `长期/中期/短期均偏强`

## 10. 评分拆解
- copyability_score: `21.600000`
- deployability_score: `20`
- multi_market_structure_score: `8.400000`
- pnl_curve_stability_score: `28`
- risk_penalty_adjustment: `-3.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
