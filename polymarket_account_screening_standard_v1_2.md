# Polymarket 跟单账户筛选通用标准（结构化套利 + 20 分钟快进快出 + 可利用性评分）

> 版本：v1.2  
> 目的：用于判断一个 Polymarket 账户是否值得跟单，重点识别三类核心问题：  
> 1. **结构化套利 / 结构化交易**  
> 2. **20 分钟内同话题快进快出**  
> 3. **低频低覆盖导致的“高分但不可利用”问题**
>
> 这是一套**实战筛选标准**，不是平台官方定义。目标不是完美还原账户策略，而是尽量过滤掉**不适合滞后跟单**的账户或题材，并把真正具有**可复制性 + 可利用性**的账户排在前面。

---

## 一、这次版本更新的核心变化

v1.1 的核心强项，是识别：

- 结构化套利 / 结构腿
- 20 分钟同话题快进快出
- 快但可跟 vs 高危快交易

但在实战中会出现一个漏洞：

> 某些账户虽然非常干净，几乎不做结构、不做快进快出，但**分析窗口内只下单极少数话题**。这类账户从“纯净度”角度会得到很高分，但对小仓位、多话题分散跟单者而言，**实际可利用价值并不高**。

例如：

- 你每个话题最多跟 **10U**
- 你依赖**多话题分散**来降低单题材波动
- 如果一个账户近几天只给出 1–2 个可跟话题，那么即使它极干净，也无法稳定提供足够的跟单机会

因此，v1.2 明确把账户评分拆成两部分：

1. **可复制性（copyability）**：这个账户的行为是否适合滞后跟单
2. **可利用性（deployability）**：这个账户在考核周期内，是否提供了足够多、足够分散、足够持续的可跟话题

一句话概括：

> **v1.1 主要回答“能不能跟”，v1.2 还要回答“值不值得纳入你的跟单池”。**

---

## 二、适用前提

本标准适用于基于 Polymarket 公开交易数据（如 `activity` / `trades` 导出的 CSV）对账户进行行为分析。

推荐分析窗口：

- **主窗口：近 30 天**
- **辅助窗口：近 7 天**（用于识别最近风格突变）

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

---

## 三、核心判断目标

判断一个账户是否值得跟，不再只是看它是否盈利，也不只是看它是否“干净”，而是要同时看三件事：

### 3.1 可复制性
这个账户的盈利，是否主要来自：

- 单边方向判断
- 中短期再定价
- 你能复制的买入和卖出窗口

而不是来自：

- 结构搭建
- 对冲切腿
- 分钟级执行速度
- 组合管理和卖出顺序

### 3.2 可利用性
这个账户在最近 30 天内，是否给出了足够多的**可保留话题**，使你能：

- 用小仓位分散布局
- 不依赖单一题材
- 不因为某一个事件失手而显著伤害整体收益

### 3.3 稳定性
这些可保留话题是否：

- 足够分散
- 不过度集中在 1–2 个事件
- 不是偶发地“恰好干净一次”

---

## 四、结构化套利 / 结构化交易：定义与识别标准

这里沿用 v1.1 的核心定义：

### 4.1 一级定义：同一 market 双边买入

#### 定义
在同一个 `conditionId` 上，账户曾经买过两个相反 outcome。

#### 建议指标

- `dual_side_condition_count_ratio`
- `dual_side_buy_usdc_ratio`
- `dual_side_buy_usdc_ratio_5m`
- `dual_side_buy_usdc_ratio_1h`
- `dual_side_buy_usdc_ratio_24h`

#### 风险阈值

- **低风险**：< 10%
- **中风险**：10% – 25%
- **高风险**：25% – 40%
- **极高风险**：> 40%

短窗口强化条件：

- 5 分钟内切两边：极危险
- 1 小时内切两边：高危险
- 24 小时内切两边：中危险

### 4.2 二级定义：同一事件多个子市场同时建仓

#### 定义
在同一个 `eventSlug` 下，账户同时买入多个不同 `conditionId`，且这些子市场互斥、高相关，或天然构成组合腿。

#### 典型场景

- 候选人 / winner / election 篮子盘
- 区间盘、box office、opening weekend
- margin / runoff / second round / advance
- 同一地缘事件下多个 deadline、多条互斥或相关子市场

#### 建议指标

- `multi_market_event_buy_usdc_ratio`
- `event_multi_market_yes_count`
- `event_multi_market_outcome_count`

#### 风险阈值

- **低风险**：< 15%
- **中风险**：15% – 35%
- **高风险**：35% – 60%
- **极高风险**：> 60%

