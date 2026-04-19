# Interesting-Stone

## 账户身份（优先人工核对）
- 展示名称: `Interesting-Stone`
- 账户地址: `0x7a2180022d383bd514276b7a2083a97e51e6ac9c`
- 平台昵称: `Interesting-Stone`
- 平台名称: `Wongwei`
- 本地名称: `account_38`

## 1. 执行结论
校准后决策分 37.04（锚点口径），结论：不值得跟。主要板块暴露：crypto。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：递进型并存梯度风险偏高。硬黑名单主题（禁止跟）：hit、oil、crude、high、april。白名单主题（优先筛选）：down、bitcoin、am-11、am-2、am-1。收益曲线标签：长期与近期均偏弱。不建议作为主跟单源，仅可少量人工挑选。

## 2. 决策快照
- decision: `不值得跟`
- final_score（决策分）: `37.040000`
- raw_score: `48`
- anchored_score: `37.040000`
- delta_vs_anchor_60: `-22.960000`
- delta_vs_anchor_raw: `-35.320000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 29 笔交易，覆盖 5 个活跃交易日（分析窗口内）。
- 低频封顶已生效，封顶分数为 48, ，表明可跟单容量受限。
- 收益曲线形态： 全周期=volatile_up, 30d=smooth_up, 7d=insufficient_data.
- 主要板块主题： crypto.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 近 30 天收益曲线表现仍偏正向。
- 可执行白名单主题：down, bitcoin, am-11, am-2, am-1, am-10.

## 5. 跟单风险
- 递进型并发梯度比例偏高，结构管理负担较重。
- 交易频次/可利用度约束限制了实盘跟单容量。
- 硬黑名单主题（应避免）：hit, oil, crude, high, april, wti.

## 6. 板块与关键词过滤
### 所属板块
- crypto

### 白名单关键词
- down
- bitcoin
- am-11
- am-2
- am-1
- am-10
- pm-11
- iranian
- regime
- fall
- am-12

### 硬黑名单关键词
- hit
- oil
- crude
- high
- april
- wti
- end
- march

### 软黑名单关键词
- (none)

## 7. 账户概览
- analysis_window: `2026-03-18 14:48:03 UTC -> 2026-04-06 10:20:51 UTC`
- trade_rows_used: `29`
- total_buy_usdc: `2770.526558`
- total_sell_usdc: `0`
- traded_markets_count_api: `132`
- position_value_api: `767.488000`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `0.00%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `0.00%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `n/a`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `74.71%`
- weighted_multi_market_risk_ratio: `14.50%`
- deployable_event_equivalent: `21.000000`
- deployable_event_density: `1.116164`
- active_trading_days: `5.000000`
- trade_count: `29.000000`
- avg_trades_per_active_day: `5.800000`

## 9. 收益曲线评估
- all_time_shape: `高波动上行`
- all_time_score: `6`
- d30_shape: `平滑上行`
- d30_score: `6`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `24.010000`
- deployability_score: `19.520000`
- multi_market_structure_score: `8.050000`
- pnl_curve_stability_score: `16.650000`
- risk_penalty_adjustment: `-16.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `48`

## 11. 数据质量与假设
- 未匹配到可用 SELL 库存，持仓时长指标不可用
