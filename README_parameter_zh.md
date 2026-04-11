# Polymarket 报告参数中文说明（总表）

本文档解释 `reportcase_26account_full` 与 `skill/polymarket-account-review-skill` 产物中的英文参数含义，方便人工复核。

## 1. 决策与锚点参数

| 参数 | 中文定义 | 说明 |
|---|---|---|
| `final_score` | 最终决策分 | 实际用于结论判定的分数；当前等于锚点校准分。 |
| `raw_score` | 原始评分 | 按规则直接计算的分数（含惩罚/封顶），未做锚点映射前。 |
| `anchored_score` | 锚点校准分 | 基于 60 分锚点基线映射后的分数，用于跨批次可比。 |
| `delta_vs_anchor_60` | 相对60分差值 | `anchored_score - 60`，正值表示高于及格基线。 |
| `delta_vs_anchor_raw` | 相对锚点原始分差值 | `raw_score - anchor_raw_base_score`。 |
| `decision` | 结论标签 | `relative_copyable` / `selective_copying_only` / `not_recommended`。 |
| `decision_zh` | 结论中文 | `decision` 的中文映射。 |
| `decision_score_basis` | 决策分口径 | 当前是 `calibrated_anchor_score`，表示用锚点校准分做判定。 |
| `anchor_version` | 锚点版本 | 本次评分使用的锚点配置版本。 |
| `anchor_account` | 锚点账户地址 | 60 分参考基线对应账户。 |
| `anchor_target_score` | 锚点目标分 | 锚点映射目标值（通常为 60）。 |
| `anchor_raw_base_score` | 锚点原始基准分 | 锚点账户在冻结窗口下算出的 `raw_score`。 |
| `anchor_offset` | 锚点平移量 | 历史兼容字段；新版主要使用比例校准。 |
| `anchor_calibration_scale` | 锚点缩放系数 | 控制 `raw_score` 到 `anchored_score` 的映射斜率。 |
| `anchor_enabled` | 是否启用锚点 | `true` 表示按锚点规则校准。 |

## 2. 账户身份与基础信息

| 参数 | 中文定义 | 说明 |
|---|---|---|
| `account_label` | 展示名称 | 报告主显示名，优先来自平台可读名称。 |
| `account_address` | 钱包地址 | 账户唯一地址。 |
| `source_name` | 平台名称字段 | 来源数据中的 `name` 字段。 |
| `source_pseudonym` | 平台昵称字段 | 来源数据中的 `pseudonym` 字段。 |
| `source_account_name` | 本地别名字段 | 来源 CSV 的 `account_name`。 |
| `analysis_window` | 分析窗口 | 交易数据覆盖的起止时间（UTC）。 |
| `trade_rows_used` | 有效交易行数 | 实际用于计算的交易记录条数。 |
| `generated_at_utc` | 生成时间 | 当前分析 JSON 的 UTC 时间戳。 |
| `summary_source` | 汇总来源 | `prefetched` / `live_fetch` / `missing`。 |

## 3. 资金与账户体量字段

| 参数 | 中文定义 | 说明 |
|---|---|---|
| `total_buy_usdc` | BUY 总名义金额 | 分析窗口内买入总额（USDC）。 |
| `total_sell_usdc` | SELL 总名义金额 | 分析窗口内卖出总额（USDC）。 |
| `positions_value` / `position_value_api` | 持仓估值 | 官方接口返回的当前持仓价值。 |
| `traded_markets` / `traded_markets_count_api` | 交易市场数 | 官方接口累计交易市场数量。 |

## 4. 交易频次与可部署性

| 参数 | 中文定义 | 说明 |
|---|---|---|
| `trade_count` | 交易笔数 | 分析窗口内交易总笔数。 |
| `active_trading_days` | 活跃交易天数 | 有交易发生的自然日数量。 |
| `window_days` | 窗口天数 | 分析时间跨度（天）。 |
| `active_day_ratio` | 活跃天占比 | `active_trading_days / window_days`。 |
| `avg_trades_per_active_day` | 活跃日均交易笔数 | `trade_count / active_trading_days`。 |
| `deployable_event_equivalent` | 可利用事件等价值 | `clean + 0.5*semiclean` 的事件供给量。 |
| `deployable_event_density` | 可利用事件密度 | 可利用事件等价值按天归一化。 |
| `low_frequency_cap` | 低频封顶分 | 频次/密度不足时对 `raw_score` 的上限。 |

## 5. 结构风险与可复制性核心比率

说明：`*_ratio` 通常是 0~1 的比例，报告里显示为百分比。

