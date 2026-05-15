# 13 官方可信信源候选池开发文档

## 1. 目标

在官方 leaderboard 深分页约 10050 名触顶的前提下，继续扩大可分析账号池，但候选发现必须优先依赖可信官方信源。

本章落地范围：

- 保留现有 `/v1/leaderboard` 多分片。
- 新增 Gamma `/markets` 热门市场发现。
- 新增 Data API `/trades` 热门市场交易钱包发现。
- 新增 Data API `/holders` 热门市场持仓钱包发现。
- 所有来源统一合并为 `AccountCandidate`，并写入 `leaderboard_context.source_evidence` 作为后续评分和人工复核证据。

非目标：

- 不接入 CLOB 下单接口。
- 不使用第三方榜单直接决定评分。
- 不因为出现在热门市场交易/持仓里就直接推送；所有账号仍必须经过预筛、完整数据拉取、Auto V3 评分。

## 2. 官方信源边界

| 信源 | Endpoint | 用途 | 可信度 | 默认动作 |
|---|---|---|---|---|
| Leaderboard | `https://data-api.polymarket.com/v1/leaderboard` | PnL/成交量榜单候选 | 高 | 已有，继续作为主候选源 |
| Markets | `https://gamma-api.polymarket.com/markets` | 找近期热门、活跃、开放市场 | 高 | 新增，用于 trades/holders 的市场入口 |
| Trades | `https://data-api.polymarket.com/trades` | 从热门市场成交记录反推活跃钱包 | 高 | 新增，只做候选发现 |
| Holders | `https://data-api.polymarket.com/holders` | 从热门市场持仓榜反推中等规模钱包 | 高 | 新增，只做候选发现 |
| Activity | `https://data-api.polymarket.com/activity` | 已有预筛/完整拉取 | 高 | 继续用于高频过滤和交易历史 |

官方文档参考：

- Leaderboard: `https://docs.polymarket.com/api-reference/core/get-trader-leaderboard-rankings`
- Markets: `https://docs.polymarket.com/api-reference/markets/list-markets`
- Trades: `https://docs.polymarket.com/api-reference/core/get-trades-for-a-user-or-markets`
- Holders: `https://docs.polymarket.com/api-reference/core/get-top-holders-for-markets`
- Activity: `https://docs.polymarket.com/api-reference/core/get-user-activity`
- Rate limits: `https://docs.polymarket.com/api-reference/rate-limits`

## 3. 数据流

```text
Leaderboard shards
  -> AccountCandidate

Gamma /markets
  -> filter active/open/liquid/high-volume markets
  -> Data API /trades by market
      -> wallet candidates with trade evidence
  -> Data API /holders by market
      -> wallet candidates with holder evidence

Candidate merge
  -> SQLite candidates
  -> Prefilter
  -> Collector
  -> Auto V3 scoring
  -> Excel/ServerChan
```

## 4. 候选合并规则

候选唯一键：`proxyWallet` 小写地址。

合并字段：

- `source_keys`: 合并来源，例如 `["month_pnl", "market_trades", "holders"]`。
- `discovery_score`: 取最高来源分，再按多来源数量加小幅 bonus。
- `leaderboard_context.official_sources`: 官方新增来源列表。
- `leaderboard_context.source_evidence`: 保留最多 30 条来源证据。
- `leaderboard_context.official_trade_count`: 官方热门市场交易次数。
- `leaderboard_context.official_trade_usdc`: 官方热门市场交易估算金额。
- `leaderboard_context.official_trade_market_count`: 交易来源市场数。
- `leaderboard_context.official_holder_balance`: 官方热门市场持仓余额合计。
- `leaderboard_context.official_holder_market_count`: 持仓来源市场数。

这些字段只影响候选处理优先级和人工解释，不直接绕过最终评分。

## 5. 热门市场筛选规则

默认配置：

