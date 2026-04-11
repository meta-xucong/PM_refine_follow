# {account_label}

## 账户身份（优先人工核对）
- 展示名称: `{account_label}`
- 账户地址: `{account_address}`
- 平台昵称: `{source_pseudonym}`
- 平台名称: `{source_name}`
- 本地名称: `{source_account_name}`

## 1. 执行结论
{narrative_conclusion}

## 2. 决策快照
- 结论标签: `{decision}`
- 决策分（最终用于判定）: `{final_score}`
- 原始评分（未锚点映射）: `{raw_score}`
- 锚点校准分: `{anchored_score}`
- 相对60分基线差值: `{delta_vs_anchor_60}`
- 相对锚点原始分差值: `{delta_vs_anchor_raw}`
- 判定口径: `{decision_score_basis}`
- 锚点版本: `{anchor_version}`
- 锚点账户: `{anchor_account}`

## 3. 行为解读
{behavior_points_bullets}

## 4. 跟单优势
{strength_points_bullets}

## 5. 跟单风险
{risk_points_bullets}

## 6. 板块与关键词过滤
### 主要板块标签
{sector_tags_bullets}

### 白名单关键词（优先筛选）
{whitelist_keywords_bullets}

### 硬黑名单关键词（原则上禁跟）
{hard_blacklist_keywords_bullets}

### 软黑名单关键词（严格触发才可跟）
{soft_blacklist_keywords_bullets}

## 7. 账户概览
- 分析时间窗口: `{analysis_window}`
- 有效交易记录数: `{trade_rows_used}`
- 买入总金额（USDC）: `{total_buy_usdc}`
- 卖出总金额（USDC）: `{total_sell_usdc}`
- 官方累计交易市场数: `{traded_markets_count_api}`
- 官方当前持仓估值: `{position_value_api}`

## 8. 核心指标
- 双边买入金额占比: `{dual_side_buy_usdc_ratio}`
- 1小时内双边买入占比: `{dual_side_buy_usdc_ratio_1h}`
- 20分钟快交易买入占比: `{token_fast_20m_buy_usdc_ratio}`
- 不可复制快交易买入占比: `{noncopyable_token_fast_buy_ratio}`
- 不可复制快交易卖出占比: `{noncopyable_token_fast_sell_ratio}`
- 不可复制快交易Token覆盖占比: `{noncopyable_token_fast_token_ratio}`
- 20分钟事件再平衡事件占比: `{event_rebalance_20m_event_ratio}`
- 互斥并发腿占比: `{exclusive_concurrent_leg_ratio}`
- 递进并发梯占比: `{nested_concurrent_leg_ratio}`
- 加权多子市场结构风险比: `{weighted_multi_market_risk_ratio}`
- 可利用事件等价值: `{deployable_event_equivalent}`
- 可利用事件密度: `{deployable_event_density}`
- 活跃交易天数: `{active_trading_days}`
- 交易总笔数: `{trade_count}`
- 活跃日均交易笔数: `{avg_trades_per_active_day}`

## 9. 收益曲线评估
- 全周期曲线形态: `{pnl_all_time_shape}`
- 全周期曲线得分: `{pnl_all_time_score}`
- 近30天曲线形态: `{pnl_30d_shape}`
- 近30天曲线得分: `{pnl_30d_score}`
- 近7天曲线形态: `{pnl_7d_shape}`
- 近7天曲线得分: `{pnl_7d_score}`
- 收益曲线综合标签: `{pnl_tag}`

## 10. 评分拆解
- 可复制性得分: `{copyability_score}`
- 可部署性得分: `{deployability_score}`
- 多子市场结构得分: `{multi_market_structure_score}`
- 收益曲线稳定性得分: `{pnl_curve_stability_score}`
- 风险惩罚项: `{risk_penalty_adjustment}`
- 集中度惩罚项: `{concentration_penalty}`
- 低频封顶分: `{low_frequency_cap}`

## 11. 数据质量与假设
{assumptions_bullets}
