# Polymarket 跟单账户筛选通用标准（结构化套利 + 20 分钟快风险双层识别 + 可利用性评分）

> 版本：v1.2.2  
> 目的：用于判断一个 Polymarket 账户是否值得跟单，重点识别五类核心问题：  
> 1. **结构化套利 / 结构化交易**  
> 2. **20 分钟内同 token 快进快出（主快风险）**  
> 3. **20 分钟内同 event 快调仓 / 切腿（辅助结构风险）**  
> 4. **低频低覆盖导致的“高分但不可利用”问题**  
> 5. **报告输出不够可执行：缺少账户级板块归纳、白名单关键词与精细化黑名单**
>
> 这是一套**实战筛选标准**，不是平台官方定义。目标不是完美还原账户策略，而是尽量过滤掉**不适合滞后跟单**的账户或题材，并把真正具有**可复制性 + 可利用性**的账户排在前面。

---

## 一、这次版本更新的核心变化（v1.2.2）

v1.1 的核心强项，是识别：

- 结构化套利 / 结构腿
- 20 分钟同话题快进快出
- 快但可跟 vs 高危快交易

v1.2 的核心补丁，是把**可利用性 / 话题覆盖度**纳入总分，避免：

- 某些账户非常干净
- 但在考核窗口内只给出极少数可跟话题
- 导致“纯净度高，但实战价值不高”的账户被误打高分

在继续使用 v1.2 的过程中，又出现了一个更细的口径问题：

> 你真正担心的，不是“同一个话题里 20 分钟内有买有卖”本身，  
> 而是**同一个 token 在 20 分钟内快速买入又卖出**，因为这会直接伤害有延迟的跟单脚本。

这个修正非常关键。

因为对滞后跟单者来说，真正决定“能不能复制”的，是：

- 目标账户是否在**同一个 token** 上快速 round-trip
- 也就是你刚看到它买，它很快就卖了
- 导致你跟进去时，最好的复制窗口已经消失

相反，如果只是：

- 同一个 `eventSlug` 下买入 token A
- 同时卖出 token B

那么这更像是：

- 事件内调仓
- deadline 切换
- 组合腿轮动
- 结构管理

它确实说明账户更复杂，但**不一定直接等于你跟不上新买入的 token**。

因此，v1.2.1 做了一个重要升级：

1. **保留你提出的修正**：把“同 token 20 分钟内买入又卖出”设为**主快风险规则**
2. **保留 v1.1 / v1.2 原来的视角**：把“同 event 20 分钟内跨 token 买卖”降级为**辅助结构风险规则**
3. 评分、阈值、决策逻辑全部按这套“双层快风险”口径同步调整
4. 新增**账户画像输出规范**：分析报告除了分数与结论，还必须输出
   - `所属板块`
   - `白名单关键词`
   - `账户级硬黑名单关键词`
   - `账户级软黑名单关键词`
5. 取消“全局硬黑名单”作为主文档中的强约束，改为：
   - 仅保留通用高危关键词簇作为**候选风险词库**
   - 真正执行时，必须落到**账户级 hard/soft blacklist**

一句话概括：

> **v1.2.1 的快交易判断，不再只问“这个话题里有没有快买快卖”，  
> 而是优先问“这个 token 本身是否快进快出”，再辅以“这个事件里是否存在快调仓 / 切腿”。**

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

## 五、20 分钟快风险：主规则、辅规则与分层识别

v1.2.1 对“快交易”采用**双层定义**：

- **主规则：同 token 快进快出**
  - 用来识别真正会伤害滞后跟单复制窗口的行为
  - 这是快交易风险的主指标
- **辅规则：同 event 快调仓 / 切腿**
  - 用来识别事件内部的轮动、切腿、deadline 切换和组合管理
  - 它更接近结构化风险的辅助指标，而不是快交易的一票否决指标

### 5.1 主规则：同 token 候选快交易（token fast candidate）

#### 定义

以 **`token_id`** 作为优先键。  
如果原始 CSV 没有 `token_id`，则用：

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
   - 存在至少 2 笔 BUY 或至少 2 笔 SELL

则记为一次 **`token_fast_candidate`**。

#### 为什么把它设为主规则

因为它直接对应你最关心的复制风险：

- 目标账户在某个 token 上快速建仓
- 很快又在同一个 token 上卖出
- 你的脚本由于延迟，可能刚跟进去，就已经接近它的卖点，甚至已经错过卖点

