# Mammoth-Tape

## 账户身份（优先人工核对）
- 展示名称: `Mammoth-Tape`
- 账户地址: `0x92d0cb81e6c891b835c8e0272e8c323095bd269e`
- 平台昵称: `Mammoth-Tape`
- 平台名称: `Analista.`
- 本地名称: `account_33`

## 1. 执行结论
校准后决策分 52.38（锚点口径），结论：只适合筛着跟。主要板块暴露：geopolitics、us_politics。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：递进型并存梯度风险偏高。硬黑名单主题（禁止跟）：april、iran、ceasefire、march、military。软黑名单主题（谨慎跟）：lebanon。白名单主题（优先筛选）：enter、trump、visit、vance、through。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `52.380000`
- raw_score: `71.590000`
- anchored_score: `52.380000`
- delta_vs_anchor_60: `-7.620000`
- delta_vs_anchor_raw: `-11.730000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 326 笔交易，覆盖 30 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=volatile_up, 7d=flat.
- 主要板块主题： geopolitics, us_politics.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 可执行白名单主题：enter, trump, visit, vance, through, ship.

## 5. 跟单风险
- 递进型并发梯度比例偏高，结构管理负担较重。
- 硬黑名单主题（应避免）：april, iran, ceasefire, march, military, announces.
- 软黑名单主题（需更严格触发）：lebanon.

## 6. 板块与关键词过滤
### 所属板块
- geopolitics
- us_politics

### 白名单关键词
- enter
- trump
- visit
- vance
- through
- ship
- commercial
- escorts
- change
- leadership
- may
- against

### 硬黑名单关键词
- april
- iran
- ceasefire
- march
- military
- announces
- support
- israel
- opposition
- meeting
- hormuz
- strait

### 软黑名单关键词
- lebanon

## 7. 账户概览
- analysis_window: `2026-03-12 18:59:33 UTC -> 2026-04-11 14:25:51 UTC`
- trade_rows_used: `326`
- total_buy_usdc: `30813.617514`
- total_sell_usdc: `31602.713562`
- traded_markets_count_api: `942`
- position_value_api: `3806.363300`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `14.85%`
- dual_side_buy_usdc_ratio_1h: `1.88%`
- token_fast_20m_buy_usdc_ratio: `9.16%`
- noncopyable_token_fast_buy_ratio: `8.74%`
- noncopyable_token_fast_sell_ratio: `8.60%`
- noncopyable_token_fast_token_ratio: `12.00%`
- event_rebalance_20m_event_ratio: `5.56%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `62.16%`
- weighted_multi_market_risk_ratio: `18.97%`
- deployable_event_equivalent: `25.000000`
- deployable_event_density: `0.838647`
- active_trading_days: `30.000000`
- trade_count: `326.000000`
- avg_trades_per_active_day: `10.866667`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `高波动上行`
- d30_score: `2`
- d7_shape: `走平`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `18.870000`
- deployability_score: `20`
- multi_market_structure_score: `9.810000`
- pnl_curve_stability_score: `25.900000`
- risk_penalty_adjustment: `-3.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