### 4.3 三级定义：事件内频繁调仓 / 切腿

#### 定义
在同一 `eventSlug` 内，账户持续买入和卖出多个相关 `conditionId`，表现出明显的组合管理行为。

#### 建议指标

- `event_two_way_activity_ratio`
- `event_multi_leg_turnover_ratio`
- `avg_condition_count_per_event_when_active`

如果一个账户在大量事件里都呈现：

- 同事件多腿建仓
- 同事件短期内又买又卖
- 同事件多条件轮动

则应视为**结构化账户**，默认不适合直接跟单。

### 4.4 其他典型结构化高危行为

建议优先警惕以下关键词簇：

- `which countries`
- `who will win`
- `who will advance`
- `advance to the second round`
- `runoff`
- `margin of victory`
- `opening weekend`
- `box office`
- `between X and Y`
- `successor`
- `supreme leader`

---

## 五、20 分钟快进快出：定义、分层与识别标准

这一部分沿用 v1.1 的核心逻辑：

### 5.1 候选快事件（fast candidate）

在同一个 `eventSlug` 的任意 20 分钟滚动窗口中，若同时满足：

1. 同窗内同时出现 BUY 和 SELL
2. `BUY usdcSize >= 10`
3. `SELL usdcSize >= 10`
4. `min(BUY, SELL) / max(BUY, SELL) >= 0.2`
5. 且再满足至少一条：
   - 成交笔数 `>= 3`
   - 涉及 `>= 2` 个 `conditionId`
   - `BUY + SELL >= 50`

则记为一次 `fast candidate`。

### 5.2 二次判定：高危快交易（non-copyable fast）

对命中的 `fast candidate`，继续计算：

- `first_sell_lag_sec`
- `window_span_sec`
- `buy_trade_count`
- `sell_trade_count`
- `buy_max_trade_share`
- `sell_max_trade_share`
- `fast_turnover_ratio`
- `repeated_fast_windows_same_event`

满足候选快事件后，若再满足以下条件中的至少 2 条，建议归为**高危快交易**：

- `first_sell_lag_sec < 120`
- `window_span_sec < 300`
- `buy_trade_count < 2` 或 `sell_trade_count < 2`
- `buy_max_trade_share > 0.6` 或 `sell_max_trade_share > 0.6`
- `fast_turnover_ratio > 0.7`
- `repeated_fast_windows_same_event >= 2`

### 5.3 快但可跟（actionable fast）

如果命中 `fast candidate`，但不满足上面的高危快交易定义，则可归类为**快但可跟**。

典型特征：

- `first_sell_lag_sec >= 180`
- `window_span_sec >= 480`
- `buy_trade_count >= 2`
- `sell_trade_count >= 2`
- `buy_max_trade_share <= 0.5`
- `sell_max_trade_share <= 0.5`

### 5.4 使用原则

> **更合理的逻辑不是“快 = 排除”，而是“快先标记，再区分成可跟的快调仓和不可跟的快交易”。**

---

## 六、v1.2 新增：可利用性 / 话题覆盖度指标

这是 v1.2 的核心补丁。

### 6.1 为什么必须新增这一层

如果你采用的是：

- 小仓位
- 多话题
- 分散式跟单

那么一个账户即便非常干净，只要它在 30 天里只给出 1–3 个可跟话题，实战价值就会显著下降。

所以，评分不能只奖励“干净”，还必须奖励：

- **可跟话题数量**
- **可跟话题的出现密度**
- **可跟话题是否过度集中**

### 6.2 话题质量分层

为了把“题材数量”纳入评分，先要把题材分层。

#### A. `clean event`
满足以下全部条件：

- 该 `eventSlug` 上存在有效 BUY
- 不属于高危快交易
- 不涉及双边买入
- 不属于多子市场结构腿事件
- 不落入硬黑名单关键词簇

这类事件可视为**可直接纳入跟单池**的题材。

#### B. `semiclean event`
满足以下条件：

- 不属于高危快交易
- 不涉及明显双边买入
- 但存在一定事件内多子市场 / 多 deadline / soft blacklist 风险

这类事件的含义不是“不能跟”，而是：

- 只能挑单腿
- 不能整题材全跟
- 需要进一步做题材级黑名单和人工过滤

#### C. `dirty event`
满足以下任一：

- 高危快交易
- 双边明显
- 结构腿明显
- 位于硬黑名单题材簇

这类事件不计入可利用性分数。

### 6.3 建议新增指标