因此：

> **“同 token 快进快出”是对滞后跟单最直接、最可执行的高危快交易定义。**

### 5.2 主规则的二次判定：高危快交易（non-copyable token fast）

对命中的 `token_fast_candidate`，继续计算：

- `first_sell_lag_sec`
- `window_span_sec`
- `buy_trade_count`
- `sell_trade_count`
- `buy_max_trade_share`
- `sell_max_trade_share`
- `token_fast_turnover_ratio`
  - 窗口内 `(BUY+SELL)` / 该 `token_key` 全周期 `(BUY+SELL)`
- `repeated_fast_windows_same_token`

满足候选快交易后，若再满足以下条件中的至少 2 条，建议归为**高危快交易**：

- `first_sell_lag_sec < 120`
- `window_span_sec < 300`
- `buy_trade_count < 2` 或 `sell_trade_count < 2`
- `buy_max_trade_share > 0.6` 或 `sell_max_trade_share > 0.6`
- `token_fast_turnover_ratio > 0.7`
- `repeated_fast_windows_same_token >= 2`

这类交易通常意味着：

- 真正可反应的时间太短
- 买卖主要被少数大单主导
- 利润更依赖先手和执行速度，而不是你能滞后复制的再定价

### 5.3 主规则下的“快但可跟”（actionable token fast）

如果命中 `token_fast_candidate`，但不满足上面的高危快交易定义，则可归类为**快但可跟**。

典型特征：

- `first_sell_lag_sec >= 180`
- `window_span_sec >= 480`
- `buy_trade_count >= 2`
- `sell_trade_count >= 2`
- `buy_max_trade_share <= 0.5`
- `sell_max_trade_share <= 0.5`

这类行为说明：

- 账户在这个 token 上确实做了较快调仓
- 但复制窗口仍然存在
- 更像“可复制的快节奏减仓 / 止盈”，而非纯速度型快冲快跑

### 5.4 辅规则：同 event 快调仓 / 切腿（event rebalance candidate）

在同一个 `eventSlug` 的任意 20 分钟滚动窗口中，若同时满足：

1. 同窗内同时出现 BUY 和 SELL
2. `BUY usdcSize >= 10`
3. `SELL usdcSize >= 10`
4. `min(BUY, SELL) / max(BUY, SELL) >= 0.2`
5. 且再满足至少一条：
   - 成交笔数 `>= 3`
   - 涉及 `>= 2` 个不同 `conditionId`
   - `BUY + SELL >= 50`

则记为一次 **`event_rebalance_candidate`**。

#### 这个指标的意义

它不再直接回答：

- “这个 token 能不能跟得上”

而是更偏向回答：

- “这个账户是否在同一事件里快速调仓”
- “是否存在 deadline 切换 / 组合腿轮动 / 事件内再平衡”
- “它的利润里是否有一部分依赖结构管理，而不是单腿观点”

因此它应该主要用于：

- 结构化风险加分项
- semiclean / dirty 事件分类
- 关键词黑名单和事件黑名单生成

而**不建议单独作为快交易主风险的一票否决指标**。

### 5.5 使用原则

v1.2.1 对快交易的推荐用法是：

1. **先用 `token_fast_candidate` 发现真正影响复制窗口的快交易**
2. **再用二次判定识别 `non-copyable token fast`**
3. **同时用 `event_rebalance_candidate` 发现事件内快调仓 / 切腿**
4. 账户准入优先看：
   - `noncopyable_token_fast_buy_ratio`
   - `noncopyable_token_fast_sell_ratio`
   - `noncopyable_token_fast_token_ratio`
5. 题材黑名单和 semiclean/dirty 分类，再结合看：
   - `event_rebalance_buy_ratio`
   - `event_rebalance_sell_ratio`
   - `event_rebalance_event_ratio`

一句话概括：

> **主规则看“你会不会在同一个 token 上跟不及”，  
> 辅规则看“这个账户有没有在同一事件里做快调仓 / 切腿”。**

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

### 7.2 20 分钟快风险相关

第一层（真正影响复制窗口的主快风险）：

1. `token_fast_20m_count`
2. `token_fast_20m_buy_usdc_ratio`
3. `token_fast_20m_sell_usdc_ratio`
4. `token_fast_20m_token_ratio`

第二层（真正高危的 token 快交易暴露）：

