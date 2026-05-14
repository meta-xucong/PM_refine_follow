# 10 当前评分机制评估与优化建议

## 结论

当前评分机制适合作为“人工复核辅助评分”和“小批量账户筛选”的基础，整体方向是合理的：它强调可复制性、结构风险、活跃度、PnL 曲线、锚点校准和关键词黑名单，能够避免只按收益高低盲目选账号。

但如果升级为“从最多 10 万候选账号里自动发现跟单目标”的常驻系统，当前机制还需要补一层自动化筛选和若干质量控制指标。否则容易出现两类偏差：

- 收益高但不可复制、数据不完整或过度高频的账号被打到可提醒区间。
- 真正适合跟单但收益曲线数据被截断、样本窗口不匹配或活跃度表达不充分的账号被低估。

## 当前评分标准总结

### 1. 核心分数结构

当前 raw score 由五类组件和一个集中度惩罚组成：

```text
raw_before_cap =
  copyability_score
+ deployability_score
+ multi_market_structure_score
+ pnl_curve_stability_score
+ risk_penalty_adjustment
- concentration_penalty
```

组件范围：

- `copyability_score`: `0..35`
- `deployability_score`: `0..20`
- `multi_market_structure_score`: `0..20`
- `pnl_curve_stability_score`: `-28..+28`
- `risk_penalty_adjustment`: `-34..0`
- `concentration_penalty`: `0..15`

### 2. 可复制性

主要扣分项：

- 双边 condition 买入占比
- 不可复制快交易 BUY/SELL 占比
- exclusive 并发腿
- nested 并发梯
- 加权多市场结构风险

这个模块是当前模型最有价值的部分，因为它直接面向“跟单能不能复现”。

### 3. 可部署性

主要加分项：

- `deployable_event_equivalent`
- `deployable_event_density`
- 活跃交易天数
- 活跃日均交易数
- 活跃日占比

低频账号会触发封顶，最高只能到 `48/56/64`。

### 4. 结构风险

主要扣分项：

- exclusive concurrent leg ratio
- nested concurrent leg ratio
- sequential switch / roll
- unknown multi-market buy ratio
- event rebalance ratio

### 5. PnL 曲线

当前用三窗口：

- all-time
- 30d
- 7d

每个窗口被分类为：

- `smooth_up`
- `volatile_up`
- `flat`
- `down`
- `insufficient_data`

再按可用窗口数做 confidence scaling，最终限制在 `-28..+28`。

### 6. 锚点校准

当前锚点账户：

```text
0x39d0f1dca6fb7e5514858c1a337724a426764fe8
```

锚点配置：

- `target_anchor_score = 60`
- `raw_base_score = 47.31`
- `calibration_scale = 0.65`

最终分数：

```text
anchored_score = clamp(60 + (raw_score - anchor_raw_base_score) * calibration_scale, 0, 100)
final_score = anchored_score
```

### 7. 风险门槛

两级门槛：

- `caution_risk_gate`: 禁止 broad copy，只能 selective-copy。
- `severe_risk_gate`: 如果 `final_score < 55`，强制 `not_recommended`。

### 8. 决策映射

- `relative_copyable`: `final_score >= 78`，且无 caution gate，PnL 不差，低频封顶不严格。
- `selective_copying_only`: `40 <= final_score < 78`
- `not_recommended`: `< 40`

额外规则：

- severe gate + `final_score < 55` => `not_recommended`
- `final_score < 32` => `not_recommended`

### 9. 关键词画像

根据 clean / semiclean / dirty 事件权重生成：

- whitelist keywords
- hard blacklist keywords
- soft blacklist keywords
- sector tags

这对“筛着跟”很重要。

## 合理的部分

1. 不是收益崇拜
   - 当前模型没有只看 PnL，而是把结构风险、快交易、双边、多市场复杂度放在前面。

2. 有锚点校准
   - 60 分标杆让跨批次比较更稳定。

3. 有低频封顶
   - 避免样本很少的账号因为看起来干净而虚高。

4. 风险门槛分层
   - caution / severe 比单一 hard reject 更适合真实账户行为。

5. 关键词黑名单可执行
   - 不只是给分，还能输出跟单过滤规则。

## 当前短板

### 1. PnL 数据可能被截断或取错时间段

当前 `fetch_polymarket_summary.py` 拉 `/closed-positions` 时使用：

```text
sortBy=TIMESTAMP
sortDirection=ASC
max_closed_records=5000
```

对于高活跃账号，如果已平仓记录超过 5000 条，可能优先拿到早期记录，导致 7d/30d PnL 曲线缺失或失真。

优化优先级：最高。

建议：

- 改成按 `DESC` 拉最近记录，用于 7d/30d。
- 另外按需拉 all-time 或用分页窗口拉取。
- 标记 `closed_positions_incomplete=true`，并降低 PnL confidence。

### 2. PnL 缺少归一化收益质量

当前 PnL 曲线主要看 realized PnL 累积形态，没有充分考虑：

- ROI
- return / volume
- return / positions_value
- profit factor
- win rate
- max drawdown ratio

这会偏向大资金账号，而不一定偏向“可复制高质量账号”。

### 3. leaderboard 信号没有进入最终评分

自动发现系统会从 leaderboard 来，但现有评分不使用：

- month leaderboard PnL
- month leaderboard volume
- week leaderboard PnL
- week leaderboard volume
- 多分类出现次数

