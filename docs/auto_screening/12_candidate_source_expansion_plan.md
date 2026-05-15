# 12 候选账号来源扩容方案

## 背景结论

当前系统的 `max_rank=100000` 是目标上限，不代表 Polymarket 官方排行榜接口一定能给出完整前 10 万。官方文档显示 `/v1/leaderboard` 单页 `limit` 最大 50，`offset` 文档范围为 0 到 1000；实测更深 offset 虽可请求，但会在约 10050 名附近返回重复或不稳定的末端排名。

因此，后续目标应从“单一排行榜前 10 万”调整为：

> 用多个官方数据源和可审计的外部榜单信号，持续构建最多 10 万个近期活跃、表现较好、可跟单价值较高的钱包候选池。

参考资料：

- 官方 Leaderboard：`https://docs.polymarket.com/api-reference/core/get-trader-leaderboard-rankings`
- 官方 API 总览：`https://docs.polymarket.com/api-reference/introduction`
- 官方 Market Data 总览：`https://docs.polymarket.com/market-data/overview`
- 官方 Rate Limits：`https://docs.polymarket.com/api-reference/rate-limits`
- 官方 Holders：`https://docs.polymarket.com/api-reference/core/get-top-holders-for-markets`
- 官方 Activity：`https://docs.polymarket.com/api-reference/core/get-user-activity`
- 官方 Trades：`https://docs.polymarket.com/api-reference/core/get-trades-for-a-user-or-markets`

## 已落地的第一阶段修正

### 1. 官方榜单触顶检测

扫描器现在会比较请求 offset 与返回 rank：

- 如果请求 `offset=10050`，理论起始排名应为 10051；
- 如果接口返回的最大 rank 仍小于请求起始排名，比如仍为 10050；
- 则判定该 leaderboard shard 已触顶，记录 `api_cap_rank`，并停止继续请求该 shard。

这样可以避免两个问题：

- 不再把重复末端页误认为“继续扫到了 10 万名”。
- 不再浪费大量请求等待 `leaderboard_no_new_pages_stop` 慢慢触发。

### 2. 前端可见上限提示

前端状态面板新增“官方榜单可见上限”：

- 目标上限：配置中的 `scan.max_rank`，默认 100000。
- 官方可见上限：运行时检测到的 `api_visible_cap_rank`。
- 多榜合并候选：本轮从多个 shard 合并去重后的候选数量。

## 候选源扩容总体架构

建议增加一个独立的候选发现层：

```text
CandidateSourceManager
  -> LeaderboardSource
  -> MarketTradeSource
  -> HolderSource
  -> ExternalReferenceSource
  -> HistoricalMemorySource
  -> CandidatePool
  -> Prefilter
  -> Full Collection
  -> Scoring
```

所有来源统一输出：

```json
{
  "address": "0x...",
  "source": "leaderboard|market_trades|holders|external_reference|memory",
  "source_key": "month_pnl_overall",
  "observed_at": "2026-05-15T00:00:00Z",
  "raw_rank": 100,
  "raw_score": 0.82,
  "reason": "月榜PnL靠前/热门市场高质量交易/持仓规模适中",
  "metadata": {}
}
```

候选池按地址去重，并保留多来源证据。后续排序不只看排行榜 rank，而看：

- 来源可信度；
- 来源数量；
- 近期活跃度；
- 最近 PnL 是否为正；
- 是否出现在多个时间窗口；
- 是否经过旧数据验证。

## 来源一：官方 Leaderboard 多维 shard

这是当前已有来源，应继续保留，但需要改得更标准。

官方支持维度：

- `category`: `OVERALL`, `POLITICS`, `SPORTS`, `CRYPTO`, `CULTURE`, `MENTIONS`, `WEATHER`, `ECONOMICS`, `TECH`, `FINANCE`
- `timePeriod`: `DAY`, `WEEK`, `MONTH`, `ALL`
- `orderBy`: `PNL`, `VOL`

建议第一批扩展 shard：

```text
OVERALL: WEEK/MONTH/ALL x PNL/VOL
SPORTS: WEEK/MONTH x PNL/VOL
CRYPTO: WEEK/MONTH x PNL/VOL
POLITICS: WEEK/MONTH x PNL/VOL
WEATHER: WEEK/MONTH x PNL/VOL
ECONOMICS: MONTH x PNL/VOL
FINANCE: MONTH x PNL/VOL
```

