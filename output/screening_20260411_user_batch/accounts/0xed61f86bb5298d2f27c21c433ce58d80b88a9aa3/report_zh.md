# Burdensome-Piracy

## 账户身份（优先人工核对）
- 展示名称: `Burdensome-Piracy`
- 账户地址: `0xed61f86bb5298d2f27c21c433ce58d80b88a9aa3`
- 平台昵称: `Burdensome-Piracy`
- 平台名称: `ewww1`
- 本地名称: `account_27`

## 1. 执行结论
校准后决策分 33.12（锚点口径），结论：不值得跟。主要板块暴露：sports。优势：可利用事件覆盖广、加权多子市场风险较低。风险点：互斥型并存腿风险较高、存在不可复制的 token 快交易暴露。硬黑名单主题（禁止跟）：win、end、draw、real、madrid。软黑名单主题（谨慎跟）：wrexham。风险门槛已触发，宽跟模式自动关闭。重风险门槛已触发，低分情形会被强制判定为不值得跟。收益曲线标签：长期/中期/短期均偏强。不建议作为主跟单源，仅可少量人工挑选。

## 2. 决策快照
- decision: `不值得跟`
- final_score（决策分）: `33.120000`
- raw_score: `41.960000`
- anchored_score: `33.120000`
- delta_vs_anchor_60: `-26.880000`
- delta_vs_anchor_raw: `-41.360000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 1040 笔交易，覆盖 19 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=smooth_up, 7d=smooth_up.
- 主要板块主题： sports.

## 4. 跟单优势
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 近 30 天收益曲线表现仍偏正向。

## 5. 跟单风险
- 不可复制的 token 快交易（BUY）比例偏高，收益更依赖执行优势。
- 存在明显互斥市场并发多腿行为。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 已触发重风险门槛，差质标的会被自动归为不值得跟。
- 硬黑名单主题（应避免）：win, end, draw, real, madrid, paris.
- 软黑名单主题（需更严格触发）：wrexham.

## 6. 板块与关键词过滤
### 所属板块
- sports

### 白名单关键词
- (none)

### 硬黑名单关键词
- win
- end
- draw
- real
- madrid
- paris
- both
- teams
- score
- senators
- city
- united

### 软黑名单关键词
- wrexham

## 7. 账户概览
- analysis_window: `2026-03-15 15:10:19 UTC -> 2026-04-10 20:23:17 UTC`
- trade_rows_used: `1040`
- total_buy_usdc: `80242.928383`
- total_sell_usdc: `89524.866726`
- traded_markets_count_api: `3171`
- position_value_api: `15.000000`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `17.18%`
- dual_side_buy_usdc_ratio_1h: `16.50%`
- token_fast_20m_buy_usdc_ratio: `98.85%`
- noncopyable_token_fast_buy_ratio: `95.87%`
- noncopyable_token_fast_sell_ratio: `97.13%`
- noncopyable_token_fast_token_ratio: `72.85%`
- event_rebalance_20m_event_ratio: `25.53%`
- exclusive_concurrent_leg_ratio: `36.06%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `9.70%`
- deployable_event_equivalent: `21.000000`
- deployable_event_density: `0.800997`
- active_trading_days: `19.000000`
- trade_count: `1040.000000`
- avg_trades_per_active_day: `54.736842`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `平滑上行`
- d30_score: `6`
- d7_shape: `平滑上行`
- d7_score: `2`
- pnl_tag: `长期/中期/短期均偏强`

## 10. 评分拆解
- copyability_score: `0`
- deployability_score: `20`
- multi_market_structure_score: `5.960000`
- pnl_curve_stability_score: `28`
- risk_penalty_adjustment: `-12.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
- 触发重风险门槛，不值得跟的判定阈值被收紧
- 重风险门槛叠加低分，判定为不值得跟
