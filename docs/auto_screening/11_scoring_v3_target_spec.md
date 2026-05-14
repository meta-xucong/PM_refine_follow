# 11 Auto V3 目标评分机制规格

本文件定义自动筛选系统落地时要实现的新评分机制。它不是对当前 V2.2 评分的立即覆盖，而是程序与 skill 开发时共同落地的目标规格。

## 设计目标

Auto V3 要解决的问题：

- 大规模候选池下，先处理近期表现好且活跃的账号。
- 不让绝对 PnL 或大资金体量单独推高评分。
- 对数据不完整、近期 PnL 缺失、API 截断做显式降级。
- 总 PnL 为负的账号直接剔除；账号年龄不足 9 个月的账号直接剔除。
- 奖励长期平滑向上的 PnL 曲线和持续活跃，惩罚剧烈波动、单日尖峰和长期沉睡后近期突然放量。
- 对高频、快交易、临近结算、极端价格交易做更强约束。
- 把“分数高于 40 要推送”拆成不同推送等级，减少噪音。

## 输出字段

Auto V3 评分输出必须包含：

```json
{
  "score_version": "auto_v3",
  "legacy_v2_score": 0.0,
  "discovery_score": 0.0,
  "raw_score_v3": 0.0,
  "anchored_score_v3": 0.0,
  "final_score": 0.0,
  "data_quality_score": 0.0,
  "pnl_quality_score": 0.0,
  "copy_capacity_score": 0.0,
  "alert_grade": "none",
  "auto_action": "skip",
  "score_breakdown_v3": {},
  "score_flags": []
}
```

兼容要求：

- `final_score` 仍然保留，作为 ServerChan 和 Excel 的主分数。
- `decision` 仍然保留：`relative_copyable` / `selective_copying_only` / `not_recommended`。
- 现有报告、summary CSV、summary JSON 不能因为新增字段而失效。

## 总体结构

Auto V3 分成五层：

1. `discovery_score`
   - 决定候选处理顺序。
   - 不直接等于跟单质量。

2. `raw_score_v3`
   - 行为、收益、容量、风险、数据质量综合后的未校准分。

3. `anchored_score_v3`
   - 用标杆账号校准后的主评分。

4. `alert_grade`
   - 决定 ServerChan 推送等级和措辞。

5. `auto_action`
   - 决定自动系统如何处理该账号。

## Discovery Score

`discovery_score` 用于候选排序，不进入最终跟单质量分。

```text
discovery_score =
  40 * month_pnl_rank_score
+ 25 * month_vol_rank_score
+ 20 * week_pnl_rank_score
+ 10 * week_vol_rank_score
+  5 * category_diversity_score
```

规则：

- 每个 rank score 在 `0..1`。
- shard 中 rank 越靠前越接近 1。
- 缺失值记 0。
- 同一钱包多个 shard 命中时取最好 rank，并记录全部来源。

用途：

- `auto_screen` 先处理 `discovery_score` 高的账号。
- Excel 中展示该分数，方便理解账号为什么被优先处理。

## Raw Score V3

Auto V3 的 raw score 使用如下结构：

```text
raw_score_v3_before_cap =
  copyability_score_v3          # 0..30
+ deployability_score_v3        # 0..15
+ structure_score_v3            # 0..15
+ pnl_quality_score             # -20..25
+ copy_capacity_adjustment      # -10..10
+ data_quality_adjustment       # -10..3
+ leaderboard_consistency_adj   # -5..5
+ lifetime_pnl_adjustment       # -12..9
+ automation_risk_penalty       # -25..0
- concentration_penalty_v3      # 0..10
```

然后：

```text
raw_score_v3 = clamp(apply_caps(raw_score_v3_before_cap), 0, 100)
```

## Copyability Score V3

基础分：30。

扣分：

```text
copyability = 30
- dual_side_buy_usdc_ratio * 20
- noncopyable_token_fast_buy_ratio * 24
- exclusive_concurrent_leg_ratio * 26
- nested_concurrent_leg_ratio * 10
- weighted_multi_market_risk_ratio * 12
```

额外扣分：

- `noncopyable_token_fast_sell_ratio > 0.35`: `(ratio - 0.35) * 8`
- `noncopyable_token_fast_token_ratio > 0.30`: `(ratio - 0.30) * 6`
- `dual_side_buy_usdc_ratio_1h > 0.20`: 额外 `3`

范围：

```text
copyability_score_v3 = clamp(copyability, 0, 30)
```

## Deployability Score V3

基础由事件供给和活跃度组成：

```text
deployability =
  min(8.0, deployable_event_equivalent * 1.25)
+ min(4.0, deployable_event_density * 16.0)
+ min(2.0, active_trading_days * 0.18)
+ min(1.0, active_day_ratio * 2.0)
```

注意：

