# reakt2026

## 账户身份（优先人工核对）
- 展示名称: `reakt2026`
- 账户地址: `0xccf128f31a3af399c40dd9854c83b60101dd25a0`
- 平台昵称: `Velvety-Lion`
- 平台名称: `reakt2026`
- 本地名称: `account_30`

## 1. 执行结论
校准后决策分 41.22（锚点口径），结论：只适合筛着跟。主要板块暴露：sports。优势：可利用事件覆盖广、不可复制快交易比例较低。风险点：互斥型并存腿风险较高、存在同 condition 双边买入。硬黑名单主题（禁止跟）：spread、pacers、heat、cavaliers、suns。软黑名单主题（谨慎跟）：wildcats。白名单主题（优先筛选）：nebraska、cornhuskers、flyers、bruins、bears。风险门槛已触发，宽跟模式自动关闭。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `41.220000`
- raw_score: `18.420000`
- anchored_score: `41.220000`
- delta_vs_anchor_60: `-18.780000`
- delta_vs_anchor_raw: `-28.890000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 1231 笔交易，覆盖 30 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=flat, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： sports.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 可执行白名单主题：nebraska, cornhuskers, flyers, bruins, bears, auburn.

## 5. 跟单风险
- 存在明显互斥市场并发多腿行为。
- 加权多子市场风险偏高。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 全周期收益并非明显上行，持续优势可信度下降。
- 硬黑名单主题（应避免）：spread, pacers, heat, cavaliers, suns, blazers.
- 软黑名单主题（需更严格触发）：wildcats.

## 6. 板块与关键词过滤
### 所属板块
- sports

### 白名单关键词
- nebraska
- cornhuskers
- flyers
- bruins
- bears
- auburn
- islanders
- seattle
- senators
- sharks
- golden
- tulsa

### 硬黑名单关键词
- spread
- pacers
- heat
- cavaliers
- suns
- blazers
- trail
- bulls
- magic
- pistons
- raptors
- thunder

### 软黑名单关键词
- wildcats

## 7. 账户概览
- analysis_window: `2026-03-11 23:47:11 UTC -> 2026-04-10 03:33:11 UTC`
- trade_rows_used: `1231`
- total_buy_usdc: `382573.105110`
- total_sell_usdc: `0`
- traded_markets_count_api: `1972`
- position_value_api: `66994.565100`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `20.06%`
- dual_side_buy_usdc_ratio_1h: `14.72%`
- token_fast_20m_buy_usdc_ratio: `0.00%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `n/a`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `61.30%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `55.86%`
- deployable_event_equivalent: `90.000000`
- deployable_event_density: `3.086743`
- active_trading_days: `30.000000`
- trade_count: `1231.000000`
- avg_trades_per_active_day: `41.033333`

## 9. 收益曲线评估
- all_time_shape: `走平`
- all_time_score: `1`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `3.970000`
- deployability_score: `20`
- multi_market_structure_score: `1.610000`
- pnl_curve_stability_score: `0.830000`
- risk_penalty_adjustment: `-8.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
- 未匹配到可用 SELL 库存，持仓时长指标不可用
