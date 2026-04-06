# Polymarket 跟单账户筛选通用标准（结构化套利 + 20分钟快进快出）

> 版本：v1.0  
> 目的：用于判断一个 Polymarket 账户是否值得跟单，重点识别两类高危行为：
> 1. **结构化套利 / 结构化交易**
> 2. **20 分钟内同话题快进快出**
>
> 这是一套**实战筛选标准**，不是平台官方定义。目标不是完美还原账户策略，而是尽量过滤掉**不适合滞后跟单**的账户或题材。

---

## 一、适用前提

本标准适用于基于 Polymarket 公开交易数据（如 `activity` / `trades` 导出的 CSV）对账户进行行为分析。

推荐最少分析窗口：

- **近 30 天**：判断近期行为风格
- **近 7 天**：观察最近是否风格突变

推荐基础字段：

- `timestamp`
- `eventSlug`
- `conditionId`
- `title`
- `side`（BUY / SELL）
- `outcome`（Yes / No 或候选人/区间等 outcome）
- `price`
- `size`
- `usdcSize`
- `transactionHash`

---

## 二、核心判断目标

判断一个账户是否值得跟单，不是看它是否盈利，而是看它的盈利是否主要来自**你能复制的行为**。

### 适合跟单的典型特征

- 以**单边方向交易**为主
- 买入后通常会持有**较长时间**，而不是反复来回切
- 同一事件下很少同时做多条互斥腿
- 很少出现同一话题短时间内又买又卖
- 账户的主要利润不是靠高频执行、盘口细微波动或组合切腿

### 不适合跟单的典型特征

- 频繁出现 **YES / NO 同时买**
- 频繁在**同一事件多个子市场同时建仓**
- 经常在同一话题内**短时间又买又卖**
- 利润明显依赖**组合管理、切腿顺序、执行速度**
- 大量交易是**分钟级 / 小时级快进快出**

---

## 三、结构化套利 / 结构化交易：定义与识别标准

这里的“结构化套利”不局限于严格无风险套利，也包括所有对跟单者不友好的**结构化组合交易**。

### 3.1 一级定义：同一 market 双边买入

#### 定义
在同一个 `conditionId` 上，账户曾经都买过两个相反 outcome。

常见形式：

- 同一 `conditionId` 上买过 `Yes` 和 `No`
- 同一候选人 / 区间 market 上，两边都碰过

#### 判断意义
这通常说明账户不是在表达单边观点，而是在：

- 对冲
- 反手
- 盘口微结构交易
- 结构调整
- 做库存管理

#### 建议计算指标

- `dual_side_condition_count_ratio`  
  = 出现双边买入的 `conditionId` 数量 / 有买入的 `conditionId` 总数

- `dual_side_buy_usdc_ratio`  
  = 出现双边买入的 `conditionId` 上的买入金额 / 总买入金额

#### 高危阈值

- **低风险**：< 10%
- **中风险**：10% – 25%
- **高风险**：25% – 40%
- **极高风险**：> 40%

#### 强化条件
如果同一 `conditionId` 上的双边买入发生在**短窗口内**，风险进一步升级：

- 5 分钟内切两边：极危险
- 1 小时内切两边：高危险
- 24 小时内切两边：中危险

可增加指标：

- `dual_side_buy_usdc_ratio_5m`
- `dual_side_buy_usdc_ratio_1h`
- `dual_side_buy_usdc_ratio_24h`

---

### 3.2 二级定义：同一事件多个子市场同时建仓

#### 定义
在同一个 `eventSlug` 下，账户同时买入多个不同 `conditionId`，且这些子市场是**互斥或高度相关**的。

典型场景：

1. **票房盘 / 区间盘**
   - 同时买多个 box office 区间的 Yes
   - 同时买多个 opening weekend 区间的 Yes

2. **候选人盘 / 谁会赢盘**
   - 同时买多个候选人/球队/结果对应的 outcome

3. **晋级 / 排名 / 多结果事件**
   - 同一事件下多 outcome 一起建仓

