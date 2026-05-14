# 04 数据模型与存储

## 运行目录

```text
runtime/auto_screen/
  state.sqlite
  logs/
  account_cache/
    <wallet>/
      activity.csv
      account_summary.json
      account_analysis.json
      report_zh.md
      report_en.md
      metadata.json
  exports/
    polymarket_auto_screen.xlsx
```

## SQLite 表

SQLite 是唯一运行状态源。

### `scan_cycles`

| 字段 | 类型 | 说明 |
|---|---|---|
| `cycle_id` | integer primary key | 扫描轮次 |
| `started_at_utc` | text | 开始时间 |
| `completed_at_utc` | text | 完成时间 |
| `status` | text | `running` / `completed` / `failed` |
| `candidate_pool_target` | integer | 目标候选数 |
| `unique_candidates` | integer | 实际唯一候选数 |
| `processed_count` | integer | 已处理账号数 |
| `alert_count` | integer | 推送账号数 |
| `api_cap_summary` | text | shard cap 摘要 JSON |

### `leaderboard_shards`

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | integer primary key | shard id |
| `cycle_id` | integer | 轮次 |
| `period` | text | `MONTH` / `WEEK` / `ALL` |
| `order_by` | text | `PNL` / `VOL` |
| `category` | text | 分类 |
| `status` | text | `pending` / `running` / `completed` / `capped` / `failed` |
| `last_offset` | integer | 最后 offset |
| `last_rank` | integer | 最后 rank |
| `unique_wallets_seen` | integer | shard 内唯一账号 |
| `api_cap_rank` | integer | 发现 cap 的 rank |
| `error` | text | 错误信息 |

### `candidates`

| 字段 | 类型 | 说明 |
|---|---|---|
| `cycle_id` | integer | 轮次 |
| `proxy_wallet` | text | 钱包 |
| `user_name` | text | 用户名 |
| `x_username` | text | X 用户名 |
| `verified_badge` | integer | 是否认证 |
| `best_rank` | integer | 最好 rank |
| `month_pnl` | real | 月 PnL |
| `month_vol` | real | 月成交量 |
| `week_pnl` | real | 周 PnL |
| `week_vol` | real | 周成交量 |
| `all_pnl` | real | 全周期 PnL |
| `all_vol` | real | 全周期成交量 |
| `category_hits` | text | 命中分类 JSON |
| `source_shards` | text | 来源 shard JSON |
| `priority_score` | real | 处理优先级 |
| `first_seen_at_utc` | text | 首次发现 |
| `last_seen_at_utc` | text | 最近发现 |
| `status` | text | `pending` / `refresh_score` / `skipped` / `store_only` / `push_watchlist` 等 |
| `leaderboard_context.seen_before` | bool | 是否曾在本地候选池出现过 |
| `leaderboard_context.scan_prompt` | text | 旧地址重扫提示，当前为“刷新分数” |

唯一键：

```text
(cycle_id, proxy_wallet)
```

当前落地实现以 `address` 作为候选主键保存最新状态。重扫榜单时，如果地址已存在，会写入 `status=refresh_score`，并保留 `previous_status` / `previous_updated_at` 供前端和评分产物识别这次属于刷新评分。

### `account_runs`

| 字段 | 类型 | 说明 |
|---|---|---|
| `run_id` | integer primary key | 单账号运行 |
| `cycle_id` | integer | 轮次 |
| `proxy_wallet` | text | 钱包 |
| `status` | text | 状态 |
| `prefilter_status` | text | `passed` / `skipped` |
| `prefilter_reason` | text | 跳过原因 |
| `activity_rows` | integer | 完整 activity 行数 |
| `trade_count` | integer | 评分交易数 |
| `active_trading_days` | real | 活跃天 |
| `raw_score` | real | 原始分 |
| `anchored_score` | real | 锚点分 |
| `final_score` | real | 决策分 |
| `decision` | text | 结论 |
| `analysis_json_path` | text | 分析 JSON |
| `report_zh_path` | text | 中文报告 |
| `report_en_path` | text | 英文报告 |
| `started_at_utc` | text | 开始时间 |
| `finished_at_utc` | text | 完成时间 |
| `error` | text | 错误 |

### `alerts`

| 字段 | 类型 | 说明 |
|---|---|---|
| `alert_id` | integer primary key | 推送 id |
| `cycle_id` | integer | 轮次 |
| `proxy_wallet` | text | 钱包 |
| `final_score` | real | 分数 |
| `pushed_at_utc` | text | 推送时间 |
| `serverchan_result` | text | 推送结果 JSON |
| `excel_written` | integer | 是否写入 Excel |
| `push_status` | text | `pending` / `sent` / `dry_run` / `disabled` / `archived` |
| `push_batch_id` | text | 批量推送 id |
| `push_result` | text | 最近一次 ServerChan 返回 JSON |

ServerChan 采用批量推送：告警先进入 `pending`，凑满 `serverchan.batch_size` 后统一发送；历史无 `push_status` 的旧告警迁移时会标记为 `sent`，避免重复推送。若评分/消息结构升级后 pending 告警缺少当前要求的消息字段，系统会在推送前把它们标记为 `archived`，避免旧规则候选和新规则候选混批推送。

## Excel 输出

Excel 文件：

```text
runtime/auto_screen/exports/polymarket_auto_screen.xlsx
```

Sheet：

- `alerts`
- `all_scored`
- `skipped`
- `cycles`

Excel 只做查看和复盘，不作为恢复状态依据。