#### 1. `clean_event_count`
分析窗口内，`clean event` 的数量。

#### 2. `semiclean_event_count`
分析窗口内，`semiclean event` 的数量。

#### 3. `deployable_event_equivalent`
定义为：

```text
deployable_event_equivalent
= clean_event_count + 0.5 * semiclean_event_count
```

解释：

- 1 个 clean 事件，按 1 个可利用话题计
- 1 个 semiclean 事件，只按 0.5 个计
- dirty 事件按 0 个计

这样做的目的是：

- 奖励真正能直接跟的 clean 题材
- 也承认“部分可跟”的 semiclean 题材有一定价值
- 但不让它们和 clean 题材等价

#### 4. `deployable_event_density`
定义为：

```text
deployable_event_density
= deployable_event_equivalent / analysis_window_days
```

推荐主窗口：30 天。

这个指标衡量的是：

- 这个账户平均每天能给出多少“可利用的跟单机会”

#### 5. `tradable_buy_ratio_v2`
定义为：

```text
tradable_buy_ratio_v2
= (clean_buy_usdc + 0.5 * semiclean_buy_usdc) / total_buy_usdc
```

这是对 v1.1 里“clean 占比”的补强版本。

#### 6. `top1_event_buy_ratio`
最大单一 `eventSlug` 的买入金额 / 总买入金额。

#### 7. `top3_event_buy_ratio`
前三大 `eventSlug` 的买入金额 / 总买入金额。

这两个指标用来防止出现：

- 账户看似可跟
- 但绝大部分机会都集中在 1–3 个话题里
- 实战上缺乏足够分散度

### 6.4 噪音过滤建议

为避免把很小的试探仓、噪音单也当成“有效话题”，建议增加：

- `deployable_event_min_buy_usd = 15`

只有当一个 `eventSlug` 在分析窗口内的总 BUY 金额 **>= 15 USDC** 时，才纳入 `clean_event_count / semiclean_event_count` 的统计。

如果你更偏保守，可以把这个门槛调到：

- `20 USDC`
- 或 “至少 2 笔 BUY，且总 BUY >= 15 USDC”

---

## 七、账户层面的完整评估指标（v1.2）

### 7.1 结构化套利相关

1. `dual_side_condition_count_ratio`
2. `dual_side_buy_usdc_ratio`
3. `dual_side_buy_usdc_ratio_1h`
4. `multi_market_event_buy_usdc_ratio`
5. `event_two_way_activity_ratio`
6. `event_multi_leg_turnover_ratio`

### 7.2 20 分钟快进快出相关

第一层（快行为总暴露）：

1. `fast_event_20m_count`
2. `fast_event_20m_buy_usdc_ratio`
3. `fast_event_20m_sell_usdc_ratio`
4. `fast_event_20m_event_ratio`

第二层（真正高危的快交易暴露）：

5. `noncopyable_fast_buy_ratio`
6. `noncopyable_fast_sell_ratio`
7. `noncopyable_fast_event_ratio`

### 7.3 复制窗口相关

1. `median_holding_time`
2. `weighted_median_holding_time`
3. `sell_usdc_ratio_within_20m`
4. `sell_usdc_ratio_within_1h`
5. `buy_sell_same_event_ratio`

### 7.4 v1.2 新增：可利用性 / 覆盖度相关

1. `clean_event_count`
2. `semiclean_event_count`
3. `deployable_event_equivalent`
4. `deployable_event_density`
5. `tradable_buy_ratio_v2`
6. `top1_event_buy_ratio`
7. `top3_event_buy_ratio`

---

## 八、v1.2 新评分标准：100 分制

v1.2 评分不再只看“干净度”，而采用：

```text
总分 = 可复制性分 + 可利用性分 + 稳定性分
```

其中：

- **可复制性分：60 分**
- **可利用性分：25 分**
- **稳定性分：15 分**

这个权重设计的含义是：

- 先保证“能跟”
- 再奖励“值得放进你的长期跟单池”

### 8.1 可复制性分（60 分）

#### A. 结构化风险（25 分）
根据以下指标综合判断：

- `dual_side_buy_usdc_ratio`
- `dual_side_buy_usdc_ratio_1h`
- `multi_market_event_buy_usdc_ratio`
- `event_two_way_activity_ratio`

经验打分建议：

- **22–25 分**：结构化风险很低，主体是单边表达
- **16–21 分**：有一定结构腿，但仍能切出较大可跟部分
- **8–15 分**：结构腿偏多，必须重度过滤后才能跟
- **0–7 分**：结构盘主导，默认不适合跟

