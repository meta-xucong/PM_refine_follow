# Unwitting-Prisoner

## 账户身份（优先人工核对）
- 展示名称: `Unwitting-Prisoner`
- 账户地址: `0xbb8e6477bcb4d0a79449507c607d36fd228fb243`
- 平台昵称: `Unwitting-Prisoner`
- 平台名称: `Generator`
- 本地名称: `account_43`

## 1. 执行结论
校准后决策分 62.48（锚点口径），结论：只适合筛着跟。主要板块暴露：geopolitics、us_politics、sports。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：递进型并存梯度风险偏高。硬黑名单主题（禁止跟）：iran、april、ceasefire、announces、trump。白名单主题（优先筛选）：march、out、netanyahu、forces、enter。收益曲线标签：长期/中期/短期均偏强。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `62.480000`
- raw_score: `87.140000`
- anchored_score: `62.480000`
- delta_vs_anchor_60: `2.480000`
- delta_vs_anchor_raw: `3.820000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 183 笔交易，覆盖 16 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=smooth_up, 7d=smooth_up.
- 主要板块主题： geopolitics, us_politics, sports.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 加权多子市场结构风险整体可控。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 近 30 天收益曲线表现仍偏正向。
- 可执行白名单主题：march, out, netanyahu, forces, enter, israel.

## 5. 跟单风险
- 递进型并发梯度比例偏高，结构管理负担较重。
- 硬黑名单主题（应避免）：iran, april, ceasefire, announces, trump, operations.

## 6. 板块与关键词过滤
### 所属板块
- geopolitics
- us_politics
- sports

### 白名单关键词
- march
- out
- netanyahu
- forces
- enter
- israel
- hezbollah

### 硬黑名单关键词
- iran
- april
- ceasefire
- announces
- trump
- operations
- military
- end
- against

### 软黑名单关键词
- (none)

## 7. 账户概览
- analysis_window: `2026-03-15 14:24:01 UTC -> 2026-04-09 21:11:35 UTC`
- trade_rows_used: `183`
- total_buy_usdc: `246613.901461`
- total_sell_usdc: `240387.405970`
- traded_markets_count_api: `311`
- position_value_api: `108775.433600`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `0.00%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `0.00%`
- noncopyable_token_fast_buy_ratio: `0.00%`
- noncopyable_token_fast_sell_ratio: `0.00%`
- noncopyable_token_fast_token_ratio: `0.00%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `47.87%`
- weighted_multi_market_risk_ratio: `17.57%`
- deployable_event_equivalent: `8.000000`
- deployable_event_density: `0.316418`
- active_trading_days: `16.000000`
- trade_count: `183.000000`
- avg_trades_per_active_day: `11.437500`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `平滑上行`
- d30_score: `6`
- d7_shape: `平滑上行`
- d7_score: `2`
- pnl_tag: `长期/中期/短期均偏强`

## 10. 评分拆解
- copyability_score: `26.800000`
- deployability_score: `20`
- multi_market_structure_score: `12.340000`
- pnl_curve_stability_score: `28`
- risk_penalty_adjustment: `0`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