4. **Neg-risk / 多结果市场的组合腿**
   - 通过多个 outcome 组合表达同一个宏观观点

#### 判断意义
这类交易常常不是在赌“单一结果”，而是在交易：

- 概率分布
- 区间带
- 相对定价
- 事件内结构
- 组合再平衡

对跟单者的风险是：

- 你看到的是单腿，原账户赚的是整组腿
- 你很难知道其**完整组合成本**
- 更难复制其**卖出顺序**和**调仓节奏**

#### 建议计算指标

定义：

- `event_multi_market_yes_count`  
  某个事件中买入了多少个不同 `conditionId` 的 `Yes`

- `event_multi_market_outcome_count`  
  某个事件中买入了多少个不同 outcome

- `multi_market_event_buy_usdc_ratio`  
  发生“同一事件多子市场建仓”的买入金额 / 总买入金额

#### 判定建议
可视为“结构化事件”的情形：

- 同一 `eventSlug` 下，买入 **≥ 2 个不同子市场**
- 且这些子市场属于：
  - 多区间盘
  - 多候选人盘
  - 多结果盘
  - margin / runoff / 晋级 / winner 类

#### 高危阈值

- **低风险**：< 15%
- **中风险**：15% – 35%
- **高风险**：35% – 60%
- **极高风险**：> 60%

---

### 3.3 三级定义：事件内频繁调仓 / 切腿

#### 定义
在同一 `eventSlug` 内，账户持续买入和卖出多个相关 `conditionId`，表现出明显的组合管理行为。

典型表现：

- 先买多个区间 Yes，再择机卖出其中几个
- 同一事件里既买某 outcome，又买另一个相关 outcome
- 同一事件内在不同子市场之间轮动
- 同一事件内多次加仓、减仓、切换方向

#### 判断意义
这类账户的优势往往来自：

- 结构搭建
- 动态再平衡
- 卖出顺序
- 分布变化的捕捉

这类利润很难由滞后跟单复刻。

#### 建议计算指标

- `event_two_way_activity_ratio`  
  出现“同一事件内同时有买和卖”的事件，对应交易金额占比

- `event_multi_leg_turnover_ratio`  
  同一事件内涉及多个 `conditionId` 且买卖都活跃的交易金额占比

- `avg_condition_count_per_event_when_active`  
  对活跃事件，平均每个事件涉及多少个 `conditionId`

#### 高危经验判断
如果一个账户在大量事件里都表现出：

- 同事件多腿建仓
- 同事件短期内又买又卖
- 同事件多条件轮动

则应视为**结构化账户**，默认不适合直接跟单。

---

### 3.4 四级定义：其他典型结构化高危行为

以下行为即使不一定落入上面三个定义，也建议视为结构化高危：

#### A. 候选人篮子 / 国家篮子 / 谁会发生盘
例如：

- `Which countries will ...`
- `Who will ...`
- `Who will advance ...`
- `Who will win mayoral election`

风险原因：

- 账户可能是在交易“篮子分布”，不是单腿观点
- 同题材天然容易多 outcome 同时建仓

#### B. Margin / runoff / second round / advance 类盘
例如：

- `margin of victory`
- `runoff`
- `advance to second round`

风险原因：

- 常伴随多腿对冲与结构切换
- outcome 之间高度耦合

#### C. Box office / opening weekend / 区间盘
例如：

- `opening weekend box office`
- `between X and Y`
- `< X`
- `> X`

风险原因：

- 典型区间分布交易
- 同事件多区间 Yes 很常见

#### D. Neg-risk / 多结果映射结构
例如：

- 多结果体育 winner / draw / moneyline
- 某 outcome 的 No 对应其他 outcome 的 Yes 组合

风险原因：

- 原账户可能在交易映射关系
- 跟单者只能看到残缺腿

---

## 四、20 分钟快进快出：定义与识别标准

### 4.1 正式定义（推荐采用）

> **20 分钟快进快出 = 在同一个 `eventSlug` 内，任意 20 分钟滚动窗口中，同时出现 BUY 和 SELL，且不是轻微抖动。**