这样可以从“4 个 shard”扩展到约 26 个 shard。即使每个 shard 只能稳定给出约 10050 名，去重后也能明显扩大候选池。

风险：

- 分类 shard 之间重叠会很高。
- DAY 榜容易引入短期暴涨账号，不适合作为高权重来源。
- VOL 榜容易混入高频/做市/套利账号，只能作为活跃信号，不应直接加高分。

落地建议：

- 把 shard 配置改成官方参数名 `timePeriod/orderBy/category`。
- 每个 shard 独立记录 `api_cap_rank`。
- 增加 `source_weight`：
  - MONTH PNL: 1.00
  - WEEK PNL: 0.80
  - ALL PNL: 0.75
  - MONTH VOL: 0.45
  - WEEK VOL: 0.35
  - DAY PNL/VOL: 0.20，仅用于发现，不用于加分

## 来源二：热门市场 Trade 扫描

官方 `/trades` 支持按 `market`、`eventId`、`user`、`side` 过滤，并返回 `proxyWallet`、交易方向、成交量、价格、时间等字段。这个来源适合补充 leaderboard 拿不到的活跃钱包。

流程：

1. 用 Gamma API 拉取近期活跃市场：
   - 按成交量、流动性、开放状态、结束时间排序。
   - 每个分类取 Top N 个市场。
2. 对每个市场调用 Data API `/trades`：
   - 拉最近 7 天/30 天交易。
   - 提取 `proxyWallet`。
   - 过滤明显高频、超小额、重复对倒嫌疑地址。
3. 对地址生成候选证据：
   - 近期参与高质量市场；
   - 交易金额达到最低阈值；
   - 不是单一市场孤注一掷；
   - 多市场复现则提高候选优先级。

建议默认参数：

```json
{
  "market_trade_source": {
    "enabled": true,
    "categories": ["SPORTS", "CRYPTO", "POLITICS", "WEATHER", "ECONOMICS"],
    "markets_per_category": 80,
    "trades_per_market": 1000,
    "lookback_days": 30,
    "min_trade_usdc": 50,
    "max_trades_per_day_prefilter": 600
  }
}
```

优点：

- 可以发现不在榜单前 10050 的活跃交易者。
- 能覆盖近期真正有交易动作的钱包。
- 能通过市场维度识别擅长领域。

风险：

- 原始交易噪声大，需要强预筛。
- 热门市场会有大量套利和做市账号。
- 需要严格限速和缓存，否则请求量会变大。

## 来源三：热门市场 Holder 扫描

官方 `/holders` 返回市场 top holders，单 token `limit` 最大 20。这个来源不是完整排名，但适合发现“当前有中等规模仓位”的钱包。

流程：

1. 从热门市场选 token/condition。
2. 调 `/holders` 拉 top holders。
3. 过滤：
   - 过大鲸鱼仓位；
   - 单市场过度集中；
   - 新号重仓；
   - 同市场 YES/NO 对冲明显的地址。
4. 把剩余地址进入候选池。

适合加分的情况：

- 多个市场持仓金额适中；
- 持仓方向和历史胜率一致；
- 持仓不是临近结算才突然出现；
- 账户历史 PnL 平滑。

不适合直接加分的情况：

- 单市场巨额持仓；
- 只在一个事件上重仓；
- 只有未结算浮盈，没有已实现盈利。

## 来源四：第三方榜单参考源

第三方榜单不能直接作为真值，但可以作为“候选发现”和“交叉验证”。

搜索到的可参考方向：

- Polyranks：体育钱包 7 日 ROI 榜，明确要求 7 日窗口内至少交易 5 个体育市场、总下注和平均下注达到阈值，并排除市场做市倾向账号。
- PolymarketWallets：强调有用榜单应综合 PnL、volume、win rate、trade count、activity、account history。
- Predicts.guru：按 PnL、成交量、市场数、胜率、多时间窗口展示 trader。
- Merlin：展示 PnL、return、volume、分类、90 日 PnL 曲线和复制入口。
- WalletHunter：重点不是静态排行榜，而是跟踪 leaderboard wallet 的新开仓并推送提醒。

参考资料：

- `https://polyranks.io/leaderboard`
- `https://www.polymarketwallets.com/polymarket-leaderboard`
- `https://www.predicts.guru/leaderboard`
- `https://merlin.trade/leaderboard`
- `https://www.thewallethunter.com/`

落地方式：

