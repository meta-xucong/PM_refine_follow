# Unhealthy-Bog

## 账户身份（优先人工核对）
- 展示名称: `Unhealthy-Bog`
- 账户地址: `0xcbbc5e035504421b084ad9248b660f6e9618b5d0`
- 平台昵称: `Unhealthy-Bog`
- 平台名称: `VibeTrader`
- 本地名称: `account_1`

## 1. 执行结论
校准后决策分 50.32（锚点口径），结论：只适合筛着跟。优势：可利用事件覆盖广、不可复制快交易比例较低。风险点：递进型并存梯度风险偏高。硬黑名单主题（禁止跟）：highest、temperature、march、april、between。软黑名单主题（谨慎跟）：ankara、aviv、tel、chengdu。白名单主题（优先筛选）：paris。收益曲线标签：长期/中期/短期均偏强。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `50.320000`
- raw_score: `68.430000`
- anchored_score: `50.320000`
- delta_vs_anchor_60: `-9.680000`
- delta_vs_anchor_raw: `-14.890000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 29654 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=smooth_up, 7d=smooth_up.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 近 30 天收益曲线表现仍偏正向。
- 可执行白名单主题：paris.

## 5. 跟单风险
- 递进型并发梯度比例偏高，结构管理负担较重。
- 加权多子市场风险偏高。
- 硬黑名单主题（应避免）：highest, temperature, march, april, between, higher.
- 软黑名单主题（需更严格触发）：ankara, aviv, tel, chengdu.

## 6. 板块与关键词过滤
### 所属板块
- (none)

### 白名单关键词
- paris

### 硬黑名单关键词
- highest
- temperature
- march
- april
- between
- higher
- seoul
- shanghai
- city
- new
- york
- toronto

### 软黑名单关键词
- ankara
- aviv
- tel
- chengdu

## 7. 账户概览
- analysis_window: `2026-03-12 15:12:33 UTC -> 2026-04-11 03:02:55 UTC`
- trade_rows_used: `29654`
- total_buy_usdc: `85843.756908`
- total_sell_usdc: `64658.149171`
- traded_markets_count_api: `5077`
- position_value_api: `1217.743700`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `4.35%`
- dual_side_buy_usdc_ratio_1h: `1.36%`
- token_fast_20m_buy_usdc_ratio: `1.42%`
- noncopyable_token_fast_buy_ratio: `0.21%`
- noncopyable_token_fast_sell_ratio: `0.21%`
- noncopyable_token_fast_token_ratio: `0.74%`
- event_rebalance_20m_event_ratio: `8.76%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `77.97%`
- weighted_multi_market_risk_ratio: `40.26%`
- deployable_event_equivalent: `89.000000`
- deployable_event_density: `3.017633`
- active_trading_days: `31.000000`
- trade_count: `29654.000000`
- avg_trades_per_active_day: `956.580645`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `平滑上行`
- d30_score: `6`
- d7_shape: `平滑上行`
- d7_score: `2`
- pnl_tag: `长期/中期/短期均偏强`

## 10. 评分拆解
- copyability_score: `18.900000`
- deployability_score: `20`
- multi_market_structure_score: `7.520000`
- pnl_curve_stability_score: `28`
- risk_penalty_adjustment: `-6.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
