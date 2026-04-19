# Untrue-Vegetation

## 账户身份（优先人工核对）
- 展示名称: `Untrue-Vegetation`
- 账户地址: `0xd2678dc3b152a54900f28b0e849afe2049df9dc6`
- 平台昵称: `Untrue-Vegetation`
- 平台名称: `xfile`
- 本地名称: `account_3`

## 1. 执行结论
校准后决策分 61.82（锚点口径），结论：只适合筛着跟。主要板块暴露：sports、geopolitics。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：存在同 condition 双边买入。硬黑名单主题（禁止跟）：win、arsenal、united、bayern、nchen。白名单主题（优先筛选）：rockets、hawks、lakers、saint-germain、paris。风险门槛已触发，宽跟模式自动关闭。收益曲线标签：长期/中期/短期均偏强。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `61.820000`
- raw_score: `86.120000`
- anchored_score: `61.820000`
- delta_vs_anchor_60: `1.820000`
- delta_vs_anchor_raw: `2.800000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 1673 笔交易，覆盖 22 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=smooth_up, 7d=smooth_up.
- 主要板块主题： sports, geopolitics.

## 4. 跟单优势
- 不可复制 token 快交易（BUY）比例较低。
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 近 30 天收益曲线表现仍偏正向。
- 可执行白名单主题：rockets, hawks, lakers, saint-germain, paris, leipzig.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 硬黑名单主题（应避免）：win, arsenal, united, bayern, nchen, newcastle.

## 6. 板块与关键词过滤
### 所属板块
- sports
- geopolitics

### 白名单关键词
- rockets
- hawks
- lakers
- saint-germain
- paris
- leipzig
- brentford
- acf
- fiorentina
- jackets
- blue
- panthers

### 硬黑名单关键词
- win
- arsenal
- united
- bayern
- nchen
- newcastle
- pelicans
- clippers
- manchester
- olympique
- heat
- city

### 软黑名单关键词
- (none)

## 7. 账户概览
- analysis_window: `2026-03-12 17:21:19 UTC -> 2026-04-11 15:40:47 UTC`
- trade_rows_used: `1673`
- total_buy_usdc: `343601.417406`
- total_sell_usdc: `154045.323609`
- traded_markets_count_api: `1332`
- position_value_api: `1351.876700`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `49.36%`
- dual_side_buy_usdc_ratio_1h: `12.98%`
- token_fast_20m_buy_usdc_ratio: `0.60%`
- noncopyable_token_fast_buy_ratio: `0.01%`
- noncopyable_token_fast_sell_ratio: `0.03%`
- noncopyable_token_fast_token_ratio: `1.18%`
- event_rebalance_20m_event_ratio: `1.59%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `0.00%`
- weighted_multi_market_risk_ratio: `0.19%`
- deployable_event_equivalent: `42.500000`
- deployable_event_density: `1.419971`
- active_trading_days: `22.000000`
- trade_count: `1673.000000`
- avg_trades_per_active_day: `76.045455`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `平滑上行`
- d30_score: `6`
- d7_shape: `平滑上行`
- d7_score: `2`
- pnl_tag: `长期/中期/短期均偏强`

## 10. 评分拆解
- copyability_score: `23.120000`
- deployability_score: `20`
- multi_market_structure_score: `20`
- pnl_curve_stability_score: `28`
- risk_penalty_adjustment: `-5.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