5. `noncopyable_token_fast_buy_ratio`
6. `noncopyable_token_fast_sell_ratio`
7. `noncopyable_token_fast_token_ratio`

第三层（事件内快调仓 / 切腿的辅助结构风险）：

8. `event_rebalance_20m_count`
9. `event_rebalance_buy_ratio`
10. `event_rebalance_sell_ratio`
11. `event_rebalance_event_ratio`

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

## 八、v1.2.1 新评分标准：100 分制

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

- `noncopyable_token_fast_buy_ratio`
- `noncopyable_token_fast_sell_ratio`
- `noncopyable_token_fast_token_ratio`
- `sell_usdc_ratio_within_20m`
- `sell_usdc_ratio_within_1h`

并辅以观察：

- `event_rebalance_buy_ratio`
- `event_rebalance_event_ratio`

经验打分建议：

- **17–20 分**：同 token 高危快交易很少，复制窗口通常充足；即便存在 event 级快调仓，也主要是辅助风险
- **11–16 分**：有一定同 token 快交易，但整体仍可复制；event 级快调仓存在但不主导
- **5–10 分**：同 token 高危快交易占比偏高，或同 event 快调仓非常频繁并与结构化风险叠加
- **0–4 分**：分钟级执行或事件内高速轮动主导，默认不适合滞后跟

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

## 十一、账户是否值得跟：v1.2.1 决策标准

### 11.1 直接排除（不值得跟）

若满足以下任一，建议直接排除：

#### A. 结构化套利占比过高
- `dual_side_buy_usdc_ratio > 40%`
- `multi_market_event_buy_usdc_ratio > 60%`
- `event_two_way_activity_ratio > 50%`

#### B. 同 token 高危快交易占比过高
- `noncopyable_token_fast_buy_ratio > 20%`
- `noncopyable_token_fast_sell_ratio > 25%`
- `noncopyable_token_fast_token_ratio > 20%`

#### C. 短窗口双边切换明显
- `dual_side_buy_usdc_ratio_1h > 20%`
- 或存在大量 5 分钟内切两边的 `conditionId`

#### D. event 级快调仓非常重，并与结构化风险叠加
例如同时满足：
- `event_rebalance_buy_ratio` 很高
- 且 `multi_market_event_buy_usdc_ratio` 很高
- 且重点题材都表现为多腿交易 / deadline 切换 / 事件内轮动

这类账户即便不一定在单一 token 上快进快出，也往往更像组合管理型账户，而不是可直接复制的观点账户。

### 11.2 观察池 / 只适合筛着跟

满足以下任意组合，建议只做过滤后跟单：

- `dual_side_buy_usdc_ratio` 在 **15% – 40%**
- `multi_market_event_buy_usdc_ratio` 在 **25% – 60%**
- `noncopyable_token_fast_buy_ratio` 在 **10% – 20%**，但未明显爆表
- `event_rebalance_buy_ratio` 不低，说明事件内调仓较多
- `weighted_median_holding_time` 为小时级
- `deployable_event_equivalent >= 5`
- 但 clean 题材占比不高，需要黑名单

### 11.3 相对可跟账户

建议同时满足大部分特征：

- `dual_side_buy_usdc_ratio < 15%`
- `multi_market_event_buy_usdc_ratio < 25%`
- `noncopyable_token_fast_buy_ratio < 10%`
- `noncopyable_token_fast_sell_ratio < 10%`
- event 级快调仓存在，但不主导整体行为
- 主体持有时间为数小时到数天
- `deployable_event_equivalent >= 8`
- `deployable_event_density >= 0.26 / 天`

一句话理解：

> 不只是“干净”，还要“有持续供给能力”，并且在**同 token 层面**有足够可复制的跟单窗口。

---

## 十二、账户级关键词画像：板块、白名单与精细化黑名单（v1.2.2）

除了账户整体评分，v1.2.2 要求分析输出进一步落到**账户级可执行画像**。

也就是说，报告不应只回答：

- 这个号能不能跟
- 分数是多少

还必须回答：

- 这个号**主要擅长什么板块**
- 哪些词簇 / 题材 **更值得保留**
- 哪些题材必须进入 **账户级硬黑名单**
- 哪些题材只适合进入 **账户级软黑名单**

### 12.1 不再设置“全局硬黑名单”

v1.2.2 明确取消主文档中的**全局硬黑名单**。

原因是：

