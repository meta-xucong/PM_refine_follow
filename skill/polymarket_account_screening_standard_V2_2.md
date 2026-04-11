# Polymarket 跟单账户筛选通用标准（V2.2）

> 版本：**V2.2**  
> 目的：用于判断一个 Polymarket 账户是否值得跟单，并输出可执行的账户画像。  
> 本版在 v1.2.2 基础上，正式引入**多子市场关系分型**：  
> 1. **互斥型子市场（exclusive）**  
> 2. **时间递进 / 包含型子市场（nested deadline）**  
> 3. **弱相关 / 近独立型子市场（independent）**  
> 4. **暂无法判定型（unknown）**  
>
> 核心原则从“同一事件多子市场 = 一律高风险”升级为：  
> **多子市场是否危险，取决于子市场之间的关系类型，以及目标账户是否实质性同时持有多个相关腿。**

---

## 一、V2.1 的核心升级

V2.2 继承 V2.1 的多子市场并存原则，并在此基础上新增“收益曲线稳定性维度”。

V2.2 解决的是 V2 与 V2.1 共同遗漏的另一个关键问题：

即便一个账户在行为结构上较为可复制，如果它的历史累计盈亏曲线持续下行，或者近 30 天、近 7 天明显转弱，那么它对跟单者的实际参考价值也应该下降；反过来，如果一个账户建号以来、近 30 天、近 7 天的盈亏曲线都整体向上，且走势较平滑，则应额外加分。

因此，V2.2 正式把“收益曲线稳定性”纳入评分体系：

- **建号以来累计盈亏曲线平滑向上**：大加分
- **近 30 天累计盈亏曲线整体向上**：中加分
- **近 7 天累计盈亏曲线整体向上**：小加分
- 若对应周期整体向下，则按相同层级给予扣分

一句话概括：

> **V2.1 主要解决“行为上能不能跟”的问题；V2.2 进一步解决“这个账户长期、中期、短期的结果曲线是否值得信任”的问题。**

V2.2 解决的是 V2 中另一个非常关键的误伤点：

V2 虽然已经把“同一事件多个子市场”分成：

- `exclusive`
- `nested_deadline`
- `independent`
- `unknown`

并且不再一刀切地把所有 multi-market 行为都视为高风险；  
但它对 `exclusive` 和 `nested_deadline` 的处理仍然偏静态：

- 只要一个账户在历史上买过多个相关子市场
- 就容易被计入较高的结构风险

这仍然会误伤两类其实应被认可的行为：

1. **互斥型中的单腿持有、清仓后换仓**
2. **递进型中的单腿持有、roll/展期式切换**

这两类行为虽然都“历史上涉及多个子市场”，但它们未必在**同一时间实质性地同时持有多个相关腿**。  
而对跟单者来说，真正危险的，往往不是“曾经买过多个相关子市场”，而是：

- **是否长期同时持有多个互斥腿**
- **是否长期同时持有多个递进腿并依赖期限结构管理**
- **是否通过多腿并存来表达分布，而不是表达单边观点**

因此，V2.1 将以下原则正式提升为第一性原则：

> **对于互斥型与递进型多子市场事件，风险判断的核心，不是账户历史上是否买过多个相关子市场，而是它是否在同一时间实质性地同时持有多个相关腿。**

对应地，V2.1 的处理方式变成：

- **exclusive（互斥型）**
  - `exclusive_concurrent_multi_leg`：高风险，重罚
  - `exclusive_sequential_switch`：中低风险，可保留为 `semiclean`
- **nested_deadline（递进型）**
  - `nested_concurrent_ladder`：中高风险，重罚但弱于 exclusive
  - `nested_sequential_roll`：中低风险，通常保留为 `semiclean`
- **independent（弱相关型）**
  - 继续低罚或放行
- **unknown**
  - 继续保守中性处理

并且允许以下情况作为**可接受的过渡重叠**，不直接判成高危结构：

- 重叠时间很短
- 重叠金额很小
- 旧腿已接近清仓，只是换仓尾单未完全结束

一句话概括：

> **V2 关注“子市场关系类型”；V2.1 在此基础上，进一步关注“这些相关腿是否被实质性同时持有”。**

## 二、适用前提

本标准适用于基于 Polymarket 公开交易数据（如 `activity` / `trades` 导出的 CSV）对账户进行行为分析。

推荐分析窗口：

- **主窗口：近 30 天**
- **辅助窗口：近 7 天**（观察风格是否突变）

推荐基础字段：

- `timestamp`
- `eventSlug`
- `conditionId`
- `title`
- `side`（BUY / SELL）
- `outcome`
- `price`
- `size`
- `usdcSize`
- `transactionHash`

若原始数据提供 `token_id`，则在快交易检测中优先使用；否则以：

```text
token_key = conditionId + outcome
```

---

## 三、核心判断目标

判断一个账户是否值得跟，不再只看它是否盈利，而是同时看四件事：

### 3.1 可复制性
其盈利是否主要来自：

- 单边方向判断
- 可复制的持仓窗口
- 中短期再定价

而不是来自：

- 结构搭建
- 赔率曲线利用
- 分钟级执行速度
- 组合管理与卖出顺序

### 3.2 可利用性
在考核窗口内，该账户是否给出了足够多的**可利用话题**，使你能：

- 小仓位分散
- 多话题并行
- 不依赖 1–2 个事件吃收益

### 3.3 稳定性
可保留机会是否：

- 不过度集中
- 不是偶发地“恰好干净一次”
- 在一段时间内持续输出
- 对应的收益曲线是否长期、中期、短期均具备正向趋势

