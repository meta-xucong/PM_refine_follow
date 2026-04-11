# High-Alarm

## 账户身份（优先人工核对）
- 展示名称: `High-Alarm`
- 账户地址: `0x9238743eeba8bbfe9e85ac7ba2e1e3d77877b73e`
- 平台昵称: `High-Alarm`
- 平台名称: `leCommissaire`
- 本地名称: `account_12`

## 1. 执行结论
校准后决策分 50.36（锚点口径），结论：只适合筛着跟。主要板块暴露：geopolitics、sports、us_politics。优势：可利用事件覆盖广、加权多子市场风险较低。风险点：递进型并存梯度风险偏高、存在同 condition 双边买入。硬黑名单主题（禁止跟）：russia、march、capture、april、iran。软黑名单主题（谨慎跟）：win、military、united、manchester、barcelona。白名单主题（优先筛选）：ceasefire、madrid、real、nchen、bayern。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `50.360000`
- raw_score: `32.480000`
- anchored_score: `50.360000`
- delta_vs_anchor_60: `-9.640000`
- delta_vs_anchor_raw: `-14.830000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 2920 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=down, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： geopolitics, sports, us_politics.

## 4. 跟单优势
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 可执行白名单主题：ceasefire, madrid, real, nchen, bayern, sloviansk.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 全周期收益并非明显上行，持续优势可信度下降。
- 硬黑名单主题（应避免）：russia, march, capture, april, iran, enter.
- 软黑名单主题（需更严格触发）：win, military, united, manchester, barcelona, league.

## 6. 板块与关键词过滤
### 所属板块
- geopolitics
- sports
- us_politics

### 白名单关键词
- ceasefire
- madrid
- real
- nchen
- bayern
- sloviansk
- bilytske
- lyman
- deal
- nuclear
- us-iran
- serhiivka

### 硬黑名单关键词
- russia
- march
- capture
- april
- iran
- enter
- all
- hryshyne
- israel
- may
- ends
- conflict

### 软黑名单关键词
- win
- military
- united
- manchester
- barcelona
- league
- champions
- arsenal
- uefa
- reach
- sporting

## 7. 账户概览
- analysis_window: `2026-03-11 18:36:45 UTC -> 2026-04-10 15:23:19 UTC`
- trade_rows_used: `2920`
- total_buy_usdc: `55127.251532`
- total_sell_usdc: `40840.492389`
- traded_markets_count_api: `1461`
- position_value_api: `16542.633700`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `31.17%`
- dual_side_buy_usdc_ratio_1h: `2.46%`
- token_fast_20m_buy_usdc_ratio: `17.61%`
- noncopyable_token_fast_buy_ratio: `13.69%`
- noncopyable_token_fast_sell_ratio: `24.52%`
- noncopyable_token_fast_token_ratio: `8.26%`
- event_rebalance_20m_event_ratio: `5.37%`
- exclusive_concurrent_leg_ratio: `13.91%`
- nested_concurrent_leg_ratio: `44.03%`
- weighted_multi_market_risk_ratio: `14.04%`
- deployable_event_equivalent: `98.000000`
- deployable_event_density: `3.281359`
- active_trading_days: `31.000000`
- trade_count: `2920.000000`
- avg_trades_per_active_day: `94.193548`

## 9. 收益曲线评估
- all_time_shape: `下行`
- all_time_score: `-10`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `12.260000`
- deployability_score: `20`
- multi_market_structure_score: `8.540000`
- pnl_curve_stability_score: `-8.330000`
- risk_penalty_adjustment: `0`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