- 同一个关键词，在不同账户里的行为质量可能差异很大
- 例如 `capture`、`enter`、`ceasefire` 这类词，在某些账户里可能高度结构化
- 但在另一些账户里，只要是单地点、单 deadline、单腿表达，也可能属于可跟部分

因此更合理的做法是：

- 保留“高危关键词簇”作为**候选风险词库**
- 但是否进入真正执行层的 blacklist，必须根据**该账户历史数据**决定

一句话概括：

> **v1.2.2 不主张全局一刀切封杀关键词，而主张账户级精细化 hard / soft blacklist。**

### 12.2 所属板块（sector / board）

#### 定义
`所属板块` 是对一个账户**主要交易能力圈**的概括，目的不是描述它碰过什么，而是描述：

- 它的买入资金主要集中在哪类题材
- 其中哪些题材在清洗后仍保留较多 clean / semiclean 机会
- 它更像哪一类“专长交易者”

#### 常见板块示例

- 地缘战争 / 军事升级
- 俄乌前线推进 / ceasefire / capture / enter
- 伊朗局势 / regime / strike / Hormuz / supreme leader
- 美国政治 / 选举 / 候选人 / 政策
- 体育 winner / championship / 晋级
- 娱乐票房 / opening weekend / highest grossing movie
- 宏观 / 利率 / 美联储 / CPI / recession
- 加密 / BTC 区间 / ETF / 监管

#### 归纳原则

一个账户的所属板块，建议最多总结 **1–3 个**，按以下逻辑筛选：

1. 买入金额占比高
2. clean + semiclean 保留金额占比不低
3. 不是只出现过一次的偶发题材
4. 能够反映该账户在实战里真正可利用的优势区间

### 12.3 白名单关键词（whitelist keywords）

#### 定义
`白名单关键词` 不是指“这个词出现就一定跟”，而是：

- 在该账户历史里，出现这个词簇的题材
- 更容易落入 clean / semiclean
- 更能代表该账户相对可复制、相对有优势的部分

#### 生成原则

建议同时满足以下条件中的多数：

- 对应题材簇的 clean / semiclean 占比较高
- 该题材簇不以双边切换为主
- 不以多子市场组合腿为主
- 不以高危同 token 快 round-trip 为主
- 出现频率或买入金额达到一定规模，不是噪音样本

#### 输出形式

对白名单关键词，建议分两层输出：

1. **板块层白名单**
   - 例如：`ceasefire`、`regime fall`、`Fed no change`
2. **精确事件层白名单**（可选）
   - 例如：`Russia x Ukraine ceasefire by April 30, 2026`
   - 用于样本较小但质量很高的账户

### 12.4 账户级硬黑名单关键词（hard blacklist keywords）

#### 定义
某个关键词簇若在该账户历史里，**稳定地对应不可复制或高度结构化行为**，则应进入该账户的硬黑名单。

#### 建议纳入 hard blacklist 的情形

满足以下任一类即可考虑纳入：

1. **结构腿显著**
   - 该词簇下大量事件落在多 outcome / 多子市场组合中
   - 对应 `multi_market_event_buy_usdc_ratio` 明显偏高

2. **双边切换显著**
   - 该词簇下频繁出现同一 `conditionId` 双边买入
   - 或短窗口双边切换明显

3. **高危快交易显著**
   - 该词簇下 `noncopyable_token_fast` 占比高
   - 或 event 级快调仓与结构风险显著叠加

4. **同类题材几乎没有可保留部分**
   - clean / semiclean 占比极低
   - 即便偶有干净事件，也不足以覆盖执行成本

#### 常见 hard blacklist 候选词簇

这些词簇不再是“全局硬黑名单”，而是**候选风险词库**：

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
- `meeting`
- `talk to`
- `public appearance`
- `forces enter`
- `another country strike`
- `capture`
- `enter`
- `re-enter`

只有当这些词在**目标账户自身历史里**表现为高度脏、结构化或不可复制时，才升级为该账户的 hard blacklist。

### 12.5 账户级软黑名单关键词（soft blacklist keywords）

#### 定义
某个关键词簇若并非绝对不能跟，但：

- 内部质量差异大
- 需要挑单腿
- 需要限制仓位
- 需要结合 eventSlug / 子市场进一步过滤

则应进入 soft blacklist。

#### 典型情形

- 同一个关键词簇里既有 clean 事件，也有大量 semiclean / dirty 事件
- 多 deadline 很常见，但单腿仍有部分可跟价值
- 账户在该词簇下并非一直结构化，只是稳定性较差

