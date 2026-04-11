# Unaware-Pipe

## 账户身份（优先人工核对）
- 展示名称: `Unaware-Pipe`
- 账户地址: `0x31c518f864d1394361fec967b3daa9093a86ede4`
- 平台昵称: `Unaware-Pipe`
- 平台名称: `BTCGambler247`
- 本地名称: `account_9`

## 1. 执行结论
校准后决策分 55.54（锚点口径），结论：只适合筛着跟。主要板块暴露：geopolitics、sports、us_politics。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：递进型并存梯度风险偏高、存在同 condition 双边买入。硬黑名单主题（禁止跟）：march、iran、april、june、forces。软黑名单主题（谨慎跟）：win、election、kamala、harris、presidential。白名单主题（优先筛选）：fed、change、there、meeting、rates。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `55.540000`
- raw_score: `40.450000`
- anchored_score: `55.540000`
- delta_vs_anchor_60: `-4.460000`
- delta_vs_anchor_raw: `-6.860000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 4583 笔交易，覆盖 29 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=volatile_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： geopolitics, sports, us_politics.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 可执行白名单主题：fed, change, there, meeting, rates, interest.

## 5. 跟单风险
- 递进型并发梯度比例偏高，结构管理负担较重。
- 硬黑名单主题（应避免）：march, iran, april, june, forces, enter.
- 软黑名单主题（需更严格触发）：win, election, kamala, harris, presidential, elections.

## 6. 板块与关键词过滤
### 所属板块
- geopolitics
- sports
- us_politics

### 白名单关键词
- fed
- change
- there
- meeting
- rates
- interest
- spread
- blue
- russia
- president
- ukraine
- devils

### 硬黑名单关键词
- march
- iran
- april
- june
- forces
- enter
- iranian
- ceasefire
- regime
- fall
- out
- netanyahu

### 软黑名单关键词
- win
- election
- kamala
- harris
- presidential
- elections
- launch
- tournament
- between

## 7. 账户概览
- analysis_window: `2026-03-12 15:10:05 UTC -> 2026-04-11 14:32:25 UTC`
- trade_rows_used: `4583`
- total_buy_usdc: `874853.347162`
- total_sell_usdc: `165402.273766`
- traded_markets_count_api: `422`
- position_value_api: `223859.805500`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `29.37%`
- dual_side_buy_usdc_ratio_1h: `0.70%`
- token_fast_20m_buy_usdc_ratio: `0.08%`
- noncopyable_token_fast_buy_ratio: `0.07%`
- noncopyable_token_fast_sell_ratio: `0.43%`
- noncopyable_token_fast_token_ratio: `0.92%`
- event_rebalance_20m_event_ratio: `2.56%`
- exclusive_concurrent_leg_ratio: `12.30%`
- nested_concurrent_leg_ratio: `71.11%`
- weighted_multi_market_risk_ratio: `15.64%`
- deployable_event_equivalent: `129.500000`
- deployable_event_density: `4.320434`
- active_trading_days: `29.000000`
- trade_count: `4583.000000`
- avg_trades_per_active_day: `158.034483`

## 9. 收益曲线评估
- all_time_shape: `高波动上行`
- all_time_score: `6`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `13.520000`
- deployability_score: `20`
- multi_market_structure_score: `4.930000`
- pnl_curve_stability_score: `5.000000`
- risk_penalty_adjustment: `-3.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
