# Sinful-Corduroy

## 账户身份（优先人工核对）
- 展示名称: `Sinful-Corduroy`
- 账户地址: `0xbe8b476070be7214c04e2b73ef56ad933157d14d`
- 平台昵称: `Sinful-Corduroy`
- 平台名称: `hberry`
- 本地名称: `account_48`

## 1. 执行结论
校准后决策分 24.07（锚点口径），结论：不值得跟。主要板块暴露：crypto、sports。优势：可利用事件覆盖广、加权多子市场风险较低。风险点：递进型并存梯度风险偏高、存在不可复制的 token 快交易暴露。硬黑名单主题（禁止跟）：march、down、bitcoin、ethereum、am-12。软黑名单主题（谨慎跟）：pm-11。白名单主题（优先筛选）：april、reach、am-9、am-3、pm-10。风险门槛已触发，宽跟模式自动关闭。重风险门槛已触发，低分情形会被强制判定为不值得跟。收益曲线标签：长期与近期均偏弱。不建议作为主跟单源，仅可少量人工挑选。

## 2. 决策快照
- decision: `不值得跟`
- final_score（决策分）: `24.070000`
- raw_score: `28.050000`
- anchored_score: `24.070000`
- delta_vs_anchor_60: `-35.930000`
- delta_vs_anchor_raw: `-55.270000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 2146 笔交易，覆盖 14 个活跃交易日（分析窗口内）。
- 收益曲线形态： 全周期=down, 30d=smooth_up, 7d=insufficient_data.
- 主要板块主题： crypto, sports.

## 4. 跟单优势
- 加权多子市场结构风险整体可控。
- 可利用主题供给相对充分，具备筛选跟单空间。
- 近 30 天收益曲线表现仍偏正向。
- 可执行白名单主题：april, reach, am-9, am-3, pm-10, am-7.

## 5. 跟单风险
- 递进型并发梯度比例偏高，结构管理负担较重。
- 已触发风险门槛，禁止宽跟，只能严格筛选跟单。
- 已触发重风险门槛，差质标的会被自动归为不值得跟。
- 全周期收益并非明显上行，持续优势可信度下降。
- 硬黑名单主题（应避免）：march, down, bitcoin, ethereum, am-12, temperature.
- 软黑名单主题（需更严格触发）：pm-11.

## 6. 板块与关键词过滤
### 所属板块
- crypto
- sports

### 白名单关键词
- april
- reach
- am-9
- am-3
- pm-10
- am-7
- pm-4

### 硬黑名单关键词
- march
- down
- bitcoin
- ethereum
- am-12
- temperature
- highest
- shanghai
- pm-12
- am-10
- am-11
- am-6

### 软黑名单关键词
- pm-11

## 7. 账户概览
- analysis_window: `2026-03-19 05:34:47 UTC -> 2026-04-01 14:15:27 UTC`
- trade_rows_used: `2146`
- total_buy_usdc: `181147.467371`
- total_sell_usdc: `15583.779989`
- traded_markets_count_api: `737`
- position_value_api: `0.000000`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `16.81%`
- dual_side_buy_usdc_ratio_1h: `16.22%`
- token_fast_20m_buy_usdc_ratio: `16.32%`
- noncopyable_token_fast_buy_ratio: `16.10%`
- noncopyable_token_fast_sell_ratio: `92.07%`
- noncopyable_token_fast_token_ratio: `24.20%`
- event_rebalance_20m_event_ratio: `0.00%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `71.03%`
- weighted_multi_market_risk_ratio: `1.18%`
- deployable_event_equivalent: `420.500000`
- deployable_event_density: `31.470843`
- active_trading_days: `14.000000`
- trade_count: `2146.000000`
- avg_trades_per_active_day: `153.285714`

## 9. 收益曲线评估
- all_time_shape: `下行`
- all_time_score: `-10`
- d30_shape: `平滑上行`
- d30_score: `6`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `13.200000`
- deployability_score: `20`
- multi_market_structure_score: `8.400000`
- pnl_curve_stability_score: `-5.550000`
- risk_penalty_adjustment: `-8.000000`
- concentration_penalty: `0.000000`
- low_frequency_cap: `n/a`

## 11. 数据质量与假设
- 触发风险门槛，禁止宽跟模式，需严格黑名单筛选
- 触发重风险门槛，不值得跟的判定阈值被收紧
- 重风险门槛叠加低分，判定为不值得跟
- 校准分低于 32，触发不值得跟底线
