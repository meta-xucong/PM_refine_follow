# 03 API 与数据源

## 官方 API 范围

系统只使用 Polymarket 公开 Data API：

- `https://data-api.polymarket.com/v1/leaderboard`
- `https://data-api.polymarket.com/activity`
- `https://data-api.polymarket.com/value`
- `https://data-api.polymarket.com/traded`
- `https://data-api.polymarket.com/positions`
- `https://data-api.polymarket.com/closed-positions`
- `https://data-api.polymarket.com/v1/accounting/snapshot`

不使用：

- CLOB 下单、撤单、签名、订单管理接口
- 私钥或 API key
- 第三方非官方排行榜源

## Leaderboard

Endpoint:

```text
GET /v1/leaderboard
```

参数：

- `category`: `OVERALL`, `POLITICS`, `SPORTS`, `CRYPTO`, `CULTURE`, `MENTIONS`, `WEATHER`, `ECONOMICS`, `TECH`, `FINANCE`
- `timePeriod`: `DAY`, `WEEK`, `MONTH`, `ALL`
- `orderBy`: `PNL`, `VOL`
- `limit`: 1 到 50
- `offset`: 官方文档为 0 到 1000

实测注意：

- 单 shard 深 offset 会在约 rank 10001 处表现出 cap。
- 因此必须有 cap 检测和多 shard 候选池。

## Activity

Endpoint:

```text
GET /activity?user=...&type=TRADE&start=...&end=...&limit=...&offset=...
```

用途：

- 预筛高频。
- 生成评分所需交易 CSV。
- 计算账户行为、持仓周期、双边、多市场结构等指标。

策略：

- 预筛使用最近 7 天浅拉。
- 完整评分默认拉最近 30 天。
- 遇到 offset 限制时按时间窗口切分。

## Account Summary

现有 `fetch_polymarket_summary.py` 已覆盖：

- `/value`: 当前持仓价值
- `/traded`: 累计交易市场数
- `/positions`: 当前持仓
- `/closed-positions`: 已平仓记录和 realized PnL 曲线
- `/v1/accounting/snapshot`: equity/positions 快照 ZIP

## 可复用外部仓库逻辑

参考仓库：

```text
F:\AI\copytrade_v5_muti-clob-v2
```

可复用文件：

```text
smartmoney_query/poly_martmoney_query/api_client.py
smartmoney_query/poly_martmoney_query/models.py
smartmoney_query/poly_martmoney_query/processors.py
```

优先复用点：

- `DataApiClient.fetch_leaderboard()`
- `DataApiClient.fetch_activity_actions()`
- `DataApiClient.fetch_trade_actions_window_from_activity()`
- `DataApiClient.fetch_positions()`
- `DataApiClient.fetch_closed_positions()`
- `_request_with_backoff()`
- `RateLimiter`

## 官方文档

- https://docs.polymarket.com/api-reference/introduction
- https://docs.polymarket.com/api-reference/core/get-trader-leaderboard-rankings
- https://docs.polymarket.com/api-reference/core/get-user-activity
- https://docs.polymarket.com/api-reference/core/get-current-positions-for-a-user
- https://docs.polymarket.com/api-reference/core/get-closed-positions-for-a-user
- https://docs.polymarket.com/api-reference/core/get-total-value-of-a-users-positions
- https://docs.polymarket.com/api-reference/misc/get-total-markets-a-user-has-traded
- https://docs.polymarket.com/api-reference/misc/download-an-accounting-snapshot-zip-of-csvs

