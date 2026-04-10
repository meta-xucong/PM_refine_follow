# Polymarket 跟单账户筛选通用标准（V2）

> 版本：**V2**  
> 目的：用于判断一个 Polymarket 账户是否值得跟单，并输出可执行的账户画像。  
> 本版在 v1.2.2 基础上，正式引入**多子市场关系分型**：  
> 1. **互斥型子市场（exclusive）**  
> 2. **时间递进 / 包含型子市场（nested deadline）**  
> 3. **弱相关 / 近独立型子市场（independent）**  
> 4. **暂无法判定型（unknown）**  
>
> 核心原则从“同一事件多子市场 = 一律高风险”升级为：  
> **多子市场是否危险，取决于子市场之间的关系类型，以及目标账户如何利用这种关系。**

---

## 一、V2 的核心升级

V2 解决的是旧版本里一个重要的误伤问题：

旧版虽然已经能识别：

- 结构化套利 / 结构腿
- 同 token 20 分钟快进快出
- 同 event 快调仓 / 切腿
- 低频高纯度但不可利用的账户

但在“**同一事件多个子市场同时建仓**”这件事上，旧版仍然偏粗：

- 只要同一个 `eventSlug` 下买了多个 `conditionId`
- 就会把这部分统一压入较高结构风险

这会把三种本质不同的情况混在一起：

1. **互斥型**：多个子市场最终只能有一个 YES，明显带有分布交易 / 篮子交易 / 结构套利特征
2. **时间递进 / 包含型**：例如 `by March 31 / by April 30 / by June 30`，较晚子市场包含较早子市场，不属于严格互斥
3. **弱相关 / 相对独立型**：同属一个大事件，但各子市场之间并无明显互斥或包含关系，很多时候接近正常的同板块分散下注

V2 的核心变化是：

- **把 multi-market 风险改成“先分类，再定风险”**
- **互斥型**重罚
- **时间递进型**中罚，可保留为 `semiclean`
- **弱相关型**低罚或放行
- **unknown** 用保守中性权重处理

一句话概括：

> **不是“多子市场”本身危险，而是“多子市场之间的关系 + 账户如何交易这些子市场”决定危险程度。**

---

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

### 3.4 可执行性
最终分析结果是否能转化为：

- 账户级 `白名单关键词`
- 账户级 `硬黑名单关键词`
- 账户级 `软黑名单关键词`
- 账户级 `所属板块`

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

## 六、二级结构风险：同一事件多个子市场同时建仓（V2 分型）

V2 不再把所有多子市场行为一刀切，而是先做**关系分型**。

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

风险含义：

- 账户更可能在交易结果分布或篮子，而不是单边观点
- 结构化特征强
- 对滞后跟单明显不友好

**处理原则：高风险，重罚。**

---

#### B. 时间递进 / 包含型（nested_deadline）
定义：多个子市场不是互斥，而是存在时间上的单调包含关系；若较早子市场发生，较晚子市场通常也一并发生。

典型场景：

- `by March 31`
- `by April 30`
- `by June 30`
- `before DATE`
- `on or before DATE`

风险含义：

- 账户可能在交易期限结构，而不是严格结构套利
- 仍有一定复杂性，但明显弱于互斥型
- 常见于多 deadline 版本的同一命题

**处理原则：中风险，可保留为 `semiclean`。**

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

风险含义：

- 不应直接按最坏情况处理
- 也不应当作完全无风险

**处理原则：保守中性处理。**

---

### 6.2 V2 的新指标

旧版核心指标：

- `multi_market_event_buy_usdc_ratio`

V2 将其拆成：

- `exclusive_multi_market_buy_ratio`
- `nested_deadline_multi_market_buy_ratio`
- `independent_multi_market_buy_ratio`
- `unknown_multi_market_buy_ratio`

建议再计算一个总的加权结构风险：

