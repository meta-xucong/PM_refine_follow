# Superior-Olive

## 账户身份（优先人工核对）
- 展示名称: `Superior-Olive`
- 账户地址: `0x0f37cb80dee49d55b5f6d9e595d52591d6371410`
- 平台昵称: `Superior-Olive`
- 平台名称: `Hans323`
- 本地名称: `account_23`

## 1. 执行结论
校准后决策分 65.65（锚点口径），结论：只适合筛着跟。主要板块暴露：geopolitics、sports、us_politics。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。硬黑名单主题（禁止跟）：iran、forces、enter、april。白名单主题（优先筛选）：highest、temperature、below、denver、march。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `65.650000`
- raw_score: `56`
- anchored_score: `65.650000`
- delta_vs_anchor_60: `5.650000`
- delta_vs_anchor_raw: `8.690000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 64 笔交易，覆盖 10 个活跃交易日（分析窗口内）。
- 低频封顶已生效，封顶分数为 56, ，表明可跟单容量受限。
- 收益曲线形态： 全周期=volatile_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： geopolitics, sports, us_politics.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 可执行白名单主题：highest, temperature, below, denver, march, ceasefire.

## 5. 跟单风险
- 交易频次/可利用度约束限制了实盘跟单容量。
- 硬黑名单主题（应避免）：iran, forces, enter, april.

## 6. 板块与关键词过滤
### 所属板块
- geopolitics
- sports
- us_politics

### 白名单关键词
- highest
- temperature
- below
- denver
- march
- ceasefire
- london
- madrid

### 硬黑名单关键词
- iran
- forces
- enter
- april

### 软黑名单关键词
- (none)

## 7. 账户概览
- analysis_window: `2026-03-24 00:29:41 UTC -> 2026-04-09 09:46:15 UTC`
- trade_rows_used: `64`
- total_buy_usdc: `78202.195041`
- total_sell_usdc: `11625.011147`
- traded_markets_count_api: `2873`
- position_value_api: `15458.113000`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `0.13%`
- dual_side_buy_usdc_ratio_1h: `0.13%`
- token_fast_20m_buy_usdc_ratio: `19.04%`
- noncopyable_token_fast_buy_ratio: `9.52%`
- noncopyable_token_fast_sell_ratio: `64.19%`
- noncopyable_token_fast_token_ratio: `6.67%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `0.85%`
- deployable_event_equivalent: `10.000000`
- deployable_event_density: `0.610258`
- active_trading_days: `10.000000`
- trade_count: `64.000000`
- avg_trades_per_active_day: `6.400000`

## 9. 收益曲线评估
- all_time_shape: `高波动上行`
- all_time_score: `6`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `29.850000`
- deployability_score: `20`
- multi_market_structure_score: `20`
- pnl_curve_stability_score: `5.000000`
- risk_penalty_adjustment: `-9.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `56`

## 11. 数据质量与假设
- (none)