| 参数 | 中文定义 | 说明 |
|---|---|---|
| `dual_side_condition_count_ratio` | 双边 condition 数量占比 | 同一 condition 上出现双向建仓的占比。 |
| `dual_side_buy_usdc_ratio` | 双边买入金额占比 | 双向结构相关 BUY 金额 / 总 BUY。 |
| `dual_side_buy_usdc_ratio_1h` | 1小时双边买入占比 | 1小时内双边结构 BUY 金额 / 总 BUY。 |
| `token_fast_20m_count` | 20分钟 token 快交易窗口数 | 短时快进快出窗口计数。 |
| `token_fast_20m_buy_usdc_ratio` | 快交易 BUY 占比 | 快交易窗口 BUY 金额 / 总 BUY。 |
| `token_fast_20m_sell_usdc_ratio` | 快交易 SELL 占比 | 快交易窗口 SELL 金额 / 总 SELL。 |
| `noncopyable_token_fast_buy_ratio` | 不可复制快交易 BUY 占比 | 高执行依赖型快交易 BUY 占总 BUY。 |
| `noncopyable_token_fast_sell_ratio` | 不可复制快交易 SELL 占比 | 高执行依赖型快交易 SELL 占总 SELL。 |
| `noncopyable_token_fast_token_ratio` | 不可复制快交易 token 占比 | 触发不可复制特征的 token 覆盖占比。 |
| `event_rebalance_20m_count` | 20分钟事件再平衡次数 | 事件级快速调仓次数。 |
| `event_rebalance_20m_event_ratio` | 快速再平衡事件占比 | 发生再平衡的事件数占比。 |
| `event_rebalance_20m_buy_ratio` | 快速再平衡 BUY 占比 | 再平衡窗口 BUY 金额 / 总 BUY。 |
| `event_rebalance_20m_sell_ratio` | 快速再平衡 SELL 占比 | 再平衡窗口 SELL 金额 / 总 SELL。 |
| `exclusive_multi_market_buy_ratio` | 互斥型多子市场 BUY 占比 | 互斥结构事件 BUY 金额占比。 |
| `nested_deadline_multi_market_buy_ratio` | 递进时限型 BUY 占比 | 递进结构事件 BUY 金额占比。 |
| `independent_multi_market_buy_ratio` | 近独立型 BUY 占比 | 近独立结构事件 BUY 金额占比。 |
| `unknown_multi_market_buy_ratio` | 未知结构 BUY 占比 | 关系未识别事件 BUY 金额占比。 |
| `exclusive_concurrent_leg_ratio` | 互斥并发腿占比 | 互斥关系下实质并发持腿强度。 |
| `nested_concurrent_leg_ratio` | 递进并发梯占比 | 递进关系下并发梯度强度。 |
| `exclusive_overlap_time_ratio` | 互斥重叠时长占比 | 互斥结构中并发重叠时间占比。 |
| `nested_overlap_time_ratio` | 递进重叠时长占比 | 递进结构中并发重叠时间占比。 |
| `weighted_multi_market_risk_ratio` | 加权结构风险比 | 对多子市场结构风险的综合加权指标。 |
| `exclusive_sequential_switch_count` | 互斥顺序切换次数 | 互斥腿之间换仓切换计数。 |
| `nested_sequential_roll_count` | 递进顺序滚动次数 | 递进梯度中的滚动换仓计数。 |
| `top1_event_buy_ratio` | 第一大事件集中度 | 最大单事件 BUY 占总 BUY。 |
| `top3_event_buy_ratio` | 前三事件集中度 | 前三大事件 BUY 占总 BUY。 |

## 6. 持仓周期相关

| 参数 | 中文定义 | 说明 |
|---|---|---|
| `median_holding_time_sec` | 持仓时长中位数（秒） | 基于匹配买卖（近似 FIFO）计算。 |
| `weighted_median_holding_time_sec` | 加权持仓中位时长（秒） | 以成交金额加权的持仓中位时长。 |
| `sell_usdc_ratio_within_20m` | 20分钟内平仓占比 | SELL 金额中 20 分钟内平仓部分占比。 |
| `sell_usdc_ratio_within_1h` | 1小时内平仓占比 | SELL 金额中 1 小时内平仓部分占比。 |

## 7. 事件质量与关键词画像

| 参数 | 中文定义 | 说明 |
|---|---|---|
| `clean_event_count` | clean 事件数 | 结构上较干净、可部署性较高的事件。 |
| `semiclean_event_count` | semiclean 事件数 | 可解释但需筛选的中间质量事件。 |
| `dirty_event_count` | dirty 事件数 | 高结构复杂度或高执行依赖事件。 |
| `sector_tags` | 板块标签 | 账户主要交易板块关键词聚类结果。 |
| `whitelist_keywords` | 白名单关键词 | 倾向可跟单的主题词。 |
| `hard_blacklist_keywords` | 硬黑名单关键词 | 原则上禁止跟单的主题词。 |
| `soft_blacklist_keywords` | 软黑名单关键词 | 仅在严格触发条件下才考虑的主题词。 |
| `whitelist_keyword_count` | 白名单词数量 | 白名单关键词总数。 |
| `hard_blacklist_keyword_count` | 硬黑名单词数量 | 硬黑名单关键词总数。 |
| `soft_blacklist_keyword_count` | 软黑名单词数量 | 软黑名单关键词总数。 |