```text
weighted_multi_market_risk_ratio
= 1.00 * exclusive
+ 0.55 * nested_deadline
+ 0.15 * independent
+ 0.50 * unknown
```

建议权重区间：

- `exclusive`: 1.00
- `nested_deadline`: 0.45 – 0.60
- `independent`: 0.10 – 0.20
- `unknown`: 0.40 – 0.60

如无特别理由，推荐使用：

- `exclusive = 1.00`
- `nested = 0.55`
- `independent = 0.15`
- `unknown = 0.50`

### 6.3 风险解释

#### exclusive_multi_market_buy_ratio
- **低风险**：< 10%
- **中风险**：10% – 25%
- **高风险**：25% – 45%
- **极高风险**：> 45%

#### nested_deadline_multi_market_buy_ratio
- **低风险**：< 15%
- **中风险**：15% – 35%
- **高风险**：35% – 60%
- **极高风险**：> 60%

#### independent_multi_market_buy_ratio
- 单独不应重罚
- 只有叠加快调仓、双边切换、极端集中时再升级风险

#### weighted_multi_market_risk_ratio
建议作为账户级综合多子市场风险的主指标：

- **低风险**：< 15%
- **中风险**：15% – 30%
- **高风险**：30% – 50%
- **极高风险**：> 50%

---

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

V2 推荐采用“**文本规则 + 结构特征 + 交易行为修正**”三层识别。

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

#### exclusive + 同时买多个子市场
直接上调风险。

#### nested_deadline + 单边表达
若该账户：

- 主要是只买不切换
- 不快速卖出旧期限去买新期限
- 不双边切换

则可保留为 `semiclean`。

#### independent + 快速跨腿调仓
即便题材结构不强，只要账户：

- 在 20 分钟内频繁跨 token 买卖
- 明显依赖事件内轮动

也应升级为高风险事件。

---

## 九、20 分钟快风险：主规则与辅规则

V2 延续 v1.2.1 的双层快风险定义。

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

## 十、账户层面的通用评估指标（V2）

### 10.1 结构风险相关

1. `dual_side_condition_count_ratio`
2. `dual_side_buy_usdc_ratio`
3. `dual_side_buy_usdc_ratio_1h`
4. `exclusive_multi_market_buy_ratio`
5. `nested_deadline_multi_market_buy_ratio`
6. `independent_multi_market_buy_ratio`
7. `unknown_multi_market_buy_ratio`
8. `weighted_multi_market_risk_ratio`
9. `event_two_way_activity_ratio`
10. `event_multi_leg_turnover_ratio`

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

## 十一、事件级 clean / semiclean / dirty 判定（V2）

### 11.1 clean
满足大部分条件：

- 无同 token 高危快交易
- 无同一 condition 双边买入
- 非互斥型多子市场结构腿
- 无明显 event 级快调仓
- 不依赖结构性组合管理

### 11.2 semiclean
典型场景：

- nested_deadline 多子市场
- independent 多子市场
- 有一定 event rebalance，但不重
- 存在一定结构复杂度，但主体仍可被理解为单边观点表达

### 11.3 dirty
出现以下任一倾向：

- 互斥型多子市场买入明显
- 同 token 高危快交易重
- 双边切换明显
- event 级快调仓 / 切腿显著
- 利润明显依赖结构管理

---

## 十二、账户是否值得跟：V2 决策标准

### 12.1 直接排除（不值得跟）
若满足以下任一情况，建议直接排除：

#### A. 互斥型结构腿过高
- `exclusive_multi_market_buy_ratio > 35%`

或：
- `weighted_multi_market_risk_ratio > 50%`
且 `exclusive_multi_market_buy_ratio > 20%`

#### B. 主快风险过高
- `noncopyable_token_fast_buy_ratio > 20%`
- `noncopyable_token_fast_sell_ratio > 25%`
- `noncopyable_token_fast_token_ratio > 20%`

#### C. 双边切换明显
- `dual_side_buy_usdc_ratio > 40%`
- `dual_side_buy_usdc_ratio_1h > 20%`

