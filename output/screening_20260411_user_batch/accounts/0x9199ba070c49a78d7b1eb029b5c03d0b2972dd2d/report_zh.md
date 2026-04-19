# Ready-Judge

## 账户身份（优先人工核对）
- 展示名称: `Ready-Judge`
- 账户地址: `0x9199ba070c49a78d7b1eb029b5c03d0b2972dd2d`
- 平台昵称: `Ready-Judge`
- 平台名称: `0x9199Ba070C49A78d7b1EB029B5c03`
- 本地名称: `account_1`

## 1. 执行结论
校准后决策分 42.24（锚点口径），结论：只适合筛着跟。主要板块暴露：entertainment。优势：加权多子市场风险较低、不可复制快交易比例较低。风险点：存在同 condition 双边买入。硬黑名单主题（禁止跟）：office、box、weekend、opening、less。软黑名单主题（谨慎跟）：hoppers。白名单主题（优先筛选）：tuscany、mario、movie、super、galaxy。收益曲线标签：长期/中期/短期均偏强。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `42.240000`
- raw_score: `56`
- anchored_score: `42.240000`
- delta_vs_anchor_60: `-17.760000`
- delta_vs_anchor_raw: `-27.320000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 452 笔交易，覆盖 23 个活跃交易日（分析窗口内）。
- 低频封顶已生效，封顶分数为 56, ，表明可跟单容量受限。
- 收益曲线形态： 全周期=volatile_up, 30d=volatile_up, 7d=smooth_up.
- 主要板块主题： entertainment.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可执行白名单主题：tuscany, mario, movie, super, galaxy.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 交易频次/可利用度约束限制了实盘跟单容量。
- 硬黑名单主题（应避免）：office, box, weekend, opening, less, between.
- 软黑名单主题（需更严格触发）：hoppers.

## 6. 板块与关键词过滤
### 所属板块
- entertainment

### 白名单关键词
- tuscany
- mario
- movie
- super
- galaxy

### 硬黑名单关键词
- office
- box
- weekend
- opening
- less
- between
- you
- they
- kill
- project
- hail
- mary

### 软黑名单关键词
- hoppers

## 7. 账户概览
- analysis_window: `2026-03-12 20:36:47 UTC -> 2026-04-11 12:44:19 UTC`
- trade_rows_used: `452`
- total_buy_usdc: `38119.847324`
- total_sell_usdc: `18526.888896`
- traded_markets_count_api: `576`
- position_value_api: `875.187600`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `38.66%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `0.00%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `0.00%`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `23.08%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `14.26%`
- deployable_event_equivalent: `4.500000`
- deployable_event_density: `0.151659`
- active_trading_days: `23.000000`
- trade_count: `452.000000`
- avg_trades_per_active_day: `19.652174`

## 9. 收益曲线评估
- all_time_shape: `高波动上行`
- all_time_score: `6`
- d30_shape: `高波动上行`
- d30_score: `2`
- d7_shape: `平滑上行`
- d7_score: `2`
- pnl_tag: `长期/中期/短期均偏强`

## 10. 评分拆解
- copyability_score: `23.720000`
- deployability_score: `14.490000`
- multi_market_structure_score: `20`
- pnl_curve_stability_score: `18.500000`
- risk_penalty_adjustment: `0`
- concentration_penalty: `0.000000`
- low_frequency_cap: `56`

## 11. 数据质量与假设
- (none)