### 3.4 可执行性
最终分析结果是否能转化为：

- 账户级 `白名单关键词`
- 账户级 `硬黑名单关键词`
- 账户级 `软黑名单关键词`
- 账户级 `所属板块`
- 收益曲线评价（建号以来 / 近30天 / 近7天）

---

## 四、结构化套利 / 结构化交易：总体定义

“结构化套利”在本标准里，不局限于严格无风险套利，也包括所有对滞后跟单者不友好的**结构化组合交易**。

典型表现：

- 同一 `conditionId` 双边买入
- 同一事件内多条腿同时建仓
- 同一事件内频繁跨腿调仓
- 通过多个子市场表达一个分布，而不是单边观点
- 利润依赖结构管理、切腿顺序、期限切换或赔率曲线

---

## 五、一级结构风险：同一 market 双边买入

### 5.1 定义
在同一个 `conditionId` 上，账户曾经买过两个相反 outcome。

常见形式：

- 同一 `conditionId` 买过 `Yes` 和 `No`
- 同一 winner / range market 上，两边都碰过

### 5.2 指标

- `dual_side_condition_count_ratio`
- `dual_side_buy_usdc_ratio`
- `dual_side_buy_usdc_ratio_5m`
- `dual_side_buy_usdc_ratio_1h`
- `dual_side_buy_usdc_ratio_24h`

### 5.3 风险阈值

- **低风险**：< 10%
- **中风险**：10% – 25%
- **高风险**：25% – 40%
- **极高风险**：> 40%

短窗口强化：

- 5 分钟内切两边：极危险
- 1 小时内切两边：高危险
- 24 小时内切两边：中危险

---

## 六、二级结构风险：同一事件多个子市场建仓（V2.1 分型 + 并存原则）

V2.1 不再只看“历史上是否买过多个相关子市场”，而是先做**关系分型**，再看这些相关腿是否被**实质性同时持有**。

### 6.1 四种关系类型

#### A. 互斥型（exclusive）
定义：同一事件下多个子市场最终只能有一个 YES。

典型场景：

- `who will win`
- `winner`
- 候选人 / 球队 / 电影 / 人选篮子盘
- 区间盘：`<X`、`X-Y`、`>Y`
- `highest grossing`
- `top scorer`
- `next leader`

V2.1 的关键修正：

- **如果账户只是先持有 A，清仓后再换到 B**，这更接近观点切换，不应直接按结构套利处理
- **如果账户在同一时间实质性地同时持有 A、B 或更多互斥腿**，这才是高危结构行为

因此，exclusive 进一步拆成：

- `exclusive_sequential_switch`：单腿持有、清仓后换仓，允许短暂小额重叠
- `exclusive_concurrent_multi_leg`：实质性并存多个互斥腿，高风险

**处理原则：**
- `exclusive_concurrent_multi_leg`：高风险，重罚
- `exclusive_sequential_switch`：中低风险，通常归入 `semiclean`

---

#### B. 时间递进 / 包含型（nested_deadline）
定义：多个子市场不是互斥，而是存在时间上的单调包含关系；若较早子市场发生，较晚子市场通常也一并发生。

典型场景：

- `by March 31`
- `by April 30`
- `by June 30`
- `before DATE`
- `on or before DATE`

V2.1 的关键修正：

- **如果账户主要是单腿持有，并在旧期限基本退出后再 roll 到新期限**，这是可接受的期限切换
- **如果账户长期并存持有多个 deadline 腿，并依赖期限结构管理**，则应视为更强的结构风险

因此，nested_deadline 进一步拆成：

- `nested_sequential_roll`：以单腿表达为主，允许顺序换期限
- `nested_concurrent_ladder`：实质性并存多个 deadline 腿，说明在做期限结构分布

**处理原则：**
- `nested_concurrent_ladder`：中高风险，重罚但弱于 exclusive
- `nested_sequential_roll`：中低风险，通常保留为 `semiclean`

---

#### C. 弱相关 / 近独立型（independent）
定义：多个子市场同属一个大事件，但彼此之间既不互斥，也不存在明显包含关系，发生与否相对独立。

典型场景：

- 同一大事件下多个国家/对象是否分别行动
- 同一大会/系列事件下多个独立子议题
- 同一地域下多个地点各自发生与否，但不构成唯一结果集

风险含义：

- 这类更接近“同板块多题材下注”
- 本身不应被简单视为结构化套利

**处理原则：低风险，原则上放行。**

---

#### D. 暂无法判定型（unknown）
定义：文本与结构信息不足，暂时无法较高置信度归入前三类。

**处理原则：保守中性处理。**

---

### 6.2 并存判定：什么叫“实质性同时持有多个相关腿”

对同一个 related cluster（exclusive 或 nested），按时间顺序重建每条腿的净仓位，检查任意时点是否出现：

- **2 条及以上** 相关腿净仓位同时显著大于 0

只有当满足“**重叠时间不短 + 重叠金额不小**”时，才记为实质性并存。  
以下情况应视为**允许的过渡重叠**，不直接记为高危结构：

- 重叠时间很短，例如 `< 3–5 分钟`
- 重叠金额很小，例如 `< 该 cluster 峰值净敞口的 10%`
- 旧腿只剩尾仓，正在清仓，而新腿刚开始建立

一句话理解：

- **历史上买过多个相关腿** ≠ 高危
- **实质性同时持有多个相关腿** = 高危信号

---

### 6.3 V2.1 的新指标

保留关系分型暴露指标：

- `exclusive_multi_market_buy_ratio`
- `nested_deadline_multi_market_buy_ratio`
- `independent_multi_market_buy_ratio`
- `unknown_multi_market_buy_ratio`