- 不建议依赖爬虫强抓第三方页面，稳定性和合规风险都较高。
- 建议先把这些榜单的评价口径吸收到本系统评分与候选排序里。
- 如第三方后续提供 API 或导出，可作为 `ExternalReferenceSource`，只给发现权重，不直接改变最终评分。

可借鉴指标：

- ROI 需要最低交易额门槛，否则小样本容易虚高。
- 胜率必须结合交易额和市场数量，否则没有意义。
- 90 日 PnL 曲线比单点 PnL 更适合判断可跟单性。
- 分类榜比总榜更容易发现稳定型账号。
- 新开仓提醒适合作为跟单时效信号，但不适合替代长期评分。

## 来源五：历史记忆池

每一轮扫描不应只依赖本轮 API。建议保留历史候选记忆：

- 曾进入候选但未达标；
- 曾被推送；
- 曾被人工标注好/坏；
- 曾短期表现好但后续回撤；
- 曾被判定高频/做市/套利。

下一轮可以从历史池中抽取一部分复查：

```text
每天复查：
  - 最近 7 天新入池但未完整评分的钱包
  - 过去 30 天 B/C 级但最近活跃的钱包
  - 人工标记 watch/good_candidate 的钱包

每周复查：
  - 曾经高分但近期未活跃的钱包
  - 曾经被拒绝但不是硬风险的钱包
```

这样可以让候选池逐步逼近 10 万，而不是每次被官方 leaderboard cap 卡住。

## 优先级排序公式

候选发现阶段建议新增 `candidate_source_score`，只用于处理顺序，不直接等于最终评分。

```text
candidate_source_score =
  35 * leaderboard_signal
+ 25 * recent_trade_signal
+ 15 * holder_signal
+ 15 * multi_source_confirmation
+ 10 * historical_memory_signal
- risk_penalty
```

解释：

- `leaderboard_signal`：来自 PnL 榜，且不是 DAY 榜，排名越靠前越高。
- `recent_trade_signal`：近期参与多个高质量市场，交易规模适中。
- `holder_signal`：当前持仓规模适中、不过度集中。
- `multi_source_confirmation`：同一地址在多个来源出现。
- `historical_memory_signal`：历史曾被评为 B/C 或人工 watch。
- `risk_penalty`：高频、单市场孤注一掷、异常暴涨、账户太新、疑似做市。

## 分阶段落地计划

### Phase 1：Leaderboard 标准化扩展

- 把 shard 参数统一为官方 `category/timePeriod/orderBy`。
- 增加分类 shard。
- 在本地状态库记录每个 shard 的 `api_cap_rank`、`pages_fetched`、`unique_added`。
- 前端展示每个 shard 的触顶位置和贡献候选数。

验收：

- 每轮候选数明显高于当前 10050 左右。
- 前端能解释为什么没有达到 100000。
- 单轮请求量可控，不出现频繁 SSL/429/Cloudflare 队列。

### Phase 2：MarketTradeSource

- 新增 `candidate_sources/market_trades.py`。
- Gamma API 拉热门市场。
- Data API `/trades` 拉市场交易地址。
- 引入缓存，避免同一市场反复扫。
- 输出统一 CandidateEvidence。

验收：

- 候选池能发现 leaderboard 未出现的钱包。
- 高频/做市地址在预筛阶段被明显压低。
- 前端显示来源为“热门市场交易”。

### Phase 3：HolderSource

- 新增 `candidate_sources/holders.py`。
- 对热门市场 top holders 抽样。
- 与历史 PnL/账户年龄/活跃度结合预筛。

验收：

- 能发现中等规模、非巨鲸、非单点暴露的钱包。
- 单市场重仓钱包不会直接高分。

### Phase 4：外部参考与人工反馈

- 新增 `external_references.json`，支持手工导入第三方榜单地址。
- 支持来源标记：`polyranks`, `predicts_guru`, `merlin`, `manual_watchlist`。
- 外部来源只增加发现优先级，不覆盖评分。

验收：

- 手工导入地址后能进入候选池并完整评分。
- 推送和 Excel 中能看到来源证据。

## 推荐下一步

下一轮开发优先做 Phase 1 和 Phase 2。理由：

- Phase 1 成本低，能立刻扩大官方 leaderboard 覆盖面。
- Phase 2 是突破 10050 限制的关键，因为它从市场交易反推钱包，而不是依赖榜单深分页。
- Phase 3 和 Phase 4 可以在候选池稳定后再补。
