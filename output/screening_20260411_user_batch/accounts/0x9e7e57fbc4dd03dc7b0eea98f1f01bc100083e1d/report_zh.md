# Scarce-Nexus

## 账户身份（优先人工核对）
- 展示名称: `Scarce-Nexus`
- 账户地址: `0x9e7e57fbc4dd03dc7b0eea98f1f01bc100083e1d`
- 平台昵称: `Scarce-Nexus`
- 平台名称: `mcorleone`
- 本地名称: `account_46`

## 1. 执行结论
校准后决策分 47.37（锚点口径），结论：只适合筛着跟。主要板块暴露：macro、sports、us_politics。优势：不可复制快交易比例较低。风险点：递进型并存梯度风险偏高。硬黑名单主题（禁止跟）：fed、cuts、happen、rate、interest。白名单主题（优先筛选）：pause、three、mar、apr、jun。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `47.370000`
- raw_score: `63.890000`
- anchored_score: `47.370000`
- delta_vs_anchor_60: `-12.630000`
- delta_vs_anchor_raw: `-19.430000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 335 笔交易，覆盖 17 个活跃交易日（分析窗口内）。
- 低频封顶已生效，封顶分数为 64, ，表明可跟单容量受限。
- 收益曲线形态： 全周期=smooth_up, 30d=smooth_up, 7d=insufficient_data.
- 主要板块主题： macro, sports, us_politics.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 近 30 天收益曲线表现仍偏正向。
- 可执行白名单主题：pause, three, mar, apr, jun, decisions.

## 5. 跟单风险
- 递进型并发梯度比例偏高，结构管理负担较重。
- 交易频次/可利用度约束限制了实盘跟单容量。
- 硬黑名单主题（应避免）：fed, cuts, happen, rate, interest, change.

## 6. 板块与关键词过滤
### 所属板块
- macro
- sports
- us_politics

### 白名单关键词
- pause
- three
- mar
- apr
- jun
- decisions
- next

### 硬黑名单关键词
- fed
- cuts
- happen
- rate
- interest
- change
- meeting
- there
- rates
- june
- win
- mayoral

### 软黑名单关键词
- (none)

## 7. 账户概览
- analysis_window: `2026-03-12 15:14:53 UTC -> 2026-03-28 14:49:59 UTC`
- trade_rows_used: `335`
- total_buy_usdc: `19955.150085`
- total_sell_usdc: `15192.592579`
- traded_markets_count_api: `132`
- position_value_api: `17386.860100`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `0.00%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `0.00%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `0.00%`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `18.18%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `74.48%`
- weighted_multi_market_risk_ratio: `20.22%`
- deployable_event_equivalent: `6.000000`
- deployable_event_density: `0.375406`
- active_trading_days: `17.000000`
- trade_count: `335.000000`
- avg_trades_per_active_day: `19.705882`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `平滑上行`
- d30_score: `6`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `23.230000`
- deployability_score: `19.600000`
- multi_market_structure_score: `8.080000`
- pnl_curve_stability_score: `24.980000`
- risk_penalty_adjustment: `-3.000000`
- concentration_penalty: `9.000000`
- low_frequency_cap: `64`

## 11. 数据质量与假设
- (none)
