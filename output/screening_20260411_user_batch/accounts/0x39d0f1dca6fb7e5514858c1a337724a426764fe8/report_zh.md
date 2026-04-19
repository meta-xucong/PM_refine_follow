# Both-Moustache

## 账户身份（优先人工核对）
- 展示名称: `Both-Moustache`
- 账户地址: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`
- 平台昵称: `Both-Moustache`
- 平台名称: `kekkone`
- 本地名称: `account_49`

## 1. 执行结论
校准后决策分 60.00（锚点口径），结论：只适合筛着跟。主要板块暴露：geopolitics、us_politics、sports。优势：可利用事件覆盖广、加权多子市场风险较低、不可复制快交易比例较低。风险点：递进型并存梯度风险偏高。硬黑名单主题（禁止跟）：iran、enter、forces、december、april。白名单主题（优先筛选）：out、netanyahu、invade、fall、regime。收益曲线标签：长期/中期/短期均偏强。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `60.000000`
- raw_score: `83.320000`
- anchored_score: `60.000000`
- delta_vs_anchor_60: `0.000000`
- delta_vs_anchor_raw: `0.000000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 2091 笔交易，覆盖 31 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=smooth_up, 30d=volatile_up, 7d=volatile_up.
- 主要板块主题： geopolitics, us_politics, sports.

## 4. 跟单优势
- 同 condition 双边暴露较低，方向表达更清晰。
- 不可复制 token 快交易（BUY）比例较低。
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 可执行白名单主题：out, netanyahu, invade, fall, regime, next.

## 5. 跟单风险
- 递进型并发梯度比例偏高，结构管理负担较重。
- 硬黑名单主题（应避免）：iran, enter, forces, december, april, israel.

## 6. 板块与关键词过滤
### 所属板块
- geopolitics
- us_politics
- sports

### 白名单关键词
- out
- netanyahu
- invade
- fall
- regime
- next
- hormuz
- strait
- traffic
- returns
- normal
- election

### 硬黑名单关键词
- iran
- enter
- forces
- december
- april
- israel
- march
- ends
- conflict
- ceasefire
- hezbollah
- against

### 软黑名单关键词
- (none)

## 7. 账户概览
- analysis_window: `2026-03-12 15:09:31 UTC -> 2026-04-11 15:05:31 UTC`
- trade_rows_used: `2091`
- total_buy_usdc: `102614.637336`
- total_sell_usdc: `64429.618819`
- traded_markets_count_api: `1472`
- position_value_api: `93605.649700`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `0.62%`
- dual_side_buy_usdc_ratio_1h: `0.00%`
- token_fast_20m_buy_usdc_ratio: `7.02%`
- noncopyable_token_fast_buy_ratio: `4.63%`
- noncopyable_token_fast_sell_ratio: `15.04%`
- noncopyable_token_fast_token_ratio: `19.05%`
- event_rebalance_20m_event_ratio: `6.67%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `53.96%`
- weighted_multi_market_risk_ratio: `18.88%`
- deployable_event_equivalent: `34.500000`
- deployable_event_density: `1.150106`
- active_trading_days: `31.000000`
- trade_count: `2091.000000`
- avg_trades_per_active_day: `67.451613`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `高波动上行`
- d30_score: `2`
- d7_shape: `高波动上行`
- d7_score: `1`
- pnl_tag: `长期/中期/短期均偏强`

## 10. 评分拆解
- copyability_score: `24.440000`
- deployability_score: `20`
- multi_market_structure_score: `11.130000`
- pnl_curve_stability_score: `27.750000`
- risk_penalty_adjustment: `0`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- (none)
