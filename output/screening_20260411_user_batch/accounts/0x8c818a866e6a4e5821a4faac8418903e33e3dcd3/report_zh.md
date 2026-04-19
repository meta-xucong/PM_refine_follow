# Mysterious-Guard

## 账户身份（优先人工核对）
- 展示名称: `Mysterious-Guard`
- 账户地址: `0x8c818a866e6a4e5821a4faac8418903e33e3dcd3`
- 平台昵称: `Mysterious-Guard`
- 平台名称: `Sharkbets.pro`
- 本地名称: `account_8`

## 1. 执行结论
校准后决策分 70.84（锚点口径），结论：只适合筛着跟。主要板块暴露：sports。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。硬黑名单主题（禁止跟）：win、real、balompi、betis、manchester。白名单主题（优先筛选）：win、saint-germain、paris、barcelona、osasuna。收益曲线标签：长期/中期/短期均偏强。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `70.840000`
- raw_score: `100`
- anchored_score: `70.840000`
- delta_vs_anchor_60: `10.840000`
- delta_vs_anchor_raw: `16.680000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 554 笔交易，覆盖 21 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=smooth_up, 7d=smooth_up.
- 主要板块主题： sports.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 近 30 天收益曲线表现仍偏正向。
- 可执行白名单主题：win, saint-germain, paris, barcelona, osasuna, arsenal.

## 5. 跟单风险
- 硬黑名单主题（应避免）：win, real, balompi, betis, manchester.

## 6. 板块与关键词过滤
### 所属板块
- sports

### 白名单关键词
- win
- saint-germain
- paris
- barcelona
- osasuna
- arsenal
- glimt
- bod
- freiburg
- olympique
- lyonnais
- blazers

### 硬黑名单关键词
- win
- real
- balompi
- betis
- manchester

### 软黑名单关键词
- (none)

## 7. 账户概览
- analysis_window: `2026-03-12 17:26:57 UTC -> 2026-04-11 13:57:59 UTC`
- trade_rows_used: `554`
- total_buy_usdc: `213597.783677`
- total_sell_usdc: `11446.002082`
- traded_markets_count_api: `1887`
- position_value_api: `21704.703700`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `0.14%`
- dual_side_buy_usdc_ratio_1h: `0.14%`
- token_fast_20m_buy_usdc_ratio: `4.28%`
- noncopyable_token_fast_buy_ratio: `2.11%`
- noncopyable_token_fast_sell_ratio: `36.97%`
- noncopyable_token_fast_token_ratio: `4.84%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `0.01%`
- deployable_event_equivalent: `55.500000`
- deployable_event_density: `1.858992`
- active_trading_days: `21.000000`
- trade_count: `554.000000`
- avg_trades_per_active_day: `26.380952`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `平滑上行`
- d30_score: `6`
- d7_shape: `平滑上行`
- d7_score: `2`
- pnl_tag: `长期/中期/短期均偏强`

## 10. 评分拆解
- copyability_score: `34.220000`
- deployability_score: `20`
- multi_market_structure_score: `20`
- pnl_curve_stability_score: `28`
- risk_penalty_adjustment: `0`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
