# 06 配置规范

配置文件建议命名：

```text
auto_screen_config.json
```

## 完整示例

```json
{
  "leaderboard": {
    "page_size": 50,
    "candidate_pool_target": 100000,
    "cycle_cooldown_minutes": 60,
    "include_day_shards": false,
    "categories": [
      "OVERALL",
      "POLITICS",
      "SPORTS",
      "CRYPTO",
      "CULTURE",
      "MENTIONS",
      "WEATHER",
      "ECONOMICS",
      "TECH",
      "FINANCE"
    ],
    "periods": ["MONTH", "WEEK", "ALL"],
    "order_bys": ["PNL", "VOL"],
    "per_shard_rank_cap": 10001,
    "api_cap_repeat_pages": 2
  },
  "collection": {
    "analysis_window_days": 30,
    "activity_page_size": 500,
    "activity_days_per_chunk": 7,
    "activity_offset_probe_after_rows": 1000,
    "activity_historical_offset_limit": 3000,
    "activity_high_frequency_window_seconds": 86400,
    "summary_page_limit": 500,
    "max_closed_records": 5000,
    "max_open_records": 5000,
    "summary_request_sleep_seconds": 0.1,
    "request_timeout_seconds": 30,
    "max_retries": 4,
    "max_requests_per_second": 2
  },
  "prefilter": {
    "enabled": true,
    "sample_window_days": 7,
    "sample_activity_page_size": 500,
    "sample_max_records": 5000,
    "sample_max_unique_tx": 2000,
    "max_trades_per_active_day": 600,
    "min_recent_positive_pnl": 0,
    "min_recent_volume_for_negative_pnl": 100000
  },
  "scoring": {
    "score_version": "auto_v3",
    "anchor_file": "skill/polymarket-account-review-skill/baseline/baseline_anchor.json",
    "auto_v3_anchor_file": "skill/polymarket-account-review-skill/baseline/baseline_anchor_auto_v3.json",
    "alert_score_threshold": 40,
    "alert_score_comparison": ">",
    "report_languages": ["zh", "en"],
    "enable_data_quality_caps": true,
    "enable_high_frequency_caps": true,
    "enable_copy_capacity_score": true,
    "min_data_quality_for_push": 4,
    "min_data_quality_for_grade_b": 7,
    "min_data_quality_for_grade_a": 8
  },
  "output": {
    "sqlite_path": "runtime/auto_screen/state.sqlite",
    "account_cache_dir": "runtime/auto_screen/account_cache",
    "reports_dir": "runtime/auto_screen/reports",
    "excel_path": "runtime/auto_screen/exports/polymarket_auto_screen.xlsx",
    "log_dir": "runtime/auto_screen/logs"
  },
  "serverchan": {
    "enabled": true,
    "sendkey_env": "SCT_SENDKEY",
    "sendkey_file": "%USERPROFILE%/.codex/secrets/serverchan_sendkey.txt",
    "batch_size": 10,
    "required_message_markers": [
      "累计收益：||总PnL:",
      "账号已运行：||账号年龄天数:",
      "收益曲线平滑度：||PnL平滑调整:",
      "长期活跃表现：||长期活跃调整:"
    ],
    "dedupe_days": 7
  },
  "runtime": {
    "dry_run_alerts": false,
    "max_accounts_per_run": 0,
    "heartbeat_interval_seconds": 60,
    "retry_failed_after_minutes": 180
  }
}
```

## 推荐默认值

- `candidate_pool_target`: `100000`
- `cycle_cooldown_minutes`: `60`
- `failure_sleep_seconds`: `60`，外部 API 失败时的短重试间隔。
- `include_day_shards`: `false`
- `per_shard_rank_cap`: `10001`
- `leaderboard_no_new_pages_stop`: `40`
- `leaderboard_api_cap_stop_enabled`: `true`，当请求 offset 已超过接口返回 rank 时，判定官方 leaderboard shard 已触顶并停止继续翻页。
- `candidate_sources.enabled`: `true`，启用官方多来源候选池。
- `candidate_sources.official_only`: `true`，候选发现默认只使用官方公开信源。
- `candidate_sources.market_discovery.limit`: `25`，每轮先从 Gamma API 获取的热门市场数。
- `candidate_sources.market_trades.markets_limit`: `10`，每轮最多对 10 个热门市场拉 trades。
- `candidate_sources.holders.markets_limit`: `10`，每轮最多对 10 个热门市场拉 holders。
- `process_batch_size`: `25`，仅表示单次内部处理批次大小。
- `process_all_candidates_per_cycle`: `true`，常驻模式会处理完整个 pending 候选池后才进入下一轮。
- `analysis_window_days`: `30`
- `max_requests_per_second`: `2`
- `activity_offset_probe_after_rows`: `1000`，单个 activity 时间片先拉到约 1000 行后，用 offset=3000 的轻量探针判断是否会触发官方历史 offset 上限；命中后直接拆片或早停高频账号，避免反复拉到 offset=3500 才失败。
- `activity_historical_offset_limit`: `3000`，对应 Polymarket Data API 历史 activity offset 限制。
- `activity_high_frequency_window_seconds`: `86400`，如果 1 天以内仍超过历史 offset 上限，判定为明显高频账号并跳过完整评分。
- `summary_request_sleep_seconds`: `0.1`，summary 侧 `/positions`、`/closed-positions`、`/user-pnl` 等请求之间保留轻量间隔，避免批量分页时贴近官方限流。
- summary 侧 `/closed-positions` 即使配置 `page_limit=500`，官方接口也可能静默只返回约 50 行；程序会按实际返回行数继续推进 offset，直到空页或达到 `max_closed_records`，避免误把 50 条记录当成完整历史。
- `alert_score_threshold`: `40`
- `alert_score_comparison`: `>`
- `score_version`: `auto_v3`
- `min_data_quality_for_push`: `4`
- `serverchan.batch_size`: `10`，命中账号先进入 pending 队列，凑满 10 个后发送一条汇总推送。
- `serverchan.required_message_markers`: 当前 pending 告警必须包含这些消息标记才允许参与批量推送；`||` 表示新旧中文文案二选一兼容。缺少标记的旧规则 pending 会自动归档为 `archived`。

## 调优建议

- 如果 API 限流明显，降低 `max_requests_per_second` 到 `1`。
- 如果某个 leaderboard 分片连续很多页没有新增唯一账号，保持 `leaderboard_no_new_pages_stop=40` 可以避免扫到 100000 offset 但候选池不增长；设为 `0` 可关闭提前停止。
- 如果前端显示“官方榜单可见上限”明显低于 `max_rank`，说明官方接口没有暴露更深排名；此时不要继续提高 `max_rank`，应增加 shard 或接入 `12_candidate_source_expansion_plan.md` 中的市场交易/持仓候选源。
- 如果候选池扩容后 API 压力偏高，优先降低 `candidate_sources.market_discovery.limit`、`market_trades.markets_limit`、`holders.markets_limit`，不要先降低评分标准。
- 如果跳过账号太多，调高 `max_trades_per_active_day` 或 `sample_max_records`。
- 如果完整评分太慢，先降低 `candidate_pool_target` 做小规模运行。
- 如果 ServerChan 消息太多，增加 `serverchan.batch_size`、增加 `dedupe_days` 或提高 `alert_score_threshold`。
- 如果首轮 Auto V3 推送过少，先观察 `data_quality_score` 和 `copy_capacity_score` 分布，不要直接降低主分数阈值。
