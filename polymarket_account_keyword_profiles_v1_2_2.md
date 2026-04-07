# Polymarket 各账号关键词画像与账户级黑白名单（v1.2.2）

这版在 `polymarket_account_blacklist_keywords_v1_2_1.md` 的基础上做了两点调整：

1. **取消全局硬黑名单**，不再预设统一的全局 hard blacklist；
2. 每个目标账户除了 **账户级硬黑名单 / 账户级软黑名单** 外，新增：
   - **所属板块**：这个账号主要擅长、主要活跃、主要盈利来源集中的题材簇；
   - **白名单关键词**：在该账号内部，相对更值得优先保留、优先观察、优先放行的关键词簇。

使用原则：
- **所属板块** 是“这个账号主要在做什么”，不等于“这些都适合跟”；
- **白名单关键词** 是“该账号里相对更干净、更可复制、更有利用价值的部分”；
- **账户级硬黑名单** 是建议直接屏蔽的内容；
- **账户级软黑名单** 是默认跳过、仅在额外确认后才放行的内容。

---

## 1. Optimus.

- 地址：`0xd5b97d08ec6098407bfbf66c2786ccc9967fe44e`
- 分层：`main`
- 评分：**71**

### 所属板块
- IPO / 上市进度
- 公司估值 / market cap
- 政治职位变动 / office change
- 司法 / 政策进展
- 简单地缘二元事件

### 白名单关键词
- `IPO`
- `market cap`
- `office change`
- `judicial`
- `policy`
- `ceasefire`
- `simple binary geopolitical`

### 账户级硬黑名单
- 无

### 账户级软黑名单
- `us forces enter`
- `forces enter`

### 说明
主池。整体最稳，双边买入、同 token 快 round-trip、同 event 快调仓都几乎为零。真正需要过滤的，主要是 `forces enter` 这类同题材多 deadline / 多腿倾向事件簇。

---

## 2. aff3

- 地址：`0xe52c0a1327a12edc7bd54ea6f37ce00a4ca96924`
- 分层：`supplemental`
- 评分：**61**

### 所属板块
- 伊朗政局 / regime change
- 伊朗相关冲突终局
- 中东地缘简单双边事件
- 少量简单赢家盘

### 白名单关键词
- `Iranian regime fall`
- `Iran x Israel conflict ends`
- `Iran x US conflict ends`
- `simple election winner`
- `simple geopolitical binary`

### 账户级硬黑名单
- 无

### 账户级软黑名单
- 无

### 说明
补充池。这个号的问题不是脏，而是**太低频、太集中**。因此白名单方向可以放得相对宽一些，但实盘里必须额外做“单事件暴露上限”和“低频账户折价”。

---

## 3. kekkone

- 地址：`0x39d0f1dca6fb7e5514858c1a337724a426764fe8`
- 分层：`supplemental`
- 评分：**60**

### 所属板块
- 伊朗战争升级 / 美伊冲突升级
- 西方国家是否打击伊朗
- 冲突结束 / 军事行动终止
- 中东重大军事二元事件

### 白名单关键词
- `US invade Iran`
- `Iranian regime fall`
- `France strike Iran`
- `UK strike Iran`
- `Germany strike Iran`
- `Trump announces end of operations`
- `simple Iran escalation binary`

### 账户级硬黑名单
- `forces enter`
- `us forces enter`
- `ceasefire`

### 账户级软黑名单
- `Netanyahu out`
- `Kharg Island no longer under Iranian control`
- `bitcoin range`
- `bitcoin between`
- `multi-deadline`

### 说明
补充池，也是你当前口径下的 **60 分及格锚点**。这个号同 token 快风险很低，但多子市场占比高，所以白名单只能保留最直观的单边升级题材；凡是多 deadline、区间、停火、政治衍生簇，都要压下去。

---

## 4. Moond

- 地址：`0x9dfe2f73d3c988a9d69df8fa0beb85651340b3dd`
- 分层：`watch`
- 评分：**53**

### 所属板块
- 伊朗政局 / 以伊局势
- 霍尔木兹海峡相关题材
- 中东政治人物/政权事件
- 少量宏观利率题材

### 白名单关键词
- `Netanyahu out`
- `Iranian regime fall`
- `Strait of Hormuz close`
- `Fed no change`
- `simple macro binary`

### 账户级硬黑名单
- `forces enter`
- `us forces enter`
- `ceasefire`
- `supreme leader`
- `public appearance`
- `P2P sale`
- `MrBeast`
- `range`

### 账户级软黑名单
- `successor`
- `multi-deadline Iran politics`
- `Iran politics cluster`

### 说明
观察池。题材覆盖不差，但双边和同 token 快风险都高于 kekkone。白名单只保留最简单的方向盘；人物接班、露脸、娱乐、区间题材都不建议碰。

---

## 5. leCommissaire

- 地址：`0x9238743eeba8bbfe9e85ac7ba2e1e3d77877b73e`
- 分层：`disabled`
- 评分：**44**

### 所属板块
- 俄乌前线推进
- 停火 / conflict deadline
- 地点级军事推进二元市场
- 前线占领 / 进入 / 再进入题材

### 白名单关键词
- `Russia x Ukraine ceasefire`
- `single-location`
- `single-deadline`
- `frontline binary`

### 账户级硬黑名单
- `conflict ends`
- `us forces enter`
- `forces enter`
- `meeting`
- `re-enter`

### 账户级软黑名单
- `capture`
- `enter`

### 说明
默认排除。它不是完全没有可跟部分，但只有非常窄的一块能保留：**单地点、单 deadline、单腿的前线二元市场**。只要进入 `capture/enter` 的大簇，就很容易落入结构化或快调仓。