- 活跃日均交易数不再直接加太多分，避免高频刷交易被当成可部署性。
- 高频的影响放到 `automation_risk_penalty` 和 high-frequency caps。

范围：

```text
deployability_score_v3 = clamp(deployability, 0, 15)
```

## Structure Score V3

基础分：15。

扣分：

```text
structure = 15
- exclusive_concurrent_leg_ratio * 22
- nested_concurrent_leg_ratio * 12
- unknown_multi_market_buy_ratio * 7
- min(3.0, exclusive_sequential_switch_count * 0.15)
- min(2.5, nested_sequential_roll_count * 0.10)
```

额外扣分：

- `event_rebalance_20m_event_ratio > 0.25`: `2`
- `event_rebalance_20m_event_ratio > 0.45`: 再扣 `2`

范围：

```text
structure_score_v3 = clamp(structure, 0, 15)
```

## PnL Quality Score

PnL 必须先修复数据拉取方向：

- 7d/30d 使用最近 `/closed-positions`，优先 `sortDirection=DESC`。
- all-time 可以单独拉或用摘要估算。
- 如果最近窗口覆盖不足，降低 PnL confidence。

新增指标：

- `realized_pnl_7d`
- `realized_pnl_30d`
- `closed_positions_count_7d`
- `closed_positions_count_30d`
- `pnl_per_volume_30d`
- `pnl_per_closed_position_30d`
- `profit_factor_30d`
- `win_rate_no_flat_30d`
- `drawdown_to_return_ratio_30d`
- `closed_positions_recent_coverage_days`
- `closed_positions_incomplete`

分数结构：

```text
pnl_quality_score =
  pnl_shape_component       # -10..12
+ normalized_return_quality # -8..10
+ recent_momentum_component # -5..5
+ drawdown_component        # -5..0
```

### PnL Shape Component

沿用 V2.2 的 all-time / 30d / 7d shape，但权重略降：

```text
pnl_shape_component = clamp((all_time_score + d30_score + d7_score) * 1.25 * pnl_confidence, -10, 12)
```

### Normalized Return Quality

建议规则：

- `pnl_per_volume_30d >= 0.08`: `+10`
- `0.04..0.08`: `+6`
- `0.015..0.04`: `+3`
- `-0.015..0.015`: `0`
- `-0.05..-0.015`: `-4`
- `< -0.05`: `-8`

如果 30d volume 不足，则降权 50%。

### Recent Momentum Component

- 30d 和 7d 都为正：`+5`
- 30d 正、7d 平：`+3`
- 30d 正、7d 负：`0`
- 30d 负、7d 正：`+1`
- 30d 负、7d 负：`-5`

### Drawdown Component

- `drawdown_to_return_ratio_30d <= 0.35`: `0`
- `0.35..0.75`: `-2`
- `0.75..1.25`: `-4`
- `> 1.25`: `-5`

范围：

```text
pnl_quality_score = clamp(total, -20, 25)
```

## Lifetime PnL Eligibility And Smoothness

这层是 Auto V3 的硬门槛和长期质量补充，不替代 7d/30d PnL，而是防止短期暴冲账号混入候选。

硬门槛：

- `account_total_pnl < 0`：直接剔除，`final_score` 最高 `39`，`decision=not_recommended`，`alert_grade=none`，`auto_action=skip`。
- `account_age_days < 270` 或无法确认账号年龄：直接剔除，`final_score` 最高 `39`，`decision=not_recommended`，`alert_grade=none`，`auto_action=skip`。

数据来源：

- `account_total_pnl` 优先使用 summary 中的 `account_total_pnl`；缺失时用 `closed_positions_realized_pnl_total + open_positions_cash_pnl_sum + open_positions_realized_pnl_sum` 估算。
- `account_age_days` 优先使用最早 closed position 时间推断。当前没有独立注册时间接口时，用“最早可验证交易/结算活动”作为保守代理；不能证明超过 9 个月则不推送。

软调整：

```text
lifetime_pnl_adjustment =
  pnl_smoothness_adjustment     # -10..6
+ lifetime_activity_adjustment  # -5..5
```

加分：

- all-time PnL `smooth_up`，且总 PnL 为正。
- 最大回撤相对总收益较低。
- 账号年龄长、活跃月份覆盖高、长期都有交易/结算活动。

扣分：

- all-time PnL `volatile_up`、`flat` 或 `down`。
- 最大回撤相对总收益过高。
- 单日收益尖峰占总正收益过高。
- 日收益波动相对总收益过高。
- 账号年龄长但历史活跃月份很少，且最近 30 天突然活跃。

输出字段：

- `score_breakdown_v3.account_total_pnl`
- `score_breakdown_v3.account_age_days`
- `score_breakdown_v3.lifetime_hard_blocks`
- `score_breakdown_v3.pnl_smoothness_adjustment`
- `score_breakdown_v3.lifetime_activity_adjustment`
- `score_breakdown_v3.lifetime_pnl_adjustment`