但对 `exclusive` 和 `nested_deadline`，新增更关键的**并存指标**：

#### exclusive 相关
- `exclusive_concurrent_leg_ratio`
  - 互斥型 cluster 中，发生“实质性同时持有 ≥2 腿”的买入金额 / 互斥型总买入金额
- `exclusive_overlap_time_ratio`
  - 互斥型 cluster 中，多腿并存的时间占比
- `exclusive_max_concurrent_legs`
  - 某互斥 cluster 曾同时持有的最大腿数
- `exclusive_sequential_switch_count`
  - 互斥型 cluster 中，清仓后顺序换到另一腿的次数

#### nested_deadline 相关
- `nested_concurrent_leg_ratio`
  - 递进型 cluster 中，发生“实质性同时持有 ≥2 deadline 腿”的买入金额 / 递进型总买入金额
- `nested_overlap_time_ratio`
  - 递进型 cluster 中，多 deadline 并存的时间占比
- `nested_max_concurrent_legs`
  - 某递进型 cluster 曾同时持有的最大腿数
- `nested_sequential_roll_count`
  - 递进型 cluster 中，顺序 roll 到下一期限的次数

建议保留一个总的加权结构风险：

```text
weighted_multi_market_risk_ratio
= 1.00 * exclusive_concurrent_component
+ 0.60 * exclusive_sequential_component
+ 0.60 * nested_concurrent_component
+ 0.30 * nested_sequential_component
+ 0.15 * independent_component
+ 0.50 * unknown_component
```

实操中可简化为：

```text
weighted_multi_market_risk_ratio
≈ 1.00 * exclusive_multi_market_buy_ratio * max(0.35, exclusive_concurrent_leg_ratio)
 + 0.55 * nested_deadline_multi_market_buy_ratio * max(0.30, nested_concurrent_leg_ratio)
 + 0.15 * independent_multi_market_buy_ratio
 + 0.50 * unknown_multi_market_buy_ratio
```

其中 `max(0.35, ...)` / `max(0.30, ...)` 的意义是：

- 即使某类 cluster 没有显著并存，也保留一个基础结构复杂度权重
- 但真正的大罚分来自并存比例，而不是“历史买过多个腿”本身

---

### 6.4 风险解释

#### exclusive_concurrent_leg_ratio
- **低风险**：< 10%
- **中风险**：10% – 25%
- **高风险**：25% – 45%
- **极高风险**：> 45%

#### nested_concurrent_leg_ratio
- **低风险**：< 15%
- **中风险**：15% – 30%
- **高风险**：30% – 50%
- **极高风险**：> 50%

#### exclusive_sequential_switch_count / nested_sequential_roll_count
- 单独出现时不应重罚
- 只有叠加快调仓、双边切换、极端集中时再升级风险

#### independent_multi_market_buy_ratio
- 单独不应重罚
- 只有叠加快调仓、双边切换、极端集中时再升级风险

#### weighted_multi_market_risk_ratio
建议作为账户级综合多子市场风险主指标之一：

- **低风险**：< 15%
- **中风险**：15% – 30%
- **高风险**：30% – 50%
- **极高风险**：> 50%

## 七、三级结构风险：事件内频繁调仓 / 切腿

### 7.1 定义
在同一 `eventSlug` 内，账户持续买入和卖出多个相关 `conditionId`，表现出明显的组合管理行为。

### 7.2 建议指标

- `event_two_way_activity_ratio`
- `event_multi_leg_turnover_ratio`
- `avg_condition_count_per_event_when_active`
- `event_rebalance_20m_ratio`（见第九章）

### 7.3 风险解释

若一个账户在大量事件中都表现出：

- 同事件多腿建仓
- 同事件短时间又买又卖
- 同事件多条件轮动
- 同事件跨 deadline 快速切换

则应视为**结构管理型账户**，即使其同 token 快 round-trip 不高，也不应被视为干净的单边观点号。

---

## 八、如何从技术角度区分三类多子市场事件

V2.1 推荐采用“**文本规则 + 结构特征 + 交易行为修正**”三层识别。

### 8.1 第一层：文本/标题规则

#### 识别 exclusive
优先检查标题、slug、outcome 中是否出现：

- `who will win`
- `winner`
- `which candidate`
- `which team`
- `highest grossing`
- `next leader`
- `box office`
- `opening weekend`
- `range`
- `between`
- `<` / `>` / `under` / `over`

这类通常是：

- 单一结果空间的枚举
- 最终只有一个 YES

#### 识别 nested_deadline
优先检查是否是一组同义命题，只是 deadline 不同：

- `by March 31`
- `by April 30`
- `by June 30`
- `before DATE`
- `on or before DATE`

技术上可以：

1. 对标题做规范化，去除日期表达
2. 若规范化后标题主体几乎相同
3. 且日期可提取、可排序
4. 则归入 `nested_deadline`

#### 识别 independent
若：

- 不满足 exclusive
- 也不满足 nested_deadline
- 各子市场对象不同，但不构成唯一结果集

则初步归为 `independent`

---

### 8.2 第二层：集合结构特征

#### exclusive 的结构特征
- 标题句式高度一致
- 差异主要是候选项 / 区间项
- 子市场数量常形成完整结果集合

#### nested_deadline 的结构特征
- 动作与对象相同
- 仅时间边界不同
- 子市场间天然存在先后顺序

#### independent 的结构特征
- 同属一个话题簇
- 但对象不同
- 不形成唯一结果集合
- 无明显时间包含关系

---

### 8.3 第三层：交易行为修正

文本分类后，仍需结合账户行为修正：