这是一个**话题级**定义，不是单腿级定义。

### 4.2 推荐过滤口径

对每个 `eventSlug`，做滚动 20 分钟窗口，满足以下条件则记为一次“20 分钟快进快出事件”：

1. 窗口内同时出现 **BUY 和 SELL**
2. 窗口内：
   - `BUY usdcSize >= 10`
   - `SELL usdcSize >= 10`
3. 为排除轻微抖动：
   - `min(BUY, SELL) / max(BUY, SELL) >= 0.2`

### 4.3 可选加强条件（推荐）

为了进一步排掉偶发的小减仓/试单，建议增加至少一条：

- 窗口内成交笔数 `>= 3`
- 或窗口内涉及 `>= 2` 个不同 `conditionId`
- 或窗口内总成交额 `BUY + SELL >= 50`

### 4.4 为什么不用“同腿 20 分钟平仓”替代

单纯按 `conditionId + outcome` 去配对买卖，会把一些正常行为也算进去，例如：

- 分批止盈
- 正常减仓
- 拆单成交
- 老仓的一部分被卖出

而你真正想排除的是：

- **同一话题里短时间来回倒仓**
- **同一事件里快速调仓**
- **需要高频反应才能跟上的行为**

所以更推荐使用**话题级 20 分钟买卖同窗**定义。

---

## 五、账户层面的通用评估指标

建议至少计算以下指标。

### 5.1 结构化套利相关

1. `dual_side_condition_count_ratio`
2. `dual_side_buy_usdc_ratio`
3. `dual_side_buy_usdc_ratio_1h`
4. `multi_market_event_buy_usdc_ratio`
5. `event_two_way_activity_ratio`
6. `event_multi_leg_turnover_ratio`

### 5.2 20 分钟快进快出相关

1. `fast_event_20m_count`
2. `fast_event_20m_buy_usdc_ratio`
3. `fast_event_20m_sell_usdc_ratio`
4. `fast_event_20m_event_ratio`
   - = 命中 20 分钟快进快出的 `eventSlug` 数量 / 总 `eventSlug` 数量

### 5.3 辅助指标（建议一起看）

1. `median_holding_time`
2. `weighted_median_holding_time`
3. `sell_usdc_ratio_within_20m`（可选，单腿级持有时长）
4. `sell_usdc_ratio_within_1h`
5. `buy_sell_same_event_ratio`

---

## 六、账户是否值得跟：通用决策标准

下面给出一套实战用的分层标准。

### 6.1 直接排除（不值得跟）

若满足以下任一情况，建议直接排除：

#### A. 结构化套利占比过高
满足任一：

- `dual_side_buy_usdc_ratio > 40%`
- `multi_market_event_buy_usdc_ratio > 60%`
- `event_two_way_activity_ratio > 50%`

#### B. 20 分钟快进快出占比过高
满足任一：

- `fast_event_20m_buy_usdc_ratio > 30%`
- `fast_event_20m_sell_usdc_ratio > 35%`
- `fast_event_20m_event_ratio > 30%`

#### C. 短窗口双边切换明显
满足任一：

- `dual_side_buy_usdc_ratio_1h > 20%`
- 存在大量 `conditionId` 在 5 分钟内切两边

#### D. 明显是组合管理型账户
例如：

- 多数重点题材都表现为多腿交易
- 利润明显依赖切腿和短线调整
- 看起来更像做库存/做分布/做结构，而不是表达单边观点

### 6.2 可疑账户（只适合筛着跟）
若满足以下任意组合，建议只做过滤后跟单：

- `dual_side_buy_usdc_ratio` 在 **15% – 40%** 之间
- `multi_market_event_buy_usdc_ratio` 在 **25% – 60%** 之间
- `fast_event_20m_buy_usdc_ratio` 在 **10% – 30%** 之间
- `fast_event_20m_sell_usdc_ratio` 在 **10% – 35%** 之间
- `weighted_median_holding_time` 为**小时级**，但短线利润占比不小