---

## 6. KBO30

- 地址：`0x1aeebd7b0eb92037a630004f8eabc0759c36c139`
- 分层：`disabled`
- 评分：**42**

### 所属板块
- 体育 winner / championship 盘
- 联赛排名 / top 4 / relegation
- 娱乐 winner 结果盘
- 典型多结果结构盘

### 白名单关键词
- 无。**不建议建立白名单。**

### 账户级硬黑名单
- `winner`
- `championship`
- `top 4`
- `quarter-finals`
- `relegated`
- `sports winner`
- `entertainment winner`

### 账户级软黑名单
- 无

### 说明
直接排除。这个号的主问题不是快交易，而是**体育/娱乐多 outcome 结构腿**。即使表面上有些持仓时间不短，也不等于适合复制。

---

## 7. Toncar16

- 地址：`0x41583f2efc720b8e2682750fffb67f2806fece9f`
- 分层：`disabled`
- 评分：**41**

### 所属板块
- 中东突发军事事件
- 伊朗周边升级 / 打击 / 网络战
- ceasefire / strike / country-action 类盘
- 人物接班 / 二轮晋级结构题材

### 白名单关键词
- `Iran strike a Gulf State`
- `Kharg Island no longer under Iranian control`
- `cyberattack`
- `simple ceasefire`
- `single-country strike`

### 账户级硬黑名单
- `advance to the second round`
- `second round`
- `successor`
- `supreme leader`
- `which countries`
- `another country strike`
- `meeting`
- `forces enter`
- `us forces enter`

### 账户级软黑名单
- `strike`
- `ceasefire`

### 说明
默认排除。虽然这个号里不是完全没有能看的单腿，但可保留范围太窄，而且同 token 快风险、多腿、持仓偏短同时存在，脚本实战不划算。

---

## 8. Nostdam

- 地址：`0xe732156a2d84cdfb4de831d3f11a22899e49898f`
- 分层：`disabled`
- 评分：**15**

### 所属板块
- 体育 moneyline / spread / O/U
- player props / sports props
- 分钟级盘口短打
- same-token 快 round-trip

### 白名单关键词
- 无。**不建议建立白名单。**

### 账户级硬黑名单
- `moneyline`
- `spread`
- `over/under`
- `O/U`
- `first blood`
- `player stats`
- `sports range`
- `sports props`

### 账户级软黑名单
- 无

### 说明
直接排除。这个号最典型地命中了你最在意的风险：**同 token 分钟级快进快出**。它的问题不是“题材脏一点”，而是根本复制不了。

---

## 9. 0x5095e97281f28d4d8549fd3834802c24cbb793ee

- 地址：`0x5095e97281f28d4d8549fd3834802c24cbb793ee`
- 分层：`disabled`
- 评分：**15**

### 所属板块
- 电影票房
- opening weekend
- box office 区间盘
- `between X and Y` 分布交易

### 白名单关键词
- 无。**不建议建立白名单。**

### 账户级硬黑名单
- `box office`
- `opening weekend`
- `between`
- `票房`
- `区间盘`

### 账户级软黑名单
- 无

### 说明
直接排除。这个号的问题不在快，而在**区间/票房分布结构**。你看到的是单腿，它赚的是整组分布。

---

## 10. Zippy

- 地址：`0x48e7ca9d4754021dc8b32adcaec0234dd6c9d5f8`
- 分层：`disabled`
- 评分：**5**

### 所属板块
- highest grossing movie
- 电影篮子 / movie basket
- 年度票房赢家盘

### 白名单关键词
- 无。**不建议建立白名单。**

### 账户级硬黑名单
- `highest grossing movie`
- `movie basket`
- `film basket`
- `highest-grossing-movie`
- `movie winner`

### 账户级软黑名单
- 无

### 说明
直接排除。样本本身就少，而且本质上是电影篮子盘，既不干净，也没有足够利用价值。

---

## 11. intrepid

- 地址：`0xd66f79a8d19d4223b6c70dd4e620d4875501a19b`
- 分层：`disabled`
- 评分：**32**（低可信度，因样本只有 BUY、无 SELL）

### 所属板块
- 足球赛果 1X2
- `win on` / `end in a draw`
- 同场三结果结构盘
- 英超 / 欧冠 / 欧联 / 足总杯 / 意甲 / 西甲等足球赛果簇

### 白名单关键词
- 无。**不建议建立白名单。**

### 账户级硬黑名单
- `win on`
- `end in a draw`
- `draw`
- `both teams to score`
- `match winner`
- `moneyline`
- `1x2`
- `Premier League`
- `Champions League`
- `Europa League`
- `FA Cup`
- `Serie A`
- `La Liga`
- `Championship`

### 账户级软黑名单
- `soccer`
- `football`
- `league match`
- `cup match`

### 说明
直接排除。这个号交易很多，但几乎都集中在**足球同场多腿 / draw / 1X2 结构盘**里，而且同一 condition 双边买入极重。它的问题不是机会少，而是机会几乎全是“毒腿”。

---

## 最后的实用说明

如果你后面继续写单账号分析报告，建议固定采用这四个输出项：

1. **所属板块**：说明这个号主要在哪些题材簇活跃；
2. **白名单关键词**：说明这个号内部相对更值得保留的方向；
3. **账户级硬黑名单**：建议直接屏蔽；
4. **账户级软黑名单**：默认跳过，仅在额外确认后才放行。

这样你后续新增账号时，文档风格和脚本逻辑都会更统一。