#### exclusive：先看是否并存持有多个互斥腿
- 若主要表现为**单腿持有 + 清仓后换仓**
  - 归入 `exclusive_sequential_switch`
  - 默认只记中低风险
- 若存在**实质性并存多个互斥腿**
  - 归入 `exclusive_concurrent_multi_leg`
  - 直接上调为高风险

#### nested_deadline：先看是否并存持有多个 deadline 腿
- 若主要表现为**单腿持有 + 顺序 roll 到更远期限**
  - 归入 `nested_sequential_roll`
  - 默认保留为 `semiclean`
- 若存在**实质性并存多个 deadline 腿**
  - 归入 `nested_concurrent_ladder`
  - 风险显著上调

#### independent + 快速跨腿调仓
即便题材结构不强，只要账户：

- 在 20 分钟内频繁跨 token 买卖
- 明显依赖事件内轮动

也应升级为高风险事件。

---

## 九、20 分钟快风险：主规则与辅规则

V2.1 延续 v1.2.1 的双层快风险定义。

### 9.1 主规则：同 token 快进快出（token fast）

#### 定义
以 `token_id` 为优先键；若没有，则使用：

```text
token_key = conditionId + outcome
```

在同一个 `token_key` 的任意 20 分钟滚动窗口中，若同时满足：

1. 同窗内同时出现 BUY 和 SELL
2. `BUY usdcSize >= 10`
3. `SELL usdcSize >= 10`
4. `min(BUY, SELL) / max(BUY, SELL) >= 0.2`
5. 且再满足至少一条：
   - 成交笔数 `>= 3`
   - `BUY + SELL >= 50`
   - 至少 2 笔 BUY 或至少 2 笔 SELL

则记为一次 `token_fast_candidate`。

### 9.2 高危快交易（non-copyable token fast）

若 `token_fast_candidate` 再满足以下条件中的至少 2 条，则定义为 `noncopyable_token_fast`：

- `first_sell_lag_sec < 120`
- `window_span_sec < 300`
- `buy_trade_count < 2` 或 `sell_trade_count < 2`
- `buy_max_trade_share > 0.6` 或 `sell_max_trade_share > 0.6`
- `fast_turnover_ratio > 0.7`
- `repeated_fast_windows_same_token >= 2`

### 9.3 主快风险指标

- `token_fast_20m_count`
- `token_fast_20m_buy_usdc_ratio`
- `token_fast_20m_sell_usdc_ratio`
- `noncopyable_token_fast_buy_ratio`
- `noncopyable_token_fast_sell_ratio`
- `noncopyable_token_fast_token_ratio`

建议阈值：

- `noncopyable_token_fast_buy_ratio > 20%`：高危
- `noncopyable_token_fast_sell_ratio > 25%`：高危
- `noncopyable_token_fast_token_ratio > 20%`：高危

---

### 9.4 辅规则：同 event 快调仓 / 切腿（event rebalance）

#### 定义
在同一个 `eventSlug` 的任意 20 分钟滚动窗口中，若：

1. 同窗内同时出现 BUY 和 SELL
2. `BUY usdcSize >= 10`
3. `SELL usdcSize >= 10`
4. `min(BUY, SELL) / max(BUY, SELL) >= 0.2`
5. 且至少满足一条：
   - 成交笔数 `>= 3`
   - 涉及 `>= 2` 个不同 `conditionId`
   - `BUY + SELL >= 50`

则记为一次 `event_rebalance_20m_candidate`。

#### 解释
这类行为不一定直接意味着你在某个 token 上跟不上，
但它通常意味着账户在做：

- 事件内调仓
- deadline 切换
- 结构腿轮动
- 多子市场再平衡

因此它更适合作为：

- 结构风险辅助指标
- `semiclean` / `dirty` 事件分类依据
- 黑名单与软黑名单的重要来源

#### 指标

- `event_rebalance_20m_count`
- `event_rebalance_20m_buy_ratio`
- `event_rebalance_20m_sell_ratio`
- `event_rebalance_20m_event_ratio`

---

## 十、账户层面的通用评估指标（V2.1）

### 10.1 结构风险相关

1. `dual_side_condition_count_ratio`
2. `dual_side_buy_usdc_ratio`
3. `dual_side_buy_usdc_ratio_1h`
4. `exclusive_multi_market_buy_ratio`
5. `exclusive_concurrent_leg_ratio`
6. `exclusive_overlap_time_ratio`
7. `exclusive_max_concurrent_legs`
8. `exclusive_sequential_switch_count`
9. `nested_deadline_multi_market_buy_ratio`
10. `nested_concurrent_leg_ratio`
11. `nested_overlap_time_ratio`
12. `nested_max_concurrent_legs`
13. `nested_sequential_roll_count`
14. `independent_multi_market_buy_ratio`
15. `unknown_multi_market_buy_ratio`
16. `weighted_multi_market_risk_ratio`
17. `event_two_way_activity_ratio`
18. `event_multi_leg_turnover_ratio`

### 10.2 快风险相关

#### 主快风险
1. `token_fast_20m_count`
2. `noncopyable_token_fast_buy_ratio`
3. `noncopyable_token_fast_sell_ratio`
4. `noncopyable_token_fast_token_ratio`

#### 辅快风险
5. `event_rebalance_20m_count`
6. `event_rebalance_20m_buy_ratio`
7. `event_rebalance_20m_sell_ratio`
8. `event_rebalance_20m_event_ratio`

### 10.3 持仓与行为相关

1. `median_holding_time`
2. `weighted_median_holding_time`
3. `sell_usdc_ratio_within_20m`
4. `sell_usdc_ratio_within_1h`
5. `buy_sell_same_event_ratio`

