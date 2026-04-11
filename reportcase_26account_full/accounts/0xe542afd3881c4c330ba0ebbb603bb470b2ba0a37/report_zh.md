# leegunner

## 账户身份（优先人工核对）
- 展示名称: `leegunner`
- 账户地址: `0xe542afd3881c4c330ba0ebbb603bb470b2ba0a37`
- 平台昵称: `Lonely-Bog`
- 平台名称: `leegunner`
- 本地名称: `account_8`

## 1. 执行结论
校准后决策分 39.64（锚点口径），结论：不值得跟。主要板块暴露：sports、us_politics、geopolitics。优势：可利用事件覆盖广、加权多子市场风险较低。风险点：互斥型并存腿风险较高、递进型并存梯度风险偏高、存在不可复制的 token 快交易暴露。硬黑名单主题（禁止跟）：win、league、nba、cup、world。软黑名单主题（谨慎跟）：nfl、championship、kansas、chiefs、madrid。白名单主题（优先筛选）：barcelona、vandewinkel、colsanitas、bouzkova、marie。风险门槛已触发，宽跟模式自动关闭。收益曲线标签：长期与近期均偏弱。不建议作为主跟单源，仅可少量人工挑选。

## 2. 决策快照
- decision: `不值得跟`
- final_score（决策分）: `39.640000`
- raw_score: `15.990000`
- anchored_score: `39.640000`
- delta_vs_anchor_60: `-20.360000`
- delta_vs_anchor_raw: `-31.320000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 22151 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： sports, us_politics, geopolitics.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 可执行白名单主题：barcelona, vandewinkel, colsanitas, bouzkova, marie, copa.

## 5. 跟单风险
- 不可复制的 token 快交易（BUY）比例偏高，收益更依赖执行优势。
- 存在明显互斥市场并发多腿行为。
- 递进型并发梯度比例偏高，结构管理负担较重。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 硬黑名单主题（应避免）：win, league, nba, cup, world, finals.
- 软黑名单主题（需更严格触发）：nfl, championship, kansas, chiefs, madrid, real.

## 6. 板块与关键词过滤
### 所属板块
- sports
- us_politics
- geopolitics

### 白名单关键词
- barcelona
- vandewinkel
- colsanitas
- bouzkova
- marie
- copa
- hanne
- rybakina
- elena
- bahrain
- lakers
- ufc

### 硬黑名单关键词
- win
- league
- nba
- cup
- world
- finals
- top
- champions
- magic
- orlando
- chelsea
- fifa

### 软黑名单关键词
- nfl
- championship
- kansas
- chiefs
- madrid
- real
- manchester
- player
- singles
- final
- french
- japan

## 7. 账户概览
- analysis_window: `2026-03-11 18:44:05 UTC -> 2026-04-10 18:26:17 UTC`
- trade_rows_used: `22151`
- total_buy_usdc: `266478.891238`
- total_sell_usdc: `263625.779700`
- traded_markets_count_api: `5011`
- position_value_api: `111557.571200`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `8.60%`
- dual_side_buy_usdc_ratio_1h: `4.03%`
- token_fast_20m_buy_usdc_ratio: `30.16%`
- noncopyable_token_fast_buy_ratio: `21.17%`
- noncopyable_token_fast_sell_ratio: `24.95%`
- noncopyable_token_fast_token_ratio: `10.56%`
- event_rebalance_20m_event_ratio: `16.50%`
- exclusive_concurrent_leg_ratio: `56.52%`
- nested_concurrent_leg_ratio: `86.32%`
- weighted_multi_market_risk_ratio: `12.71%`
- deployable_event_equivalent: `119.000000`
- deployable_event_density: `3.968302`
- active_trading_days: `31.000000`
- trade_count: `22151.000000`
- avg_trades_per_active_day: `714.548387`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `0`
- deployability_score: `20`
- multi_market_structure_score: `0`
- pnl_curve_stability_score: `9.990000`
- risk_penalty_adjustment: `-14.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