#### B. 快交易风险（20 分）
根据以下指标综合判断：

- `noncopyable_fast_buy_ratio`
- `noncopyable_fast_sell_ratio`
- `noncopyable_fast_event_ratio`
- `sell_usdc_ratio_within_20m`
- `sell_usdc_ratio_within_1h`

经验打分建议：

- **17–20 分**：快行为很少，或快行为大多属于 actionable fast
- **11–16 分**：有明显快行为，但仍以可复制窗口为主
- **5–10 分**：高危快交易占比偏高
- **0–4 分**：分钟级执行主导，默认不适合滞后跟

#### C. 复制窗口 / 持仓质量（15 分）
根据以下指标综合判断：

- `weighted_median_holding_time`
- `sell_usdc_ratio_within_20m`
- `sell_usdc_ratio_within_1h`

经验打分建议：

- **12–15 分**：主体持仓为数小时到数天，复制窗口充足
- **8–11 分**：主体仍可复制，但一部分利润来自短线调仓
- **4–7 分**：大量利润依赖小时级以内执行
- **0–3 分**：分钟级快冲快跑占主导

### 8.2 可利用性分（25 分）

这一部分是 v1.2 新增的关键。

#### A. 可跟话题等价数（15 分）
用 `deployable_event_equivalent` 评分。

以 30 天窗口为例，建议按以下区间打分：

- **0–2**：0 分
- **3–4.9**：4 分
- **5–7.9**：7 分
- **8–11.9**：10 分
- **12–15.9**：13 分
- **>= 16**：15 分

解释：

- 如果 30 天里真正可利用的话题只有 1–2 个，实战价值明显不足
- 如果能达到 8–12 个，已经能支撑小仓多话题分散
- 如果达到 16 个以上，说明它不只是“干净”，而且“有供给能力”

#### B. 可跟话题密度（10 分）
用 `deployable_event_density` 评分。

以 30 天窗口为例：

- **< 0.10 / 天**：0 分
- **0.10 – 0.16 / 天**：2 分
- **0.17 – 0.25 / 天**：4 分
- **0.26 – 0.40 / 天**：6 分
- **0.41 – 0.60 / 天**：8 分
- **> 0.60 / 天**：10 分

直观理解：

- `< 0.10 / 天` 大约意味着 30 天里只有不到 3 个等价可跟话题
- `0.26 – 0.40 / 天` 意味着 30 天里大约有 8–12 个等价可跟话题
- `> 0.60 / 天` 意味着题材供给非常充足

### 8.3 稳定性分（15 分）

这部分不是看它“赚不赚钱”，而是看它的可利用机会是否过度集中。

#### A. 资金集中度（10 分）
主要看：

- `top1_event_buy_ratio`
- `top3_event_buy_ratio`

经验打分建议：

- **8–10 分**：买入分布相对分散，不依赖 1–2 个事件
- **5–7 分**：有一定集中，但仍可接受
- **2–4 分**：明显集中于少数题材
- **0–1 分**：高度依赖单一话题，不适合作为分散跟单源

#### B. 可保留资金占比（5 分）
用 `tradable_buy_ratio_v2` 评分。

经验打分建议：

- **4–5 分**：大部分买入都能保留下来
- **2–3 分**：只有一半上下可保留
- **0–1 分**：可保留部分很少

---

## 九、v1.2 新增：低频账户封顶规则

这是为了解决你指出的核心漏洞。

即使一个账户非常干净，只要它在考核窗口内的**可利用话题数过少**，总分也不应过高。

因此，增加以下**总分封顶条款**：

### 9.1 话题覆盖封顶

根据 `deployable_event_equivalent`：

- **< 3**：总分最高 **55 分**
- **3 – < 5**：总分最高 **62 分**
- **5 – < 8**：总分最高 **70 分**
- **>= 8**：不封顶

### 9.2 密度封顶

根据 `deployable_event_density`：

- **< 0.10 / 天**：总分最高 **55 分**
- **0.10 – < 0.17 / 天**：总分最高 **62 分**
- **0.17 – < 0.26 / 天**：总分最高 **70 分**
- **>= 0.26 / 天**：不封顶

### 9.3 集中度额外扣分

如果同时满足：

- `top1_event_buy_ratio > 50%`
- 且 `deployable_event_equivalent < 5`

则额外扣 **5 分**。

如果同时满足：

- `top3_event_buy_ratio > 80%`
- 且 `deployable_event_equivalent < 8`

