# 09 运维手册

## 启动

开发调试：

```powershell
python -m auto_screen.cli once --config auto_screen_config.json --limit-candidates 10 --dry-run-alerts
```

常驻运行：

```powershell
python -m auto_screen.cli run --config auto_screen_config.json
```

常驻模式的一整轮不是固定处理 25 个账号。系统先扫描候选池，再按 `process_batch_size` 分批处理 pending 地址；默认 `process_batch_size=25` 只是每批大小。只有本轮 pending 候选处理完后，cycle 才完成并进入下一轮。

如果新一轮从排行榜开头扫到历史已出现地址，候选状态会变成 `refresh_score`，前端提示“刷新分数”。`refresh_score` 会和 `pending` 一样进入处理队列，用最新交易数据重新计算评分。

## 查看状态

```powershell
python -m auto_screen.cli status --config auto_screen_config.json
```

状态应展示：

- 当前 cycle
- 当前 shard
- 候选总数
- 已处理数
- 跳过数
- 高分推送数
- 最近错误
- heartbeat 时间

## 停止

用 Ctrl+C 停止。系统应在当前账号处理完后安全退出，并保留 SQLite 状态。

Windows 脚本后续提供：

```powershell
windows\stop_auto_screen.ps1
```

## 恢复

重新执行：

```powershell
python -m auto_screen.cli run --config auto_screen_config.json
```

系统按 SQLite 状态恢复：

- 当前 cycle 未完成：继续。
- 当前 cycle 已完成：等待或开始下一轮。
- 上次账号处于 `collecting`：按 retry 规则重试或标记失败。

## 日志

目录：

```text
runtime/auto_screen/logs/
```

建议日志文件：

- `auto_screen.log`
- `api_errors.log`
- `alerts.log`

日志不能包含：

- 完整 ServerChan SendKey
- 任何私钥或交易凭证

## Excel

文件：

```text
runtime/auto_screen/exports/polymarket_auto_screen.xlsx
```

人工主要看：

- `alerts`: 可跟单候选
- `all_scored`: 所有完整评分账号
- `skipped`: 高频和低信号排除
- `cycles`: 每轮概览

## ServerChan

SendKey 读取顺序：

1. 环境变量 `SCT_SENDKEY`
2. `%USERPROFILE%\.codex\secrets\serverchan_sendkey.txt`

推送策略：

- 命中 `final_score > alert_threshold` 的候选会立即写入 SQLite `alerts` 和 Excel `alerts`。
- 默认不会单个账号立刻推送，而是记录为 `push_status=pending`。
- 当 pending 告警数量达到 `serverchan.batch_size`，默认 `10`，系统发送一条 ServerChan 汇总消息，并把该批标记为 `sent`。
- pending 不满 10 个时会保留到后续账号或后续轮次继续凑批。
- 推送前会检查 pending 告警是否包含当前评分版本要求的消息字段，例如 `总PnL`、`账号年龄天数`、`PnL平滑调整`、`长期活跃调整`。缺少这些字段的旧规则 pending 会标记为 `archived`，不会和新规则候选混发。

推送失败：

- 记录进 SQLite。
- 当前批保持 `push_status=pending`，不阻塞后续账号处理。
- 后续启动或后续命中账号时，若 pending 仍满足批量阈值，会再次尝试推送。

## 常见问题

### leaderboard 卡在某个 rank

这是 API cap 或重复页。scanner 应记录 `api_cap_rank` 并进入下一个 shard。

### 高频账号太多

先看 `skipped` sheet：

- 如果误杀太多，调高 `max_trades_per_active_day`。
- 如果完整评分太慢，降低 `sample_max_records` 或 `sample_max_unique_tx`。
- 当前采集器会在 activity 时间片达到约 1000 行后探测 `offset=3000`。如果探针发现该时间片超过官方历史 offset 上限，会直接拆分时间片；如果 1 天以内仍超过上限，则标记为高频账号跳过。这只优化采集效率，不改变评分规则。
- 摘要接口默认每次请求之间间隔 `0.1s`，activity 接口默认每页/每片间隔 `0.2s`。如果日志出现 `HTTP 429`，优先把 `page_sleep_seconds`、`chunk_sleep_seconds` 或 `summary_fetch.request_sleep_seconds` 提高到 `0.3-0.5`。

### 推送太多

调高：

- `alert_score_threshold`
- `serverchan.dedupe_days`
- `serverchan.batch_size`

或临时设置：

```json
{"runtime": {"dry_run_alerts": true}}
```

### Excel 被打开导致写入失败

建议初版处理：

- 写临时文件再原子替换。
- 如果替换失败，记录错误，下一轮重试。
