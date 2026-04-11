# Sorrowful-Semester

## 账户身份（优先人工核对）
- 展示名称: `Sorrowful-Semester`
- 账户地址: `0x16bd7cc71f6da1e77d1d8255677abc75b9bae288`
- 平台昵称: `Sorrowful-Semester`
- 平台名称: `ddalkkak`
- 本地名称: `account_45`

## 1. 执行结论
校准后决策分 58.89（锚点口径），结论：只适合筛着跟。主要板块暴露：geopolitics、sports、us_politics。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：递进型并存梯度风险偏高、存在同 condition 双边买入。硬黑名单主题（禁止跟）：april、win、iran、march、ceasefire。软黑名单主题（谨慎跟）：vance、republican、duke、blue。白名单主题（优先筛选）：israel、kentucky、santa、broncos、wildcats。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `58.890000`
- raw_score: `45.610000`
- anchored_score: `58.890000`
- delta_vs_anchor_60: `-1.110000`
- delta_vs_anchor_raw: `-1.700000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 1529 笔交易，覆盖 19 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： geopolitics, sports, us_politics.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 可执行白名单主题：israel, kentucky, santa, broncos, wildcats, clara.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 递进型并发梯度比例偏高，结构管理负担较重。
- 硬黑名单主题（应避免）：april, win, iran, march, ceasefire, presidential.
- 软黑名单主题（需更严格触发）：vance, republican, duke, blue.

## 6. 板块与关键词过滤
### 所属板块
- geopolitics
- sports
- us_politics

### 白名单关键词
- israel
- kentucky
- santa
- broncos
- wildcats
- clara
- launch
- lebanon
- ground
- offensive
- major
- flyers

### 硬黑名单关键词
- april
- win
- iran
- march
- ceasefire
- presidential
- nomination
- netanyahu
- out
- democratic
- ocasio-cortez
- alexandria

### 软黑名单关键词
- vance
- republican
- duke
- blue

## 7. 账户概览
- analysis_window: `2026-03-12 21:49:25 UTC -> 2026-04-10 16:05:47 UTC`
- trade_rows_used: `1529`
- total_buy_usdc: `123794.158680`
- total_sell_usdc: `21998.063008`
- traded_markets_count_api: `488`
- position_value_api: `74936.182400`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `34.60%`
- dual_side_buy_usdc_ratio_1h: `5.76%`
- token_fast_20m_buy_usdc_ratio: `0.92%`
- noncopyable_token_fast_buy_ratio: `0.18%`
- noncopyable_token_fast_sell_ratio: `0.88%`
- noncopyable_token_fast_token_ratio: `2.35%`
- event_rebalance_20m_event_ratio: `1.85%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `84.35%`
- weighted_multi_market_risk_ratio: `10.07%`
- deployable_event_equivalent: `40.500000`
- deployable_event_density: `1.408139`
- active_trading_days: `19.000000`
- trade_count: `1529.000000`
- avg_trades_per_active_day: `80.473684`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `15.120000`
- deployability_score: `20`
- multi_market_structure_score: `6.500000`
- pnl_curve_stability_score: `9.990000`
- risk_penalty_adjustment: `-6.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
