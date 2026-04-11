# Dead-Brook

## 账户身份（优先人工核对）
- 展示名称: `Dead-Brook`
- 账户地址: `0x6a8328b1ae11569f7b27600073558879885e4c59`
- 平台昵称: `Dead-Brook`
- 平台名称: `Pulser`
- 本地名称: `account_2`

## 1. 执行结论
校准后决策分 56.30（锚点口径），结论：只适合筛着跟。主要板块暴露：geopolitics。风险点：递进型并存梯度风险偏高、存在不可复制的 token 快交易暴露。硬黑名单主题（禁止跟）：iran、april、ceasefire、march、out。白名单主题（优先筛选）：nuke、strike、dimona、israel。风险门槛已触发，宽跟模式自动关闭。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `56.300000`
- raw_score: `41.610000`
- anchored_score: `56.300000`
- delta_vs_anchor_60: `-3.700000`
- delta_vs_anchor_raw: `-5.700000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 350 笔交易，覆盖 17 个活跃交易日（分析窗口内）。
- 低频封顶已生效，封顶分数为 64, ，表明可跟单容量受限。
- 收益曲线形态： 全周期=volatile_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： geopolitics.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 可执行白名单主题：nuke, strike, dimona, israel.

## 5. 跟单风险
- 不可复制的 token 快交易（BUY）比例偏高，收益更依赖执行优势。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 交易频次/可利用度约束限制了实盘跟单容量。
- 硬黑名单主题（应避免）：iran, april, ceasefire, march, out, netanyahu.

## 6. 板块与关键词过滤
### 所属板块
- geopolitics

### 白名单关键词
- nuke
- strike
- dimona
- israel

### 硬黑名单关键词
- iran
- april
- ceasefire
- march
- out
- netanyahu

### 软黑名单关键词
- (none)

## 7. 账户概览
- analysis_window: `2026-03-11 20:46:23 UTC -> 2026-04-08 16:14:13 UTC`
- trade_rows_used: `350`
- total_buy_usdc: `45627.803841`
- total_sell_usdc: `42344.170064`
- traded_markets_count_api: `1002`
- position_value_api: `7653.146200`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `0.00%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `41.93%`
- noncopyable_token_fast_buy_ratio: `31.35%`
- noncopyable_token_fast_sell_ratio: `38.25%`
- noncopyable_token_fast_token_ratio: `11.76%`
- event_rebalance_20m_event_ratio: `9.09%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `44.09%`
- weighted_multi_market_risk_ratio: `21.42%`
- deployable_event_equivalent: `7.000000`
- deployable_event_density: `0.251699`
- active_trading_days: `17.000000`
- trade_count: `350.000000`
- avg_trades_per_active_day: `20.588235`

## 9. 收益曲线评估
- all_time_shape: `高波动上行`
- all_time_score: `6`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `17.670000`
- deployability_score: `20`
- multi_market_structure_score: `12.940000`
- pnl_curve_stability_score: `5.000000`
- risk_penalty_adjustment: `-5.000000`
- concentration_penalty: `9.000000`
- low_frequency_cap: `64`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