### 10.4 可利用性相关

1. `clean_event_count`
2. `semiclean_event_count`
3. `deployable_event_equivalent`
4. `deployable_event_density`
5. `top1_event_buy_ratio`
6. `top3_event_buy_ratio`

其中：

```text
deployable_event_equivalent = clean_event_count + 0.5 * semiclean_event_count
```

---

## 十一、事件级 clean / semiclean / dirty 判定（V2.1）

### 11.1 clean
满足大部分条件：

- 无同 token 高危快交易
- 无同一 condition 双边买入
- 不存在实质性并存的 exclusive / nested 多腿
- 无明显 event 级快调仓
- 不依赖结构性组合管理

### 11.2 semiclean
典型场景：

- `exclusive_sequential_switch`
- `nested_sequential_roll`
- independent 多子市场
- 有一定 event rebalance，但不重
- 存在一定结构复杂度，但主体仍可被理解为单边观点表达

### 11.3 dirty
出现以下任一倾向：

- `exclusive_concurrent_multi_leg` 明显
- `nested_concurrent_ladder` 明显
- 同 token 高危快交易重
- 双边切换明显
- event 级快调仓 / 切腿显著
- 利润明显依赖结构管理

---

## 十二、账户是否值得跟：V2.1 决策标准

### 12.1 直接排除（不值得跟）
若满足以下任一情况，建议直接排除：

#### A. 相关腿实质并存过高
满足任一：

- `exclusive_concurrent_leg_ratio > 35%`
- `nested_concurrent_leg_ratio > 40%` 且 `event_rebalance_20m_event_ratio` 不低
- `weighted_multi_market_risk_ratio > 50%` 且（`exclusive_concurrent_leg_ratio > 20%` 或 `nested_concurrent_leg_ratio > 25%`）

#### B. 主快风险过高
- `noncopyable_token_fast_buy_ratio > 20%`
- `noncopyable_token_fast_sell_ratio > 25%`
- `noncopyable_token_fast_token_ratio > 20%`

#### C. 双边切换明显
- `dual_side_buy_usdc_ratio > 40%`
- `dual_side_buy_usdc_ratio_1h > 20%`

#### D. 明显是事件内组合管理型账户
例如：

- 大量 `exclusive_concurrent_multi_leg` / `nested_concurrent_ladder`
- event rebalance 明显偏高
- clean 事件很少
- 收益看起来更依赖多腿并存和结构调整，而不是单腿观点

---

### 12.2 只适合筛着跟
若出现以下组合，建议只做过滤后跟单：

- `exclusive_concurrent_leg_ratio` 中等，但 `exclusive_sequential_switch_count` 高于并存事件数
- `nested_deadline_multi_market_buy_ratio` 较高，但主要表现为 `nested_sequential_roll`
- `independent_multi_market_buy_ratio` 高，但无明显快调仓和双边切换
- `event_rebalance_20m_event_ratio` 中等
- `weighted_median_holding_time` 为小时级

这类账户的使用方式：

- 不能全量跟
- 必须做账户级黑名单
- `exclusive_sequential_switch` 可以保留，但要警惕切换过快
- `nested_sequential_roll` 可以保留，但优先挑最直观单腿
- independent 类若无快调仓，可放行较大比例

---

### 12.3 相对可跟账户
若满足以下大部分条件，可视为相对可跟：

- `dual_side_buy_usdc_ratio < 15%`
- `exclusive_concurrent_leg_ratio < 10%`
- `nested_concurrent_leg_ratio < 15%`
- `weighted_multi_market_risk_ratio < 20%`
- `noncopyable_token_fast_buy_ratio < 10%`
- `noncopyable_token_fast_sell_ratio < 10%`
- exclusive 主要落在 `exclusive_sequential_switch` 或更少
- nested_deadline 主要落在 `nested_sequential_roll`
- independent 类型多数可放行
- 持仓时间以数小时到数天为主

---

## 十三、评分体系：可复制性 + 可利用性 + 稳定性

### 13.1 总体原则
V2.1 仍采用三维评分：

- **可复制性**（主体风险）
- **可利用性**（话题供给）
- **稳定性**（分散度与集中度）

### 13.2 多子市场风险记分方式
V2.1 不再仅凭“历史上买过多个相关子市场”来重扣，而是优先依据：

- `exclusive_concurrent_leg_ratio`：重扣
- `nested_concurrent_leg_ratio`：中重扣
- `exclusive_sequential_switch_count`：轻中扣，通常只影响上限，不直接判死
- `nested_sequential_roll_count`：轻扣，通常保留在 `semiclean`
- `independent_multi_market_buy_ratio`：轻扣
- `unknown_multi_market_buy_ratio`：保守中扣
- `weighted_multi_market_risk_ratio`：作为汇总参考

### 13.3 低频封顶规则（继续保留）
为避免 aff3 这类“高纯度、但几天只给 1–2 个机会”的账号拿过高分，保留以下封顶：

- `deployable_event_equivalent < 3` 或 `density < 0.10/天` → 总分最高 **55**
- `deployable_event_equivalent < 5` 或 `density < 0.17/天` → 总分最高 **62**
- `deployable_event_equivalent < 8` 或 `density < 0.26/天` → 总分最高 **70**

### 13.4 集中度附加扣分
- 若 `top1_event_buy_ratio > 50%` 且 `deployable_event_equivalent < 5`，额外扣 **5 分**
- 若 `top3_event_buy_ratio > 80%` 且 `deployable_event_equivalent < 8`，额外扣 **5 分**

### 13.5 及格线校准
V2.1 继续保留实盘锚点：