则再额外扣 **5 分**。

### 9.4 这条规则的实战含义

它直接解决下面这类误判：

- 某个账户极干净
- 但 30 天里只有 1–3 个可跟话题
- 导致评分异常高
- 实际上却不足以支撑多话题分散跟单

v1.2 的结论是：

> **低频、低覆盖、低分散的账户，最多只能被视为“辅助观察源”，不能因为纯净度高就拿到主跟单池分数。**

---

## 十、kekkone 作为 60 分及格锚点

你提出的实战反馈非常重要：

> 对 kekkone 的全量跟单跑了一个多月，整体略微盈利。

这说明 kekkone 虽然并不干净，也有明显缺陷，但它至少已经达到了：

- **可复制性不算差**
- **话题供给足够**
- **整体上有一定可利用价值**

因此，v1.2 明确把：

> **“kekkone 型账户”视为 60 分附近的及格锚点。**

### 10.1 kekkone 型账户的典型画像

一般表现为：

- 双边买入不高或可控
- 高危快交易不高或可控
- 持仓周期不算短
- 但多子市场事件偏多
- 需要做黑名单和题材过滤
- 同时又能提供足够多的话题供给

### 10.2 评分校准建议

在 v1.2 下，建议按下面的口径理解分数：

- **75–100 分**：明显好于 kekkone，可进入主跟单池
- **60–74 分**：达到或略好于 kekkone，属于可跟 / 及格
- **45–59 分**：弱于 kekkone，只适合筛着跟或作为观察池
- **< 45 分**：不及格，默认不进入跟单池

### 10.3 对 aff3 一类账户的约束含义

即使某些账户在纯净度上明显优于 kekkone，但如果：

- `deployable_event_equivalent` 太低
- `deployable_event_density` 太低
- 机会集中度又太高

那么它的总分也应被压到：

- **55–62 分左右**，甚至更低

这意味着：

- 它可以是“很干净的信号源”
- 但未必是“高价值的主跟单源”

这正是 v1.2 相比 v1.1 的关键修正。

---

## 十一、账户是否值得跟：v1.2 决策标准

### 11.1 直接排除（不值得跟）

若满足以下任一，建议直接排除：

#### A. 结构化套利占比过高
- `dual_side_buy_usdc_ratio > 40%`
- `multi_market_event_buy_usdc_ratio > 60%`
- `event_two_way_activity_ratio > 50%`

#### B. 高危快交易占比过高
- `noncopyable_fast_buy_ratio > 20%`
- `noncopyable_fast_sell_ratio > 25%`
- `noncopyable_fast_event_ratio > 20%`

#### C. 短窗口双边切换明显
- `dual_side_buy_usdc_ratio_1h > 20%`
- 或存在大量 5 分钟内切两边的 `conditionId`

#### D. 明显是组合管理型账户
- 多数重点题材都表现为多腿交易
- 利润明显依赖切腿和短线调整
- 看起来更像做库存 / 做分布 / 做结构，而不是表达单边观点

### 11.2 观察池 / 只适合筛着跟

满足以下任意组合，建议只做过滤后跟单：

- `dual_side_buy_usdc_ratio` 在 **15% – 40%**
- `multi_market_event_buy_usdc_ratio` 在 **25% – 60%**
- `fast_event_20m_buy_usdc_ratio` 在 **10% – 40%**，但 `noncopyable_fast_*` 未明显爆表
- `weighted_median_holding_time` 为小时级
- `deployable_event_equivalent >= 5`
- 但 clean 题材占比不高，需要黑名单

### 11.3 相对可跟账户

建议同时满足大部分特征：

- `dual_side_buy_usdc_ratio < 15%`
- `multi_market_event_buy_usdc_ratio < 25%`
- `noncopyable_fast_buy_ratio < 10%`
- `noncopyable_fast_sell_ratio < 10%`
- 快事件存在，但大多属于 actionable fast
- 主体持有时间为数小时到数天
- `deployable_event_equivalent >= 8`
- `deployable_event_density >= 0.26 / 天`

一句话理解：

> 不只是“干净”，还要“有持续供给能力”。

---

## 十二、事件 / 关键词层面的黑名单建议

除了账户整体评分，还应继续做：

- `hard_blacklist_eventSlugs`
- `hard_blacklist_keywords`
- `soft_blacklist_keywords`

### 12.1 典型硬黑名单关键词

#### 结构腿高危关键词
- `advance to the second round`
- `runoff`
- `margin of victory`
- `who will win`
- `which countries`
- `successor`
- `supreme leader`
- `opening weekend`
- `box office`
- `between X and Y`

