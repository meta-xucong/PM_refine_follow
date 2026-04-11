# Germany-007

## 账户身份（优先人工核对）
- 展示名称: `Germany-007`
- 账户地址: `0x6cff25615924313a189d3bcd5ca99db452cdc3da`
- 平台昵称: `Colossal-Latency`
- 平台名称: `Germany-007`
- 本地名称: `account_24`

## 1. 执行结论
校准后决策分 67.72（锚点口径），结论：只适合筛着跟。主要板块暴露：sports、crypto、geopolitics。优势：可利用事件覆盖广、加权多子市场风险较低。风险点：递进型并存梯度风险偏高、存在不可复制的 token 快交易暴露、存在同 condition 双边买入。硬黑名单主题（禁止跟）：win、bucks、candidates、fide、sindarov。软黑名单主题（谨慎跟）：end、draw、galatasaray、liverpool、am-11。白名单主题（优先筛选）：tico、atl、madrid、club、pm-5。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `67.720000`
- raw_score: `59.180000`
- anchored_score: `67.720000`
- delta_vs_anchor_60: `7.720000`
- delta_vs_anchor_raw: `11.870000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 5379 笔交易，覆盖 20 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： sports, crypto, geopolitics.

## 4. 跟单优势
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 可执行白名单主题：tico, atl, madrid, club, pm-5, pm-6.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 不可复制的 token 快交易（BUY）比例偏高，收益更依赖执行优势。
- 硬黑名单主题（应避免）：win, bucks, candidates, fide, sindarov, javokhir.
- 软黑名单主题（需更严格触发）：end, draw, galatasaray, liverpool, am-11, pm-12.

## 6. 板块与关键词过滤
### 所属板块
- sports
- crypto
- geopolitics

### 白名单关键词
- tico
- atl
- madrid
- club
- pm-5
- pm-6
- ethereum
- pm-4
- pm-2
- xrp
- solana
- pm-1

### 硬黑名单关键词
- win
- bucks
- candidates
- fide
- sindarov
- javokhir
- tournament
- hawks
- march
- pacers
- down
- raptors

### 软黑名单关键词
- end
- draw
- galatasaray
- liverpool
- am-11
- pm-12
- am-8
- most
- bundesliga

## 7. 账户概览
- analysis_window: `2026-03-11 19:28:53 UTC -> 2026-04-09 20:12:41 UTC`
- trade_rows_used: `5379`
- total_buy_usdc: `54208.072414`
- total_sell_usdc: `41373.472870`
- traded_markets_count_api: `4174`
- position_value_api: `2245.171500`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `30.20%`
- dual_side_buy_usdc_ratio_1h: `19.58%`
- token_fast_20m_buy_usdc_ratio: `41.45%`
- noncopyable_token_fast_buy_ratio: `28.55%`
- noncopyable_token_fast_sell_ratio: `44.64%`
- noncopyable_token_fast_token_ratio: `14.23%`
- event_rebalance_20m_event_ratio: `1.22%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `32.75%`
- weighted_multi_market_risk_ratio: `3.60%`
- deployable_event_equivalent: `336.500000`
- deployable_event_density: `11.591291`
- active_trading_days: `20.000000`
- trade_count: `5379.000000`
- avg_trades_per_active_day: `268.950000`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `14.550000`
- deployability_score: `20`
- multi_market_structure_score: `14.640000`
- pnl_curve_stability_score: `9.990000`
- risk_penalty_adjustment: `0`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