此类账户的使用方式：

- 不能全量跟
- 必须做题材黑名单
- 必须跳过结构化事件
- 必须跳过 20 分钟同话题买卖活跃的事件

### 6.3 相对可跟账户
满足以下大部分特征，可认为相对适合跟：

- `dual_side_buy_usdc_ratio < 15%`
- `multi_market_event_buy_usdc_ratio < 25%`
- `fast_event_20m_buy_usdc_ratio < 10%`
- `fast_event_20m_sell_usdc_ratio < 10%`
- 短时间双边切换很少
- 持有时间以**数小时到数天**为主
- 主体行为是正常买入后等待再定价，再卖出获利/止损

这类账户依然不等于可以无脑跟，但至少**主体行为是可复制的**。

---

## 七、事件 / 关键词层面的黑名单建议

除了看账户整体比例，还应做**话题级黑名单**。

### 7.1 典型高危关键词

建议优先警惕以下类型：

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

### 7.2 黑名单执行原则

如果某个关键词簇在历史数据里同时满足：

- 结构腿占比高
- 20 分钟同话题买卖占比高

则建议直接屏蔽整类题材。

---

## 八、建议的实际筛选流程

### 第一步：账户级粗筛
先算账户整体指标：

- `dual_side_buy_usdc_ratio`
- `multi_market_event_buy_usdc_ratio`
- `fast_event_20m_buy_usdc_ratio`
- `fast_event_20m_sell_usdc_ratio`
- `weighted_median_holding_time`

若明显超阈值，直接排除。

### 第二步：话题级细筛
对账户按 `eventSlug` / 关键词分类，找出：

- 结构腿集中话题
- 20 分钟同话题买卖集中话题

生成：

- `hard_blacklist_eventSlugs`
- `hard_blacklist_keywords`
- `soft_blacklist_keywords`

### 第三步：保留相对干净的部分
只保留：

- 单边方向为主的话题
- 很少短时间买卖来回切的话题
- 持仓周期更长的话题

---

## 九、最终通用结论

判断一个 Polymarket 账户值不值得跟，核心不是看它赚不赚钱，而是看它的盈利是不是主要来自：

- **你能复制的方向判断**
- 还是来自**你复制不了的结构管理和短线执行**

### 直接理解为一句话

- **结构化套利 / 结构化交易占比高** → 不适合跟
- **20 分钟同话题快进快出占比高** → 不适合跟
- **两者都低，主体是正常持仓再卖出** → 相对可跟

### 最实用的决策原则

如果一个账户：

- 结构腿买入金额占比 **> 25%**，并且
- 20 分钟同话题买卖金额占比 **> 15%**

那就应高度警惕；
如果再叠加：

- 同一 `conditionId` 双边切换明显
- 多子市场事件建仓比例很高

则应视为**不值得跟的账户**。

---

## 十、建议保留为脚本参数的字段

```python
SCREENING_CONFIG = {
    "fast_window_minutes": 20,
    "fast_min_buy_usd": 10,
    "fast_min_sell_usd": 10,
    "fast_balance_ratio_min": 0.2,
    "fast_min_trade_count": 3,
    "fast_min_condition_count": 2,

    "high_risk_dual_side_buy_ratio": 0.25,
    "very_high_risk_dual_side_buy_ratio": 0.40,

    "high_risk_multi_market_event_buy_ratio": 0.35,
    "very_high_risk_multi_market_event_buy_ratio": 0.60,

    "high_risk_fast_event_buy_ratio": 0.15,
    "very_high_risk_fast_event_buy_ratio": 0.30,

    "high_risk_fast_event_sell_ratio": 0.15,
    "very_high_risk_fast_event_sell_ratio": 0.35,
}
```

---

## 十一、使用建议

这套标准建议作为：

1. **账户准入筛选器**：先判断一个号整体值不值得跟
2. **题材黑名单筛选器**：即便账户整体可跟，也屏蔽高危题材
3. **动态复审器**：每周或每 30 天重新计算一次，防止风格切换

---