## 8. PnL 曲线字段

| 参数 | 中文定义 | 说明 |
|---|---|---|
| `pnl_curve` | 收益曲线模块 | 包含 `all_time` / `d30` / `d7` 三窗口结果。 |
| `all_time_shape` / `d30_shape` / `d7_shape` | 曲线形态 | `smooth_up` / `volatile_up` / `flat` / `down` / `insufficient_data`。 |
| `all_time_score` / `d30_score` / `d7_score` | 窗口打分 | 各时间窗形态映射到的离散得分。 |
| `pnl_tag` / `summary_tag` | PnL 综合标签 | 三窗口综合后的摘要标签。 |
| `total_return` | 区间收益 | 窗口累计收益。 |
| `trend_slope` | 趋势斜率 | 收益曲线趋势方向与强度。 |
| `max_drawdown` | 最大回撤 | 窗口内最大回撤幅度。 |
| `daily_volatility` | 日波动 | 窗口内收益波动强度。 |
| `points_count` | 采样点数 | 曲线计算样本数量。 |
| `window` | 窗口标识 | `all_time` / `d30` / `d7`。 |

## 9. 评分拆解字段（score_breakdown）

| 参数 | 中文定义 | 说明 |
|---|---|---|
| `copyability_score` | 可复制性得分 | 复制难度维度得分（越高越可复制）。 |
| `deployability_score` | 可部署性得分 | 可跟单容量与稳定供给维度得分。 |
| `multi_market_structure_score` | 多子市场结构得分 | 结构清晰度与风险可控性得分。 |
| `pnl_curve_stability_score` | 收益曲线稳定得分 | 三窗口 PnL 形态的加权得分。 |
| `risk_penalty_adjustment` | 风险惩罚项 | 风险门槛相关扣分（负值为扣分）。 |
| `concentration_penalty` | 集中度惩罚 | 事件过度集中带来的额外扣分。 |
| `raw_before_cap` | 封顶前原始分 | 应用低频封顶前的中间分。 |
| `pnl_confidence` | PnL 置信度 | 三窗口可用性形成的置信因子。 |
| `pnl_windows_available` | 可用窗口数 | PnL 可用窗口数量。 |
| `caution_risk_gate_triggered` | 风险门槛触发 | 触发后禁止宽跟，仅允许筛选跟单。 |
| `severe_risk_gate_triggered` | 重风险门槛触发 | 触发后低分会强制判不推荐。 |

## 10. 汇总表字段（summary_all_accounts.*）

| 参数 | 中文定义 | 说明 |
|---|---|---|
| `rank` | 排名 | 按 `final_score` 降序。 |
| `account_address` | 账户地址 | 唯一地址。 |
| `account_label` | 展示名称 | 汇总展示名称。 |
| `raw_score` | 原始评分 | 见上文。 |
| `anchored_score` | 锚点校准分 | 见上文。 |
| `final_score` | 决策分 | 见上文。 |
| `delta_vs_anchor_60` | 相对60分差值 | 见上文。 |
| `delta_vs_anchor_raw` | 相对锚点原始分差值 | 见上文。 |
| `decision_score_basis` | 决策分口径 | 见上文。 |
| `decision` | 英文结论 | 见上文。 |
| `decision_zh` | 中文结论 | 见上文。 |
| `anchor_version` | 锚点版本 | 见上文。 |
| `anchor_account` | 锚点地址 | 见上文。 |
| `summary_source` | 汇总数据来源 | `prefetched` / `live_fetch` / `missing`。 |
| `deployable_event_equivalent` | 可利用事件等价值 | 见上文。 |
| `weighted_multi_market_risk_ratio` | 加权结构风险比 | 见上文。 |
| `exclusive_concurrent_leg_ratio` | 互斥并发腿占比 | 见上文。 |
| `nested_concurrent_leg_ratio` | 递进并发梯占比 | 见上文。 |
| `active_trading_days` | 活跃交易天数 | 见上文。 |
| `trade_count` | 交易笔数 | 见上文。 |
| `dual_side_buy_usdc_ratio` | 双边买入占比 | 见上文。 |
| `noncopyable_token_fast_buy_ratio` | 不可复制快交易 BUY 占比 | 见上文。 |
| `traded_markets` | 交易市场数 | 官方接口字段。 |
| `positions_value` | 持仓价值 | 官方接口字段。 |
| `report_en` | 英文报告路径 | 账户英文报告相对路径。 |
| `report_zh` | 中文报告路径 | 账户中文报告相对路径。 |

## 11. 如何快速解读

1. 先看 `decision` + `final_score`。  
2. 再看 `weighted_multi_market_risk_ratio`、`noncopyable_token_fast_buy_ratio`、`nested_concurrent_leg_ratio`。  
3. 再看 `pnl_tag` 与 `pnl_curve_stability_score`。  
4. 最后结合 `whitelist_keywords` / `hard_blacklist_keywords` 做实盘过滤。  
