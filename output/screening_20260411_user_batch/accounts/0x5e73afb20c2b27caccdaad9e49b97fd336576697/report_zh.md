# Mundane-Hood

## 账户身份（优先人工核对）
- 展示名称: `Mundane-Hood`
- 账户地址: `0x5e73afb20c2b27caccdaad9e49b97fd336576697`
- 平台昵称: `Mundane-Hood`
- 平台名称: `Newshound`
- 本地名称: `account_13`

## 1. 执行结论
校准后决策分 56.28（锚点口径），结论：只适合筛着跟。主要板块暴露：geopolitics、us_politics、macro。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：递进型并存梯度风险偏高、存在同 condition 双边买入。硬黑名单主题（禁止跟）：iran、end、hit、oil、high。软黑名单主题（谨慎跟）：israel、deal、new、nato。白名单主题（优先筛选）：vance、meeting、diplomatic、spx、down。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `56.280000`
- raw_score: `77.600000`
- anchored_score: `56.280000`
- delta_vs_anchor_60: `-3.720000`
- delta_vs_anchor_raw: `-5.720000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 930 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=volatile_up, 7d=down.
- 主要板块主题： geopolitics, us_politics, macro.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 可执行白名单主题：vance, meeting, diplomatic, spx, down, opens.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 近 7 天收益动量为负，需要更严格入场过滤。
- 硬黑名单主题（应避免）：iran, end, hit, oil, high, crude.
- 软黑名单主题（需更严格触发）：israel, deal, new, nato.

## 6. 板块与关键词过滤
### 所属板块
- geopolitics
- us_politics
- macro

### 白名单关键词
- vance
- meeting
- diplomatic
- spx
- down
- opens
- june
- iranian
- tariffs
- refund
- court
- force

### 硬黑名单关键词
- iran
- end
- hit
- oil
- high
- crude
- march
- december
- april
- ceasefire
- trump
- forces

### 软黑名单关键词
- israel
- deal
- new
- nato

## 7. 账户概览
- analysis_window: `2026-03-12 15:20:03 UTC -> 2026-04-11 15:37:15 UTC`
- trade_rows_used: `930`
- total_buy_usdc: `91700.419198`
- total_sell_usdc: `76112.622542`
- traded_markets_count_api: `1398`
- position_value_api: `27095.856500`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `41.14%`
- dual_side_buy_usdc_ratio_1h: `8.82%`
- token_fast_20m_buy_usdc_ratio: `5.41%`
- noncopyable_token_fast_buy_ratio: `0.60%`
- noncopyable_token_fast_sell_ratio: `1.50%`
- noncopyable_token_fast_token_ratio: `1.69%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `26.96%`
- weighted_multi_market_risk_ratio: `13.49%`
- deployable_event_equivalent: `61.000000`
- deployable_event_density: `2.032524`
- active_trading_days: `31.000000`
- trade_count: `930.000000`
- avg_trades_per_active_day: `30.000000`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `高波动上行`
- d30_score: `2`
- d7_shape: `下行`
- d7_score: `-2`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `19.830000`
- deployability_score: `20`
- multi_market_structure_score: `15.570000`
- pnl_curve_stability_score: `22.200000`
- risk_penalty_adjustment: `0`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
