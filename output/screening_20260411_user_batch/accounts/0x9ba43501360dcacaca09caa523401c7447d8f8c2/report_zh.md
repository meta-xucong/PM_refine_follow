# Digital-Bill

## 账户身份（优先人工核对）
- 展示名称: `Digital-Bill`
- 账户地址: `0x9ba43501360dcacaca09caa523401c7447d8f8c2`
- 平台昵称: `Digital-Bill`
- 平台名称: `BipBop`
- 本地名称: `account_20`

## 1. 执行结论
校准后决策分 31.13（锚点口径），结论：不值得跟。主要板块暴露：us_politics、geopolitics。优势：加权多子市场风险较低。风险点：递进型并存梯度风险偏高、存在不可复制的 token 快交易暴露。硬黑名单主题（禁止跟）：say、trump、during、march、week。软黑名单主题（谨慎跟）：questions、reform、minister、starmer、prime。风险门槛已触发，宽跟模式自动关闭。重风险门槛已触发，低分情形会被强制判定为不值得跟。收益曲线标签：长期/中期/短期均偏强。不建议作为主跟单源，仅可少量人工挑选。

## 2. 决策快照
- decision: `不值得跟`
- final_score（决策分）: `31.130000`
- raw_score: `38.900000`
- anchored_score: `31.130000`
- delta_vs_anchor_60: `-28.870000`
- delta_vs_anchor_raw: `-44.420000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 339 笔交易，覆盖 18 个活跃交易日（分析窗口内）。
- 低频封顶已生效，封顶分数为 56, ，表明可跟单容量受限。
- 收益曲线形态： 全周期=smooth_up, 30d=smooth_up, 7d=smooth_up.
- 主要板块主题： us_politics, geopolitics.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 加权多子市场结构风险整体可控。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 近 30 天收益曲线表现仍偏正向。

## 5. 跟单风险
- 不可复制的 token 快交易（BUY）比例偏高，收益更依赖执行优势。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 已触发重风险门槛，差质标的会被自动归为不值得跟。
- 交易频次/可利用度约束限制了实盘跟单容量。
- 硬黑名单主题（应避免）：say, trump, during, march, week, epic.
- 软黑名单主题（需更严格触发）：questions, reform, minister, starmer, prime.

## 6. 板块与关键词过滤
### 所属板块
- us_politics
- geopolitics

### 白名单关键词
- (none)

### 硬黑名单关键词
- say
- trump
- during
- march
- week
- epic
- fury
- times
- press
- next
- white
- house

### 软黑名单关键词
- questions
- reform
- minister
- starmer
- prime

## 7. 账户概览
- analysis_window: `2026-03-12 20:37:57 UTC -> 2026-04-08 17:46:39 UTC`
- trade_rows_used: `339`
- total_buy_usdc: `36274.659083`
- total_sell_usdc: `44731.017876`
- traded_markets_count_api: `1181`
- position_value_api: `0.000000`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `0.00%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `92.58%`
- noncopyable_token_fast_buy_ratio: `86.48%`
- noncopyable_token_fast_sell_ratio: `86.69%`
- noncopyable_token_fast_token_ratio: `74.42%`
- event_rebalance_20m_event_ratio: `66.67%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `39.40%`
- weighted_multi_market_risk_ratio: `17.74%`
- deployable_event_equivalent: `4.000000`
- deployable_event_density: `0.148804`
- active_trading_days: `18.000000`
- trade_count: `339.000000`
- avg_trades_per_active_day: `18.833333`

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
- deployability_score: `13.620000`
- multi_market_structure_score: `9.280000`
- pnl_curve_stability_score: `28`
- risk_penalty_adjustment: `-12.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `56`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
- 触发重风险门槛，不值得跟的判定阈值被收紧
- 重风险门槛叠加低分，判定为不值得跟
- 校准分低于 32，触发不值得跟底线