新增 flags：

- `negative_total_pnl`
- `account_age_under_9m`
- `account_age_unknown`
- `pnl_smooth_up`
- `pnl_spiky`
- `pnl_single_spike`
- `pnl_drawdown_high`
- `pnl_daily_volatility_high`
- `long_consistent_activity`
- `consistent_activity`
- `dormant_recent_spike`
- `sparse_lifetime_activity`

## Data Quality Score

独立输出 `data_quality_score: 0..10`。

加分项：

- activity CSV 完整：`+3`
- account summary 核心字段完整：`+2`
- recent closed positions 覆盖 30d：`+2`
- snapshot 正常：`+1`
- 没有 API cap / truncation：`+2`

扣分项优先覆盖：

- activity 拉取失败：最高 `3`
- summary 缺失：最高 `5`
- recent closed positions 明显截断：最高 `6`
- PnL unknown：最高 `6`

转换为 raw score 调整：

```text
if data_quality_score >= 8: data_quality_adjustment = +3
elif data_quality_score >= 6: data_quality_adjustment = 0
elif data_quality_score >= 4: data_quality_adjustment = -4
else: data_quality_adjustment = -10
```

推送限制：

- `data_quality_score < 6`: 不能给 A/B，只能 C。
- `data_quality_score < 4`: 不推送，只入库 `defer_recheck`。

## Copy Capacity Score

独立输出 `copy_capacity_score: 0..10`。

指标：

- `median_buy_notional`
- `p10_buy_notional`
- `p90_buy_notional`
- `tiny_trade_buy_ratio`
- `extreme_price_trade_ratio`
- `near_resolution_trade_ratio`
- `still_open_recent_market_ratio`
- `avg_trades_per_active_day`

建议规则：

基础分：5。

加分：

- 中位 BUY 金额适中，例如 `20..2000 USDC`: `+2`
- p90 不过大，普通跟单资金可复制: `+1`
- 近期交易的市场仍开放比例高: `+2`

扣分：

- 小额刷量占比高: `-2..-4`
- 极端价格交易占比高: `-2..-4`
- 临近结算/很短窗口交易占比高: `-2..-4`
- 活跃日均交易数过高: `-2..-5`

范围：

```text
copy_capacity_score = clamp(score, 0, 10)
copy_capacity_adjustment = (copy_capacity_score - 5) * 2
```

## Leaderboard Consistency Adjustment

该项用于轻量奖励候选来源一致性，不允许单独推高差账号。

```text
leaderboard_consistency_adj = clamp(adj, -5, 5)
```

建议：

- 同时出现在 `MONTH+PNL` 和 `MONTH+VOL`: `+2`
- 同时出现在 `WEEK+PNL` 和 `MONTH+PNL`: `+2`
- 命中 >= 3 个分类: `+1`
- 只出现在 VOL shard 且 PnL 为负: `-3`
- month 和 week PnL 都为负: `-5`

## Automation Risk Penalty

自动系统专用风险惩罚。

```text
automation_risk_penalty = 0
```

高频：

- `avg_trades_per_active_day > 600`: `-25`，且 `auto_action=skip`
- `> 300`: `-15`，alert grade 最高 C
- `> 150`: `-6`，增加人工确认 flag

数据截断：

- activity cap: `-8`
- closed positions cap: `-6`

强执行依赖：

- `noncopyable_token_fast_buy_ratio > 0.40`: 额外 `-8`
- `sell_usdc_ratio_within_20m > 0.50`: `-6`

范围：

```text
automation_risk_penalty = clamp(total, -25, 0)
```

## Concentration Penalty V3

沿用 V2.2，但收紧到 `0..10`：

- `top1_event_buy_ratio > 0.50` 且 `deployable_event_equivalent < 5`: `+4`
- `top3_event_buy_ratio > 0.80` 且 `deployable_event_equivalent < 8`: `+4`
- `top1_event_buy_ratio > 0.65` 且 `deployable_event_equivalent < 8`: 额外 `+2`

## Caps

### Low-Frequency Caps

沿用 V2.2：

- `cap=48`: `deployable < 3` 或 `density < 0.10` 或 `active_days < 4` 或 `trade_count < 40`
- `cap=56`: `deployable < 5` 或 `density < 0.17` 或 `active_days < 8` 或 `trade_count < 100`
- `cap=64`: `deployable < 8` 或 `density < 0.26` 或 `active_days < 12` 或 `trade_count < 180`

### High-Frequency Caps

新增：

- `avg_trades_per_active_day > 600`: skip，不推送
- `> 300`: final cap `64`
- `> 150`: final cap `72`

### Data Quality Caps

新增：

- `data_quality_score < 4`: final cap `39`，不推送
- `data_quality_score < 6`: final cap `58`

