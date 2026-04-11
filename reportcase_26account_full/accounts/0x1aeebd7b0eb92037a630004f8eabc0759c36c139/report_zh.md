# KBO30

## 账户身份（优先人工核对）
- 展示名称: `KBO30`
- 账户地址: `0x1aeebd7b0eb92037a630004f8eabc0759c36c139`
- 平台昵称: `n/a`
- 平台名称: `KBO30`
- 本地名称: `account_19`

## 1. 执行结论
校准后决策分 56.34（锚点口径），结论：只适合筛着跟。主要板块暴露：sports、entertainment。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：存在同 condition 双边买入。硬黑名单主题（禁止跟）：win、league、arsenal、champions、cup。软黑名单主题（谨慎跟）：finland、televote、frankenstein。白名单主题（优先筛选）：best、academy、awards、actress、jessie。风险门槛已触发，宽跟模式自动关闭。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `56.340000`
- raw_score: `41.680000`
- anchored_score: `56.340000`
- delta_vs_anchor_60: `-3.660000`
- delta_vs_anchor_raw: `-5.630000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 3593 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=down, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： sports, entertainment.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 可执行白名单主题：best, academy, awards, actress, jessie, buckley.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 全周期收益并非明显上行，持续优势可信度下降。
- 硬黑名单主题（应避免）：win, league, arsenal, champions, cup, uefa.
- 软黑名单主题（需更严格触发）：finland, televote, frankenstein.

## 6. 板块与关键词过滤
### 所属板块
- sports
- entertainment

### 白名单关键词
- best
- academy
- awards
- actress
- jessie
- buckley

### 硬黑名单关键词
- win
- league
- arsenal
- champions
- cup
- uefa
- reach
- eurovision
- carabao
- madrid
- real
- scheffler

### 软黑名单关键词
- finland
- televote
- frankenstein

## 7. 账户概览
- analysis_window: `2026-03-11 18:58:03 UTC -> 2026-04-10 18:12:01 UTC`
- trade_rows_used: `3593`
- total_buy_usdc: `113651.409563`
- total_sell_usdc: `26684.370191`
- traded_markets_count_api: `534`
- position_value_api: `34936.183600`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `58.62%`
- dual_side_buy_usdc_ratio_1h: `36.87%`
- token_fast_20m_buy_usdc_ratio: `0.00%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `0.00%`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `8.11%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `13.79%`
- deployable_event_equivalent: `13.000000`
- deployable_event_density: `0.433796`
- active_trading_days: `31.000000`
- trade_count: `3593.000000`
- avg_trades_per_active_day: `115.903226`

## 9. 收益曲线评估
- all_time_shape: `下行`
- all_time_score: `-10`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `19.000000`
- deployability_score: `20`
- multi_market_structure_score: `20`
- pnl_curve_stability_score: `-8.330000`
- risk_penalty_adjustment: `-9.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
