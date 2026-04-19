# Smart-Strip

## 账户身份（优先人工核对）
- 展示名称: `Smart-Strip`
- 账户地址: `0xff165cf8eb75ee77933a7544d7cd600ccb2c7511`
- 平台昵称: `Smart-Strip`
- 平台名称: `solwizzo-onX`
- 本地名称: `account_11`

## 1. 执行结论
校准后决策分 45.08（锚点口径），结论：只适合筛着跟。主要板块暴露：sports、crypto、us_politics。优势：可利用事件覆盖广。风险点：递进型并存梯度风险偏高、存在不可复制的 token 快交易暴露、存在同 condition 双边买入。硬黑名单主题（禁止跟）：hit、high、crude、oil、april。软黑名单主题（谨慎跟）：world、championship、nfl、league、vikings。白名单主题（优先筛选）：tesla、dip、price、ufc、heavyweight。收益曲线标签：长期/中期/短期均偏强。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `45.080000`
- raw_score: `60.360000`
- anchored_score: `45.080000`
- delta_vs_anchor_60: `-14.920000`
- delta_vs_anchor_raw: `-22.960000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 4814 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=smooth_up, 7d=smooth_up.
- 主要板块主题： sports, crypto, us_politics.

## 4. 跟单优势
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 近 30 天收益曲线表现仍偏正向。
- 可执行白名单主题：tesla, dip, price, ufc, heavyweight, fun.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 不可复制的 token 快交易（BUY）比例偏高，收益更依赖执行优势。
- 递进型并发梯度比例偏高，结构管理负担较重。
- 硬黑名单主题（应避免）：hit, high, crude, oil, april, wti.
- 软黑名单主题（需更严格触发）：world, championship, nfl, league, vikings, minnesota.

## 6. 板块与关键词过滤
### 所属板块
- sports
- crypto
- us_politics

### 白名单关键词
- tesla
- dip
- price
- ufc
- heavyweight
- fun

### 硬黑名单关键词
- hit
- high
- crude
- oil
- april
- wti
- win
- raiders
- masters
- bryson
- tournament
- dechambeau

### 软黑名单关键词
- world
- championship
- nfl
- league
- vikings
- minnesota
- nba
- classic
- baseball
- series
- new

## 7. 账户概览
- analysis_window: `2026-03-12 15:24:05 UTC -> 2026-04-11 12:37:57 UTC`
- trade_rows_used: `4814`
- total_buy_usdc: `108415.545961`
- total_sell_usdc: `96211.920855`
- traded_markets_count_api: `651`
- position_value_api: `23826.871500`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `32.93%`
- dual_side_buy_usdc_ratio_1h: `0.94%`
- token_fast_20m_buy_usdc_ratio: `37.27%`
- noncopyable_token_fast_buy_ratio: `27.24%`
- noncopyable_token_fast_sell_ratio: `31.16%`
- noncopyable_token_fast_token_ratio: `10.22%`
- event_rebalance_20m_event_ratio: `12.07%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `73.56%`
- weighted_multi_market_risk_ratio: `23.39%`
- deployable_event_equivalent: `30.500000`
- deployable_event_density: `1.020592`
- active_trading_days: `31.000000`
- trade_count: `4814.000000`
- avg_trades_per_active_day: `155.290323`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `平滑上行`
- d30_score: `6`
- d7_shape: `平滑上行`
- d7_score: `2`
- pnl_tag: `长期/中期/短期均偏强`

## 10. 评分拆解
- copyability_score: `7.370000`
- deployability_score: `20`
- multi_market_structure_score: `7.990000`
- pnl_curve_stability_score: `28`
- risk_penalty_adjustment: `-3.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