#### 20 分钟快进快出高危关键词
- `meeting`
- `talk to`
- `public appearance`
- `forces enter`
- `another country strike`
- `capture`
- `enter`
- `re-enter`

### 12.2 黑名单执行原则

如果某个关键词簇在历史数据里同时满足：

- 结构腿占比高
- 高危快交易占比高

则建议直接屏蔽整类题材。

---

## 十三、建议的实际筛选流程（v1.2）

### 第一步：账户级粗筛
先算：

- `dual_side_buy_usdc_ratio`
- `multi_market_event_buy_usdc_ratio`
- `noncopyable_fast_buy_ratio`
- `noncopyable_fast_sell_ratio`
- `weighted_median_holding_time`
- `deployable_event_equivalent`
- `deployable_event_density`
- `top1_event_buy_ratio`
- `top3_event_buy_ratio`

若结构化或快交易明显超线，可直接排除。

### 第二步：题材级细筛
按 `eventSlug` / 关键词分类，找出：

- 结构腿集中话题
- 高危快交易集中话题
- clean 题材
- semiclean 题材

生成：

- `hard_blacklist_eventSlugs`
- `hard_blacklist_keywords`
- `soft_blacklist_keywords`
- `clean_whitelist_eventSlugs`

### 第三步：算 v1.2 总分
先计算：

- 可复制性分
- 可利用性分
- 稳定性分

再应用：

- 低频账户封顶规则
- 高集中度额外扣分

### 第四步：放入不同池子

- **75+**：主跟单池
- **60–74**：及格 / 次主池
- **45–59**：观察池，只能筛着跟
- **< 45**：直接排除

---

## 十四、建议保留为脚本参数的字段（v1.2）

```python
SCREENING_CONFIG = {
    # fast window
    "fast_window_minutes": 20,
    "fast_min_buy_usd": 10,
    "fast_min_sell_usd": 10,
    "fast_balance_ratio_min": 0.2,
    "fast_min_trade_count": 3,
    "fast_min_condition_count": 2,

    # non-copyable fast
    "noncopyable_fast_first_sell_lag_sec": 120,
    "noncopyable_fast_window_span_sec": 300,
    "noncopyable_fast_max_trade_share": 0.6,
    "noncopyable_fast_turnover_ratio": 0.7,
    "noncopyable_fast_repeated_windows": 2,
    "noncopyable_fast_rule_hits_required": 2,

    # structure risk thresholds
    "high_risk_dual_side_buy_ratio": 0.25,
    "very_high_risk_dual_side_buy_ratio": 0.40,
    "high_risk_multi_market_event_buy_ratio": 0.35,
    "very_high_risk_multi_market_event_buy_ratio": 0.60,
    "high_risk_noncopyable_fast_buy_ratio": 0.15,
    "very_high_risk_noncopyable_fast_buy_ratio": 0.20,
    "high_risk_noncopyable_fast_sell_ratio": 0.15,
    "very_high_risk_noncopyable_fast_sell_ratio": 0.25,

    # v1.2 deployability
    "analysis_window_days": 30,
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

    # score anchor note
    "passline_anchor_account_style": "kekkone_like",
    "passline_score": 60,
}
```

---

## 十五、最终通用结论（v1.2）

判断一个 Polymarket 账户值不值得跟，核心不再只是：

- 它赚不赚钱
- 它是否干净

而是三件事同时成立：

1. **可复制**：利润主要来自你能复制的方向判断
2. **可利用**：近 30 天里有足够多的可跟话题
3. **可分散**：机会不是高度集中在极少数题材上

### 一句话理解

- **结构化套利 / 结构腿占比高** → 不适合跟
- **高危快交易占比高** → 不适合跟
- **虽然很干净，但低频、低覆盖、低分散** → 也不能高分
- **有一定缺陷，但可跟话题足够多，且整体略有正期望** → 可以达到及格线

### 最实用的决策原则

如果一个账户：

- 结构腿可控
- 高危快交易可控
- 持仓窗口尚可复制
- 并且 `deployable_event_equivalent >= 8`
- 且 `deployable_event_density >= 0.26 / 天`

那它才更像一个真正有实战价值的跟单源。

反之，哪怕它非常干净，只要：

- 30 天里只有 1–4 个可利用话题
- 大部分资金又集中在极少数事件

那它最多也只能被视为：

- **高纯度辅助信号源**
- 而不是高价值主跟单源

