# Witty-Tripod

## 账户身份（优先人工核对）
- 展示名称: `Witty-Tripod`
- 账户地址: `0x05374492e37f036fb751d708fe487aeca60b5b0f`
- 平台昵称: `Witty-Tripod`
- 平台名称: `Frigg`
- 本地名称: `account_51`

## 1. 执行结论
校准后决策分 64.43（锚点口径），结论：只适合筛着跟。主要板块暴露：macro。优势：加权多子市场风险较低。风险点：存在同 condition 双边买入。硬黑名单主题（禁止跟）：crude、high、hit、oil、march。软黑名单主题（谨慎跟）：backpack、opensea。白名单主题（优先筛选）：gta、iceman、drake、release、fed。收益曲线标签：长期与近期均偏弱。建议仅在严格事件筛选和黑名单约束下筛选着跟。

## 2. 决策快照
- decision: `只适合筛着跟`
- final_score（决策分）: `64.430000`
- raw_score: `54.120000`
- anchored_score: `64.430000`
- delta_vs_anchor_60: `4.430000`
- delta_vs_anchor_raw: `6.810000`
- decision_score_basis: `calibrated_anchor_score`
- anchor_version: `anchor_v2_20260411`
- anchor_account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

## 3. 行为解读
- 观察到 365 笔交易，覆盖 22 个活跃交易日（分析窗口内）。
- 低频封顶已生效，封顶分数为 56, ，表明可跟单容量受限。
- 收益曲线形态： 全周期=smooth_up, 30d=insufficient_data, 7d=insufficient_data.
- 主要板块主题： macro.

## 4. 跟单优势
- 递进型并发行为相对可控。
- 加权多子市场结构风险整体可控。
- 全周期收益曲线为平滑上行，策略一致性较好。
- 可执行白名单主题：gta, iceman, drake, release, fed, meeting.

## 5. 跟单风险
- 同 condition 双边活动较高，跟单复现难度大。
- 交易频次/可利用度约束限制了实盘跟单容量。
- 硬黑名单主题（应避免）：crude, high, hit, oil, march, end.
- 软黑名单主题（需更严格触发）：backpack, opensea.

## 6. 板块与关键词过滤
### 所属板块
- macro

### 白名单关键词
- gta
- iceman
- drake
- release
- fed
- meeting
- there
- change
- interest
- rates

### 硬黑名单关键词
- crude
- high
- hit
- oil
- march
- end
- one
- launch
- above
- fdv
- day
- april

### 软黑名单关键词
- backpack
- opensea

## 7. 账户概览
- analysis_window: `2026-03-13 09:04:31 UTC -> 2026-04-11 08:12:29 UTC`
- trade_rows_used: `365`
- total_buy_usdc: `14040.834616`
- total_sell_usdc: `17016.936983`
- traded_markets_count_api: `829`
- position_value_api: `0.000000`

## 8. 核心指标
- dual_side_buy_usdc_ratio: `34.35%`
- dual_side_buy_usdc_ratio_1h: `11.46%`
- token_fast_20m_buy_usdc_ratio: `35.28%`
- noncopyable_token_fast_buy_ratio: `13.73%`
- noncopyable_token_fast_sell_ratio: `17.70%`
- noncopyable_token_fast_token_ratio: `17.39%`
- event_rebalance_20m_event_ratio: `12.50%`
- exclusive_concurrent_leg_ratio: `0.00%`
- nested_concurrent_leg_ratio: `12.96%`
- weighted_multi_market_risk_ratio: `13.81%`
- deployable_event_equivalent: `4.000000`
- deployable_event_density: `0.138103`
- active_trading_days: `22.000000`
- trade_count: `365.000000`
- avg_trades_per_active_day: `16.590909`

## 9. 收益曲线评估
- all_time_shape: `平滑上行`
- all_time_score: `12`
- d30_shape: `数据不足`
- d30_score: `0`
- d7_shape: `数据不足`
- d7_score: `0`
- pnl_tag: `长期与近期均偏弱`

## 10. 评分拆解
- copyability_score: `19.420000`
- deployability_score: `13.380000`
- multi_market_structure_score: `17.330000`
- pnl_curve_stability_score: `9.990000`
- risk_penalty_adjustment: `0`
- concentration_penalty: `6.000000`
- low_frequency_cap: `56`

## 11. 数据质量与假设
- (none)
