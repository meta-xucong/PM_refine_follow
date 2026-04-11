# False-Mall

## 账户身份（优先人工核对）
- 展示名称: `False-Mall`
- 账户地址: `0x712433f69c169ebaaa67ce13f3f66f54575e70c1`
- 平台昵称: `False-Mall`
- 平台名称: `S55`
- 本地名称: `account_29`

## 1. 执行结论
校准后决策分 78.75（锚点口径），结论：相对可跟。主要板块暴露：macro、geopolitics、us_politics。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。硬黑名单主题（禁止跟）：end、march、iran、oil、crude。白名单主题（优先筛选）：fed、meeting、there、rates、interest。收益曲线标签：长期与近期均偏弱。建议在账户级黑名单过滤下进行较高比例跟随。

## 2. 决策快照
- decision: `相对可跟`
- final_score（决策分）: `78.750000`
- raw_score: `76.160000`
- anchored_score: `78.750000`
- delta_vs_anchor_60: `18.750000`
- delta_vs_anchor_raw: `28.850000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 470 笔交易，覆盖 28 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： macro, geopolitics, us_politics.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 可执行白名单主题：fed, meeting, there, rates, interest, change.

## 5. 跟单风险
- 硬黑名单主题（应避免）：end, march, iran, oil, crude, hit.

## 6. 板块与关键词过滤
### 所属板块
- macro
- geopolitics
- us_politics

### 白名单关键词
- fed
- meeting
- there
- rates
- interest
- change
- april
- regime
- iranian
- fall
- forces
- enter

### 硬黑名单关键词
- end
- march
- iran
- oil
- crude
- hit
- high
- ceasefire
- april
- military
- trump
- operations

### 软黑名单关键词
- (none)

## 7. 账户概览
- analysis_window: `2026-03-12 16:03:09 UTC -> 2026-04-10 09:21:55 UTC`
- trade_rows_used: `470`
- total_buy_usdc: `73214.732206`
- total_sell_usdc: `26902.520293`
- traded_markets_count_api: `396`
- position_value_api: `46411.615200`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `3.81%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `1.02%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `0.00%`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `3.12%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `22.18%`
- weighted_multi_market_risk_ratio: `12.21%`
- deployable_event_equivalent: `24.500000`
- deployable_event_density: `0.853024`
- active_trading_days: `28.000000`
- trade_count: `470.000000`
- avg_trades_per_active_day: `16.785714`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `29.710000`
- deployability_score: `20`
- multi_market_structure_score: `16.450000`
- pnl_curve_stability_score: `9.990000`
- risk_penalty_adjustment: `0`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