- **kekkone 型账户 = 60 分及格线**

也就是：

- 有一定缺陷
- 但可利用话题足够多
- 全量跟单未必优，但经过筛选后仍有正期望

---

## 十四、账户级关键词画像：板块、白名单与黑名单

V2.1 要求每个账户分析报告除了分数，还必须输出：

1. `所属板块`
2. `白名单关键词`
3. `账户级硬黑名单关键词`
4. `账户级软黑名单关键词`

### 14.1 所属板块
指该账户最主要、最稳定、最有代表性的题材簇。

常见示例：

- 地缘政治 / 战争 / ceasefire / strike
- 美国政治 / Trump / cabinet / election
- 体育 winner / championship / soccer
- 娱乐票房 / opening weekend / highest grossing
- 宏观经济 / Fed / recession / CPI
- crypto / BTC range / ETF / regulation

### 14.2 白名单关键词
`白名单关键词` 不是“出现这个词就必跟”，而是：

- 该账户在该词簇下，历史上更偏单边表达
- 结构风险低
- 双边与快交易少
- 适合作为优先观察区

### 14.3 账户级硬黑名单
满足以下倾向之一，建议进入 hard blacklist：

- 该词簇下大部分事件落在 `dirty`
- 互斥型结构腿明显
- token fast 或双边切换明显
- 该词簇几乎无法靠后验过滤修复

### 14.4 账户级软黑名单
满足以下倾向之一，建议进入 soft blacklist：

- 词簇内 clean / dirty 混合
- 多为 nested_deadline 或 moderate rebalance
- 只有在挑单腿、去除快交易、去除双边后才勉强可用

### 14.5 输出格式建议

```text
账户：XXXX
评分：XX/100
结论：相对可跟 / 部分可跟 / 不值得跟

所属板块：
- 板块 A
- 板块 B

白名单关键词：
- ...

账户级硬黑名单：
- ...

账户级软黑名单：
- ...
```

注意：

> **V2.1 不主张全局一刀切硬黑名单，而主张账户级精细化 hard / soft blacklist。**

---

## 十五、建议的实际筛选流程（V2.1）

### 第一步：账户级粗筛
先算账户整体指标：

- `dual_side_buy_usdc_ratio`
- `exclusive_multi_market_buy_ratio`
- `nested_deadline_multi_market_buy_ratio`
- `weighted_multi_market_risk_ratio`
- `noncopyable_token_fast_buy_ratio`
- `noncopyable_token_fast_sell_ratio`
- `deployable_event_equivalent`
- `deployable_event_density`

### 第二步：事件级关系分型
对每个 `eventSlug` 下的多子市场事件，先判：

- `exclusive`
- `nested_deadline`
- `independent`
- `unknown`

### 第三步：重建净仓位并判断是否实质并存
对 `exclusive` 与 `nested_deadline` cluster，重建各腿净仓位时间序列，识别：

- 是否同时持有 ≥2 条相关腿
- 是否只是短暂小额过渡重叠
- 是 `sequential_switch / sequential_roll` 还是 `concurrent_multi_leg / concurrent_ladder`

### 第四步：行为修正
再看该账户在每个事件上的行为是否有：

- 同 token 快 round-trip
- 同 condition 双边切换
- event rebalance
- 多腿轮动

### 第五步：事件分层
将事件打成：

- `clean`
- `semiclean`
- `dirty`

### 第六步：输出账户画像
对该账户总结：

- 所属板块
- 白名单关键词
- 账户级硬黑名单
- 账户级软黑名单

---

## 十六、脚本参数建议（V2.1）



## 十、收益曲线稳定性维度（V2.2 新增）

V2.2 正式将 **账户历史盈亏曲线** 纳入评分体系。

核心原则：

> **一个值得跟单的账户，不仅要“行为上可复制”，还应在收益结果上体现出相对稳定的正向累积。**

这里看的不是某几笔交易是否暴赚，而是账户在不同时间尺度上的累计盈亏曲线，是否体现出：

- 长期方向正确
- 中期没有明显失控
- 短期状态没有明显恶化
- 上行过程尽量平滑，而不是剧烈波动后侥幸盈利

### 10.1 三层时间尺度

建议至少评估以下三个周期：

1. **建号以来 / 样本可见全历史**
   - 用于判断账户是否长期具备稳定赚钱能力
   - 权重最高

2. **近 30 天**
   - 用于判断账户近期是否仍保持有效
   - 权重中等

3. **近 7 天**
   - 用于判断账户最近状态是否改善或恶化
   - 权重最低，但可用于动态微调

### 10.2 基本判断原则

#### A. 建号以来累计盈亏曲线平滑向上
这是 **大加分项**。

若建号以来累计盈亏曲线：

- 长期方向向上
- 回撤存在但不过度剧烈
- 上升过程较平滑

则应给予明显加分。

若建号以来累计盈亏曲线整体向下，则应给予明显扣分。

#### B. 近 30 天累计盈亏曲线整体向上
这是 **中加分项**。

若近 30 天累计盈亏曲线整体向上，应给予中等加分；
若近 30 天整体向下，应给予中等扣分。

#### C. 近 7 天累计盈亏曲线整体向上
这是 **小加分项**。

若近 7 天累计盈亏曲线整体向上，给予小加分；
若近 7 天整体向下，给予小扣分。

### 10.3 “平滑向上”比“高波动向上”更重要

V2.2 不建议只看最终累计收益是否为正，还要看 **收益曲线质量**。

应优先区分：