#### D. 明显是事件内组合管理型账户
例如：

- 大量 exclusive / nested_deadline 题材反复切换
- event rebalance 明显偏高
- clean 事件很少

---

### 12.2 只适合筛着跟
若出现以下组合，建议只做过滤后跟单：

- `exclusive_multi_market_buy_ratio` 中等
- `nested_deadline_multi_market_buy_ratio` 较高
- `independent_multi_market_buy_ratio` 高，但无明显快调仓和双边切换
- `event_rebalance_20m_event_ratio` 中等
- `weighted_median_holding_time` 为小时级

这类账户的使用方式：

- 不能全量跟
- 必须做账户级黑名单
- nested_deadline 类默认只保留最直观单腿
- independent 类若无快调仓，可放行较大比例

---

### 12.3 相对可跟账户
若满足以下大部分条件，可视为相对可跟：

- `dual_side_buy_usdc_ratio < 15%`
- `exclusive_multi_market_buy_ratio < 10%`
- `weighted_multi_market_risk_ratio < 20%`
- `noncopyable_token_fast_buy_ratio < 10%`
- `noncopyable_token_fast_sell_ratio < 10%`
- nested_deadline 主要落在 `semiclean`
- independent 类型多数可放行
- 持仓时间以数小时到数天为主

---

## 十三、评分体系：可复制性 + 可利用性 + 稳定性

### 13.1 总体原则
V2 仍采用三维评分：

- **可复制性**（主体风险）
- **可利用性**（话题供给）
- **稳定性**（分散度与集中度）

### 13.2 多子市场风险记分方式
V2 不再直接使用粗暴的 `multi_market_event_buy_usdc_ratio` 扣分，而是优先依据：

- `exclusive_multi_market_buy_ratio`：重扣
- `nested_deadline_multi_market_buy_ratio`：中扣
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
V2 继续保留实盘锚点：

- **kekkone 型账户 = 60 分及格线**

也就是：

- 有一定缺陷
- 但可利用话题足够多
- 全量跟单未必优，但经过筛选后仍有正期望

---

## 十四、账户级关键词画像：板块、白名单与黑名单

V2 要求每个账户分析报告除了分数，还必须输出：

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

> **V2 不主张全局一刀切硬黑名单，而主张账户级精细化 hard / soft blacklist。**

---

## 十五、建议的实际筛选流程（V2）

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

### 第三步：行为修正
再看该账户在每个事件上的行为是否有：

- 同 token 快 round-trip
- 同 condition 双边切换
- event rebalance
- 多腿轮动

### 第四步：事件分层
将事件打成：

- `clean`
- `semiclean`
- `dirty`

### 第五步：输出账户画像
对该账户总结：

- 所属板块
- 白名单关键词
- 账户级硬黑名单
- 账户级软黑名单

---

## 十六、脚本参数建议（V2）

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

    # V2：multi-market relation typing
    "exclusive_weight": 1.00,
    "nested_deadline_weight": 0.55,
    "independent_weight": 0.15,
    "unknown_weight": 0.50,

    # structure risk thresholds
    "high_risk_dual_side_buy_ratio": 0.25,
    "very_high_risk_dual_side_buy_ratio": 0.40,
    "high_risk_exclusive_multi_market_buy_ratio": 0.25,
    "very_high_risk_exclusive_multi_market_buy_ratio": 0.45,
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

## 十七、最终通用结论（V2）

V2 最重要的升级，不是简单增加了几个指标，而是把“同事件多子市场”从**表面现象**推进到**结构本质**。

### 最值得记住的一句话

> **不是“多子市场”本身危险，  
> 而是“多子市场之间的关系类型 + 账户如何利用这种关系”决定危险程度。**

### 最实用的决策原则

- **互斥型多子市场**：高风险，优先视为结构化交易
- **时间递进 / 包含型多子市场**：中风险，可保留为 `semiclean`
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
