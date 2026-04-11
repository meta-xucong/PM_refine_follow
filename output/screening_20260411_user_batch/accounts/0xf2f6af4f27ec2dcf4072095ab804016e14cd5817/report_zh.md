# Stained-Cynic

## 账户身份（优先人工核对）
- 展示名称: `Stained-Cynic`
- 账户地址: `0xf2f6af4f27ec2dcf4072095ab804016e14cd5817`
- 平台昵称: `Stained-Cynic`
- 平台名称: `gopfan2`
- 本地名称: `account_5`

## 1. 执行结论
校准后决策分 49.01（锚点口径），结论：只适合筛着跟。主要板块暴露：sports、us_politics、crypto。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：互斥型并存腿风险较高、递进型并存梯度风险偏高。硬黑名单主题（禁止跟）：march、out、netanyahu、dip、bitcoin。软黑名单主题（谨慎跟）：candidates、tournament、giri、fide、anish。白名单主题（优先筛选）：iranian、fall、regime、june、spread。风险门槛已触发，宽跟模式自动关闭。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `49.010000`
- raw_score: `30.400000`
- anchored_score: `49.010000`
- delta_vs_anchor_60: `-10.990000`
- delta_vs_anchor_raw: `-16.910000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 8986 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： sports, us_politics, crypto.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 可执行白名单主题：iranian, fall, regime, june, spread, real.

## 5. 跟单风险
- 存在明显互斥市场并发多腿行为。
- 递进型并发梯度比例偏高，结构管理负担较重。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 硬黑名单主题（应避免）：march, out, netanyahu, dip, bitcoin, seats.
- 软黑名单主题（需更严格触发）：candidates, tournament, giri, fide, anish, second.

## 6. 板块与关键词过滤
### 所属板块
- sports
- us_politics
- crypto

### 白名单关键词
- iranian
- fall
- regime
- june
- spread
- real
- arsenal
- ufc
- prelims
- night
- fight
- texas

### 硬黑名单关键词
- march
- out
- netanyahu
- dip
- bitcoin
- seats
- parliamentary
- election
- most
- win
- april
- slovenian

### 软黑名单关键词
- candidates
- tournament
- giri
- fide
- anish
- second
- senate
- tisza
- least
- democratic
- presidential
- race

## 7. 账户概览
- analysis_window: `2026-03-12 15:22:31 UTC -> 2026-04-11 10:06:37 UTC`
- trade_rows_used: `8986`
- total_buy_usdc: `1419984.630382`
- total_sell_usdc: `527513.964841`
- traded_markets_count_api: `1940`
- position_value_api: `689121.699700`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `6.13%`
- dual_side_buy_usdc_ratio_1h: `1.64%`
- token_fast_20m_buy_usdc_ratio: `3.02%`
- noncopyable_token_fast_buy_ratio: `2.99%`
- noncopyable_token_fast_sell_ratio: `6.84%`
- noncopyable_token_fast_token_ratio: `1.05%`
- event_rebalance_20m_event_ratio: `5.31%`
- exclusive_concurrent_leg_ratio: `51.82%`
- nested_concurrent_leg_ratio: `54.68%`
- weighted_multi_market_risk_ratio: `15.55%`
- deployable_event_equivalent: `87.000000`
- deployable_event_density: `2.921362`
- active_trading_days: `31.000000`
- trade_count: `8986.000000`
- avg_trades_per_active_day: `289.870968`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `8.410000`
- deployability_score: `20`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `9.990000`
- risk_penalty_adjustment: `-8.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