- **平滑向上型**：逐步累积、回撤可控、少依赖单笔暴赚
- **高波动向上型**：结果为正，但中间回撤很深，盈利依赖少数极端事件
- **震荡/走平型**：长时间没有明确上升趋势
- **持续下行型**：应明确扣分

因此，收益曲线评估不应只看“终点高低”，还应看：

- 最大回撤
- 回撤恢复速度
- 上涨段与下跌段的连续性
- 是否由少数异常大单主导

### 10.4 建议指标

建议至少计算以下指标：

- `equity_total_return_all_time`
- `equity_trend_slope_all_time`
- `equity_max_drawdown_all_time`
- `equity_total_return_30d`
- `equity_trend_slope_30d`
- `equity_max_drawdown_30d`
- `equity_total_return_7d`
- `equity_trend_slope_7d`
- `equity_max_drawdown_7d`

### 10.5 实战评分建议

建议把收益曲线稳定性单独作为一组 **附加分 / 附加扣分**：

#### 长期层（建号以来）
- 平滑明显向上：`+10 ~ +15`
- 向上但波动较大：`+4 ~ +9`
- 近似走平：`0 ~ +3`
- 明显向下：`-8 ~ -15`

#### 中期层（近 30 天）
- 整体向上：`+4 ~ +8`
- 近似走平：`0 ~ +2`
- 整体向下：`-4 ~ -8`

#### 短期层（近 7 天）
- 整体向上：`+1 ~ +4`
- 近似走平：`0 ~ +1`
- 整体向下：`-1 ~ -4`

### 10.6 使用原则

这组规则的定位是：

- **不是替代行为分析**
- **而是在行为分析通过后，对“结果稳定性”做加减分校正**

也就是说：

- 行为结构很差的账户，不能仅因收益曲线近期漂亮就放行
- 行为质量本来不错的账户，如果长期和近期收益曲线也向上，应进一步加分
- 若账户行为上可跟，但收益曲线长期明显下行，则要显著降分甚至降级

### 10.7 报告输出要求

在账户分析报告中，V2.2 建议新增一个固定部分：

#### 收益曲线评价
至少用描述性语言回答以下问题：

- 建号以来累计盈亏曲线是否平滑向上？
- 近 30 天累计盈亏曲线是否整体向上？
- 近 7 天累计盈亏曲线是否整体向上？
- 若向上，其质量是平滑上升还是高波动上升？
- 若向下，下行是持续恶化还是阶段性回撤？

并给出结论：

- `长期强 / 中期强 / 短期强`
- `长期强但近期转弱`
- `长期一般但近期转强`
- `长期与近期均偏弱`


```python
SCREENING_CONFIG = {
    # analysis window
    "analysis_window_days": 30,

    # 主快风险：same token 20m fast
    "fast_window_minutes": 20,
    "fast_token_key_mode": "token_id_or_condition_plus_outcome",
    "fast_min_buy_usd": 10,
    "fast_min_sell_usd": 10,
    "fast_balance_ratio_min": 0.2,
    "fast_min_trade_count": 3,
    "fast_min_total_turnover_usd": 50,
    "fast_min_buy_or_sell_leg_count": 2,

    # 主快风险：non-copyable token fast
    "noncopyable_token_fast_first_sell_lag_sec": 120,
    "noncopyable_token_fast_window_span_sec": 300,
    "noncopyable_token_fast_max_trade_share": 0.6,
    "noncopyable_token_fast_turnover_ratio": 0.7,
    "noncopyable_token_fast_repeated_windows": 2,
    "noncopyable_token_fast_rule_hits_required": 2,

    # 辅快风险：event rebalance
    "event_rebalance_window_minutes": 20,
    "event_rebalance_min_buy_usd": 10,
    "event_rebalance_min_sell_usd": 10,
    "event_rebalance_balance_ratio_min": 0.2,
    "event_rebalance_min_trade_count": 3,
    "event_rebalance_min_condition_count": 2,
    "event_rebalance_min_total_turnover_usd": 50,

    # V2.1：multi-market relation typing
    "exclusive_weight": 1.00,
    "nested_deadline_weight": 0.55,
    "independent_weight": 0.15,
    "unknown_weight": 0.50,

    # V2.1：相关腿并存判定（第一性原则）
    "related_leg_overlap_min_minutes": 3,
    "related_leg_overlap_material_ratio": 0.10,
    "related_leg_overlap_absolute_usd_floor": 10,
    "exclusive_concurrent_min_legs": 2,
    "nested_concurrent_min_legs": 2,

    # structure risk thresholds
    "high_risk_dual_side_buy_ratio": 0.25,
    "very_high_risk_dual_side_buy_ratio": 0.40,
    "high_risk_exclusive_concurrent_leg_ratio": 0.25,
    "very_high_risk_exclusive_concurrent_leg_ratio": 0.45,
    "high_risk_nested_concurrent_leg_ratio": 0.30,
    "very_high_risk_nested_concurrent_leg_ratio": 0.50,
    "high_risk_weighted_multi_market_risk_ratio": 0.30,
    "very_high_risk_weighted_multi_market_risk_ratio": 0.50,
    "high_risk_noncopyable_token_fast_buy_ratio": 0.15,
    "very_high_risk_noncopyable_token_fast_buy_ratio": 0.20,
    "high_risk_noncopyable_token_fast_sell_ratio": 0.15,
    "very_high_risk_noncopyable_token_fast_sell_ratio": 0.25,

    # deployability
    "deployable_event_min_buy_usd": 15,
    "semiclean_event_weight": 0.5,

    # score cap by deployable event equivalent
    "score_cap_if_deployable_event_equivalent_lt_3": 55,
    "score_cap_if_deployable_event_equivalent_lt_5": 62,
    "score_cap_if_deployable_event_equivalent_lt_8": 70,

    # score cap by deployable density
    "score_cap_if_density_lt_0_10": 55,
    "score_cap_if_density_lt_0_17": 62,
    "score_cap_if_density_lt_0_26": 70,

    # concentration penalties
    "extra_penalty_if_top1_gt_50_and_deployable_lt_5": 5,
    "extra_penalty_if_top3_gt_80_and_deployable_lt_8": 5,

    # passline anchor
    "passline_anchor_account_style": "kekkone_like",
    "passline_score": 60,
}
```