#### 执行建议

soft blacklist 的含义通常是：

- 默认跳过
- 仅在满足附加条件时保留

常见附加条件包括：

- 只保留单 deadline
- 只保留单地点 / 单国家 / 单方向
- 只保留 clean 单腿
- 只保留无双边、无多子市场、无 token fast 的事件

### 12.6 账户级关键词画像的标准输出格式

对每个目标账户，分析报告建议至少输出以下结构：

```text
账户：0x...
评分：XX / 100
结论：主池 / 补充池 / 观察池 / 排除

所属板块：
- 板块 A
- 板块 B

白名单关键词：
- keyword 1
- keyword 2

账户级硬黑名单：
- hard keyword 1
- hard keyword 2

账户级软黑名单：
- soft keyword 1
- soft keyword 2
```

### 12.7 黑名单与白名单的生成顺序

推荐顺序是：

1. 先做账户级粗筛，判断是否总体可跟
2. 再按 `eventSlug` / 关键词簇统计 clean / semiclean / dirty 分布
3. 先总结**所属板块**
4. 再总结**白名单关键词**
5. 再生成**账户级硬黑名单**
6. 最后把“介于中间”的题材归入**账户级软黑名单**

这样做的好处是：

- 先找到“这个号真正擅长什么”
- 再排除它明显不适合跟的部分
- 最终得到的是可执行的“保留什么 / 跳过什么”画像，而不是只有负面过滤器

---

## 十三、建议的实际筛选流程（v1.2.2）

### 第一步：账户级粗筛
先算：

- `dual_side_buy_usdc_ratio`
- `multi_market_event_buy_usdc_ratio`
- `noncopyable_token_fast_buy_ratio`
- `noncopyable_token_fast_sell_ratio`
- `event_rebalance_buy_ratio`
- `weighted_median_holding_time`
- `deployable_event_equivalent`
- `deployable_event_density`
- `top1_event_buy_ratio`
- `top3_event_buy_ratio`

若结构化、同 token 快交易或 event 级快调仓叠加明显超线，可直接排除。

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

## 十四、建议保留为脚本参数的字段（v1.2.2）

除核心筛选参数外，v1.2.2 建议把以下“账户画像输出”参数也保留为可配置项：

- `max_sector_count = 3`
- `max_whitelist_keyword_count = 8`
- `max_hard_blacklist_keyword_count = 12`
- `max_soft_blacklist_keyword_count = 12`
- `sector_min_buy_ratio_hint = 0.10`
- `keyword_min_buy_usd_hint = 15`
- `keyword_min_event_count_hint = 2`
- `prefer_account_level_blacklist_over_global = True`

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

    # structure risk thresholds
    "high_risk_dual_side_buy_ratio": 0.25,
    "very_high_risk_dual_side_buy_ratio": 0.40,
    "high_risk_multi_market_event_buy_ratio": 0.35,
    "very_high_risk_multi_market_event_buy_ratio": 0.60,
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

## 十五、最终通用结论（v1.2.2）

判断一个 Polymarket 账户值不值得跟，核心不再只是：

- 它赚不赚钱
- 它是否干净

而是三件事同时成立：

1. **可复制**：利润主要来自你能复制的方向判断
2. **可利用**：近 30 天里有足够多的可跟话题
3. **可分散**：机会不是高度集中在极少数题材上

### 一句话理解

- **结构化套利 / 结构腿占比高** → 不适合跟
- **同 token 高危快交易占比高** → 不适合跟
- **event 级快调仓 / 切腿很重，并与结构风险叠加** → 也不适合跟
- **虽然很干净，但低频、低覆盖、低分散** → 也不能高分
- **有一定缺陷，但可跟话题足够多，且整体略有正期望** → 可以达到及格线

### 最实用的决策原则

如果一个账户：

- 结构腿可控
- 同 token 高危快交易可控
- 持仓窗口尚可复制
- 并且 `deployable_event_equivalent >= 8`
- 且 `deployable_event_density >= 0.26 / 天`

并且 event 级快调仓没有重到表明其主体利润来自组合管理，
那它才更像一个真正有实战价值的跟单源。

反之，哪怕它非常干净，只要：

- 30 天里只有 1–4 个可利用话题
- 大部分资金又集中在极少数事件

那它最多也只能被视为：

- **高纯度辅助信号源**
- 而不是高价值主跟单源