## Anchor V3

Auto V3 改变 raw score 结构，因此必须重建并冻结新锚点。

锚点账号不变：

```text
0x39d0f1dca6fb7e5514858c1a337724a426764fe8
```

目标：

```text
target_anchor_score = 60
```

新文件：

```text
skill/polymarket-account-review-skill/baseline/baseline_anchor_auto_v3.json
```

校准：

```text
anchored_score_v3 = clamp(60 + (raw_score_v3 - anchor_raw_base_score_v3) * calibration_scale, 0, 100)
calibration_scale = 0.65
final_score = anchored_score_v3
```

要求：

- 初次实现时对锚点账号重新按 Auto V3 算 raw。
- 生成 `baseline_anchor_auto_v3.json`。
- 不复用 V2.2 的 `raw_base_score=47.31`。

## Decision Mapping

保留三分类：

- `relative_copyable`
- `selective_copying_only`
- `not_recommended`

规则：

```text
relative_copyable:
  final_score >= 78
  and not caution_risk_gate
  and not severe_risk_gate
  and data_quality_score >= 8
  and copy_capacity_score >= 7
  and pnl_quality_score >= 4

selective_copying_only:
  final_score >= 40
  and data_quality_score >= 4
  and not skipped_by_hft

not_recommended:
  otherwise
```

保留 severe gate：

- severe gate + `final_score < 55` => `not_recommended`
- `final_score < 32` => `not_recommended`

## Alert Grade

ServerChan 推送仍按用户要求：`final_score > 40`。

但推送必须分级：

| 等级 | 条件 | 含义 |
|---|---|---|
| `A` | `final_score >= 78`, no caution/severe gate, `data_quality >= 8`, `copy_capacity >= 7` | 强候选，可重点人工复核 |
| `B` | `final_score >= 65`, no severe gate, `data_quality >= 7`, `copy_capacity >= 5` | 较强筛选跟单候选 |
| `C` | `final_score > 40`, `data_quality >= 4`, not skipped | 观察名单，只能筛着看 |
| `none` | 其他 | 不推送 |

等级上限：

- caution gate: 最高 B。
- `data_quality < 6`: 最高 C。
- `avg_trades_per_active_day > 300`: 最高 C。
- severe gate: 最高 C，且必须在消息里高亮。

## Auto Action

新增 `auto_action`：

| 条件 | auto_action |
|---|---|
| `alert_grade=A` | `push_strong_candidate` |
| `alert_grade=B` | `push_selective_candidate` |
| `alert_grade=C` | `push_watchlist` |
| `data_quality < 4` 且 discovery 高 | `defer_recheck` |
| 高频 skip 或 severe dirty | `skip` |
| `final_score <= 40` | `store_only` |

## Score Flags

必须输出 `score_flags`，方便 Excel 和 ServerChan 展示。

建议 flag：

- `hft_suspected`
- `activity_incomplete`
- `closed_positions_incomplete`
- `pnl_recent_missing`
- `data_quality_low`
- `copy_capacity_low`
- `caution_risk_gate`
- `severe_risk_gate`
- `high_dual_side`
- `high_noncopyable_fast`
- `leaderboard_negative_pnl`
- `strong_recent_pnl`
- `multi_category_hit`

## Skill 落地要求

需要更新：

- `skill/polymarket-account-review-skill/scripts/fetch_polymarket_summary.py`
- `skill/polymarket-account-review-skill/scripts/analyze_account.py`
- `skill/polymarket-account-review-skill/scripts/run_full_screening.py`
- `skill/polymarket-account-review-skill/scripts/render_report.py`
- `skill/polymarket-account-review-skill/schemas/output_schema.json`
- `skill/polymarket-account-review-skill/schemas/metrics_schema.json`
- `skill/polymarket-account-review-skill/references/scoring.md`
- `skill/polymarket-account-review-skill/references/pnl_curve_rules.md`

新增：

- `skill/polymarket-account-review-skill/references/scoring_auto_v3.md`
- `skill/polymarket-account-review-skill/baseline/baseline_anchor_auto_v3.json`

## Auto Screen 程序落地要求

需要新增：

- `auto_screen/scoring_features.py`
  - 从 leaderboard、activity、summary 中构建 Auto V3 额外特征。
- `auto_screen/scorer.py`
  - 调用 skill 的 Auto V3 scoring。
- `auto_screen/excel_store.py`
  - 写入 Auto V3 新字段。
- `auto_screen/notifier.py`
  - 按 `alert_grade` 格式化消息。

## 测试要求

新增测试：

- PnL 最近窗口优先，不能被早期 5000 条截断。
- data quality caps 生效。
- high-frequency caps 生效。
- alert grade 上限生效。
- v3 anchor 文件存在且字段完整。
- V2.2 和 Auto V3 可以同时解析旧产物。