---

## 十七、最终通用结论（V2.1）

V2.1 最重要的升级，不是简单增加了几个指标，而是把“同事件多子市场”从**表面现象**推进到**结构本质**。

### 最值得记住的一句话

> **不是“多子市场”本身危险，  
> 而是“多子市场之间的关系类型 + 账户如何利用这种关系”决定危险程度。**

### 最实用的决策原则

- **互斥型多子市场**：只有在实质性同时持有多个互斥腿时才高风险；若主要是清仓后换仓，应降级看待
- **时间递进 / 包含型多子市场**：只有在实质性并存多个 deadline 腿时才显著升风险；顺序 roll 应保留为 `semiclean`
- **弱相关 / 近独立型多子市场**：低风险，原则上可放行
- **任何类型若叠加快调仓、双边切换、跨腿轮动**：再升级风险等级
- **同 token 高危快 round-trip**：仍是快风险主规则
- **虽然很干净，但低频、低覆盖、低分散**：也不能高分

如果一个账户：

- 互斥型结构腿可控
- 时间递进型多数可解释为期限表达而非结构套利
- 近独立型多子市场占比虽高但缺乏切腿与快风险
- 同 token 高危快交易低
- 并且近 30 天有足够多的可利用话题

那么它才更像一个真正值得实盘使用的跟单源。
---

## 十八、60分锚点基线机制（稳定评分补充条款）

> 本条款用于解决“不同批次数据、不同时间运行导致分数口径漂移”的问题。

### 18.1 锚点账户

固定锚点地址：
- `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

解释：
- 该地址对应你定义的 **60 分参考基线**。
- 后续所有账户分数都相对该锚点做统一平移，保证评分稳定可复现。

### 18.2 两层分数定义

1. `raw_score`：按 V2.2 原始规则（可复制性 / 可利用性 / 结构风险 / 收益曲线 / 封顶 / 扣分）直接计算。
2. `anchored_score`：在 `raw_score` 基础上做锚点平移：

```text
anchored_score = clamp(raw_score + score_offset, 0, 100)
score_offset   = 60 - anchor_raw_base_score
```

其中：
- `anchor_raw_base_score` 为锚点账户在冻结窗口下的原始分。
- `score_offset` 一旦冻结，不随日常评估变化。

### 18.3 判定使用 anchored_score

事件结论阈值改为基于 `anchored_score`：
- `>= 75`：`relative_copyable`
- `60 ~ 74.99`：`selective_copying_only`
- `< 60`：`not_recommended`

注意：
- **硬风控红线（hard exclusion）仍然优先**，不能被锚点平移覆盖。

### 18.4 锚点冻结与更新策略

默认策略：
- 锚点文件冻结，不自动重建。
- 仅在显式触发 `rebuild/re-anchor` 时更新。

建议存档字段：
- `anchor_version`
- `created_at_utc`
- `anchor_account`
- `target_anchor_score`
- `raw_base_score`
- `score_offset`
- `window_days`
- `data_fingerprint`
- `baseline_metrics`

### 18.5 报告输出强制项

每个账户报告必须额外展示：
- `raw_score`
- `anchored_score`
- `delta_vs_anchor_60 = anchored_score - 60`
- `anchor_version`
- `anchor_account`

### 18.6 批量汇总总表强制项

总表必须包含列：
- `raw_score`
- `anchored_score`
- `delta_vs_anchor_60`
- `decision`
- `anchor_version`
- `anchor_account`

这保证不同日期批量跑出的结果，始终可解释为“相对同一60分基线”的稳定比较。

## 19. 2026-04-11 Scoring Stabilization Addendum (Implementation Binding)

This addendum is binding for automated skill execution and resolves drift between descriptive review and scripted scoring.

1. Anchor usage remains reference-first:
- keep frozen anchor file and anchored score (`anchored_score`) for cross-run comparability.
- decision thresholding is based on calibrated `anchored_score`.
- `60` is a baseline reference, not automatic "recommended".

2. Risk-gated decision policy (replacing one-shot hard force):
- `>=78` and clean risk gate -> `relative_copyable`.
- `40..77.99` -> default `selective_copying_only`.
- `<40` -> default `not_recommended`.
- severe-risk gate + low score still forces `not_recommended`.

3. Low-frequency constraints are strengthened:
- caps depend on `deployable_event_equivalent`, `deployable_event_density`, `active_trading_days`, and `trade_count`.
- low activity can reduce score even when structure metrics look clean.

4. PnL curve influence is strengthened:
- three-window PnL score is confidence-weighted and upscaled versus earlier version.
- accounts with weak long/mid/short curve quality should be visibly pushed down.

5. Keyword filtering is strengthened for selective-copy mode:
- hard and soft blacklists are generated using weighted dirty ratios and event-level dirty boosts.
- most 40+ accounts should be operated via whitelist copy + blacklist blocking, not broad copying.

6. API retrieval follows two-layer policy:
- layer 1: prefetch account summary in data pull stage.
- layer 2: if missing/incomplete, analysis stage performs one live fallback query.