```json
{
  "market_discovery": {
    "enabled": true,
    "limit": 25,
    "active": true,
    "closed": false,
    "order": "volume24hr",
    "ascending": false,
    "min_volume_24h": 1000,
    "min_liquidity": 100,
    "require_orderbook": true,
    "categories": []
  }
}
```

解释：

- 只扫开放市场，避免旧市场结算噪声。
- 按 24 小时成交量排序，优先近期活跃市场。
- 最低成交量和流动性避免极冷门市场。
- `categories` 默认空，表示不按分类过滤；后续可按 SPORTS/CRYPTO/POLITICS 等做多组任务。

## 6. Trades 候选规则

默认配置：

```json
{
  "market_trades": {
    "enabled": true,
    "markets_limit": 10,
    "limit_per_market": 100,
    "filter_type": "CASH",
    "min_cash": 25,
    "min_address_cash": 50,
    "max_address_trades_per_market": 80
  }
}
```

解释：

- 每轮只取前 10 个热门市场，控制请求量。
- 每个市场最多取 100 条成交。
- `filterType=CASH` 和 `filterAmount=25` 用于过滤太小的成交。
- 地址在单市场累计成交额至少 50 才进入候选。
- 单市场交易次数过高的地址不从该来源进入候选，避免热门市场高频/做市噪声。

## 7. Holders 候选规则

默认配置：

```json
{
  "holders": {
    "enabled": true,
    "markets_limit": 10,
    "limit_per_market": 20,
    "min_balance": 10,
    "max_balance": 250000
  }
}
```

解释：

- 每个热门市场只取 top holders 中的前 20。
- 低于 10 的余额视为噪声。
- 高于 250000 的余额默认排除，避免超大资金账号直接占据候选优先级。
- Holder 来源只说明“当前有持仓”，不能证明历史可跟单，必须进入完整评分。

## 8. 模块清单

| 文件 | 责任 |
|---|---|
| `auto_screen/data_api.py` | 增加 `fetch_trades`、`fetch_holders`、`GammaApiClient.fetch_markets` |
| `auto_screen/official_sources.py` | 新增官方多来源候选发现、证据合并、候选排序 |
| `auto_screen/scheduler.py` | 从 `official_sources.scan_candidates` 获取候选，进度支持官方信源 |
| `dashboard/server.py` | `/api/status` 暴露 `candidate_source` |
| `dashboard/static/app.js` | 前端显示当前官方信源扫描进度 |
| `auto_screen_config*.json` | 增加 `candidate_sources` 配置 |

## 9. 验收标准

代码级：

- 新模块能在 leaderboard 关闭时，仅通过官方 markets/trades/holders 产生候选。
- 同一地址同时出现在 trades 和 holders 时会合并为一个候选，并保留两个来源证据。
- 旧 leaderboard 扫描器的触顶检测仍然有效。
- Scheduler 旧测试 patch `scan_candidates` 仍然兼容。

运行级：

- `python -m compileall auto_screen dashboard` 通过。
- `python -m pytest -q` 通过。
- 小规模 dry-run 能从官方信源发现候选，进入预筛流程，并且 `--dry-run-alerts` 不真实推送。

风控级：

- 默认新增官方源请求量约为：
  - Gamma markets: 1 次；
  - trades: 最多 10 次；
  - holders: 最多 10 次；
  - 合计约 21 次/轮。
- 这些请求使用现有 `scan.sleep_seconds`/Gamma `sleep_seconds` 进行轻量限速。
- 扩大到更多市场前，应先观察 429、SSL EOF、Cloudflare 队列情况。

## 10. 后续可扩展项

- 增加分类分批：SPORTS/CRYPTO/POLITICS/WEATHER 分别扫不同热门市场。
- 增加 source contribution 看板：每个来源贡献多少新增候选。
- 给 source evidence 进入 Excel，方便人工复核账号为什么被发现。
- 外部第三方榜单只作为手工导入 watchlist，不作为自动评分依据。