这些不应直接决定最终分，但应进入 discovery/ranking 或 confidence。

### 4. 缺少数据完整性评分

现在缺数据主要写入 assumptions，PnL 设为 neutral，但没有形成独立的 `data_quality_score`。

自动系统里，数据完整性应该影响：

- 是否推送
- 推送等级
- 是否进入人工复核

### 5. 缺少跟单容量与流动性指标

当前 deployability 更多看事件数量和活跃天数，还没有纳入：

- 账号平均单笔金额
- 可跟随市场的成交深度
- 当前市场是否仍开放
- 价格是否极端接近 0/1
- target 买入后到 follower 发现之间的时间可复制性

这些决定“看到了以后还能不能跟”。

### 6. 自动提醒阈值太宽

`final_score > 40` 按当前定义只是进入 selective-copy 区间，不等于强推荐。自动推送如果只按一个阈值，消息会比较嘈杂。

建议继续按用户要求 `>40` 推送，但增加推送等级。

## 优化方案

### 优化 1: 增加三层评分输出

保留现有 `final_score`，新增：

1. `discovery_score`
   - 用于候选处理顺序。
   - 来自 leaderboard shard、近期 PnL、成交量、分类覆盖。

2. `copytrade_score`
   - 当前 `final_score` 的升级版。
   - 仍以结构风险和可复制性为核心。

3. `alert_grade`
   - 用于 ServerChan 消息分级。

建议分级：

| 条件 | 等级 |
|---|---|
| `final_score > 78` 且无 caution gate | `A / broad-copy candidate` |
| `final_score >= 65` 且风险低 | `B / strong selective` |
| `final_score > 40` | `C / watchlist selective` |
| `final_score <= 40` | 不推送 |

### 优化 2: 修复 PnL 拉取与曲线置信度

新增字段：

- `closed_positions_incomplete`
- `closed_positions_recent_coverage_days`
- `pnl_data_quality`
- `pnl_recent_records_count`

规则：

- 7d/30d 曲线必须优先用最近 closed positions。
- 如果最近窗口数据不完整，PnL score 降权。
- 如果只拿到 all-time 老数据，不允许给高 PnL 加分。

### 优化 3: 增加收益质量指标

建议新增：

- `realized_pnl_30d`
- `realized_pnl_7d`
- `pnl_per_volume_30d`
- `pnl_per_closed_position_30d`
- `profit_factor_30d`
- `win_rate_no_flat_30d`
- `drawdown_to_return_ratio`

评分方式：

- 不让绝对 PnL 单独拉高分。
- 用 ROI / PnL per volume 给收益质量加权。
- 负收益或高回撤直接降低 alert grade。

### 优化 4: 增加数据质量评分

新增 `data_quality_score: 0..10`：

加分：

- activity 完整
- summary 完整
- recent closed positions 完整
- snapshot 正常

扣分：

- API cap
- closed positions 截断
- PnL unknown
- activity split 失败

建议：

- `data_quality_score < 6` 时不发 A/B，只能 C 级观察。
- `data_quality_score < 4` 时不推送，只入库待复查。

### 优化 5: 增加跟单容量/执行可行性

新增 `copy_capacity_score: 0..10`：

指标：

- 平均 BUY notional 是否适中。
- 交易分布是否不是极小额刷量。
- 近期市场是否仍开放。
- 高频窗口占比。
- 极端价格交易占比。

建议：

- 小额刷量账号不应因 trade_count 高而获得 deployability 加分。
- 如果多数优势来自快速进出或临近结算市场，降低 copy capacity。

### 优化 6: 让高频从“预筛”和“评分”双重生效

预筛阶段：

- 明显 HFT 直接跳过。

评分阶段：

- 未被预筛跳过但活跃日均交易数极高的账号，增加 `automation_hft_penalty`。
- 例如：
  - `avg_trades_per_active_day > 600`: 强风险
  - `> 300`: 降 alert grade
  - `> 150`: 标记“需人工确认可复制性”

### 优化 7: 针对自动系统新增推荐口径

当前三分类保留：

- `relative_copyable`
- `selective_copying_only`
- `not_recommended`

新增自动系统字段：

- `auto_action`

建议：

| 条件 | `auto_action` |
|---|---|
| A 级 | `push_strong_candidate` |
| B 级 | `push_selective_candidate` |
| C 级 | `push_watchlist` |
| 数据不足但潜力高 | `defer_recheck` |
| 高频/结构脏 | `skip` |

这样 ServerChan 消息不会把所有 `>40` 混成一类。

## 推荐实施顺序

1. 先修 PnL 拉取方向和 recent coverage。
2. 增加 `data_quality_score`。
3. 增加 alert grade，不改变现有 final_score。
4. 增加 leaderboard-derived `discovery_score`，只用于候选排序。
5. 增加收益质量归一化指标。
6. 增加 copy capacity / liquidity proxy。
7. 第一轮真实扫描后，用 Excel 分布校准阈值。

## 最终建议

当前评分机制不要推倒重来。它的结构风险和可复制性判断是有价值的，应作为自动筛选系统的核心。

但自动系统必须把当前评分从“单一最终分”升级为：

```text
discovery_score -> 决定先看谁
final_score     -> 判断账号质量
data_quality    -> 判断结果可信不可信
alert_grade     -> 决定推送优先级和措辞
auto_action     -> 决定后续处理
```

这样既保留原模型的稳定性，又能适应大规模、长时间、自动化扫描。

