# 05 代码清单与模块职责

## 新增代码清单

```text
auto_screen/
  __init__.py
  cli.py
  config.py
  data_api.py
  models.py
  state_store.py
  leaderboard_scanner.py
  prefilter.py
  collector.py
  scoring_features.py
  scorer.py
  notifier.py
  excel_store.py
  scheduler.py
  logging_utils.py
```

```text
tests/
  test_auto_screen_config.py
  test_auto_screen_state_store.py
  test_auto_screen_leaderboard_scanner.py
  test_auto_screen_prefilter.py
  test_auto_screen_excel_store.py
  test_auto_screen_notifier.py
  test_auto_screen_scheduler.py
```

```text
windows/
  start_auto_screen.ps1
  status_auto_screen.ps1
  stop_auto_screen.ps1
```

```text
auto_screen_config.example.json
```

## 复用代码清单

本仓库：

| 文件 | 复用方式 |
|---|---|
| `pull_polymarket_trades_to_csv.py` | 抽取单账号 activity 拉取逻辑，或初版包装调用 |
| `skill/polymarket-account-review-skill/scripts/fetch_polymarket_summary.py` | 直接 import 或 subprocess 调用，生成 summary JSON |
| `skill/polymarket-account-review-skill/scripts/analyze_account.py` | 初版 subprocess 调用，保持评分一致 |
| `skill/polymarket-account-review-skill/scripts/render_report.py` | 生成中英文报告 |
| `skill/polymarket-account-review-skill/baseline/baseline_anchor.json` | 60 分锚点 |

参考仓库：

| 文件 | 复用方式 |
|---|---|
| `F:\AI\copytrade_v5_muti-clob-v2\smartmoney_query\poly_martmoney_query\api_client.py` | 移植 Data API 客户端、限速、重试、leaderboard、activity 逻辑 |
| `F:\AI\copytrade_v5_muti-clob-v2\smartmoney_query\poly_martmoney_query\models.py` | 参考标准化数据模型 |
| `F:\AI\copytrade_v5_muti-clob-v2\smartmoney_query\poly_martmoney_query\processors.py` | 参考统计与汇总逻辑 |

## 模块职责

### `models.py`

数据结构：

- `LeaderboardShard`
- `AccountCandidate`
- `PrefilterResult`
- `CollectionResult`
- `ScoreResult`
- `AlertPayload`
- `CycleSummary`

### `data_api.py`

职责：

- 统一 HTTP 请求。
- 统一 rate limit。
- 统一 backoff。
- 封装公开 Data API。

### `leaderboard_scanner.py`

职责：

- 扫描 shard。
- 合并候选。
- 检测 API cap。
- 计算优先级。

### `prefilter.py`

职责：

- 根据 leaderboard 信号和浅层 activity 做早停。
- 输出可解释跳过原因。

### `collector.py`

职责：

- 拉完整 activity CSV。
- 拉 account summary。
- 管理账号缓存目录。

### `scorer.py`

职责：

- 调用评分脚本。
- 调用报告渲染脚本。
- 解析核心指标。
- 接收 Auto V3 评分结果，包括 `final_score`、`alert_grade`、`auto_action`。

### `scoring_features.py`

职责：

- 从 leaderboard、activity、summary 中构建 Auto V3 新特征。
- 生成 `discovery_score`、leaderboard consistency、data quality、copy capacity 所需输入。
- 将自动筛选系统的上下文传给 skill 评分器。

### `notifier.py`

职责：

- 生成 ServerChan 标题和正文。
- 生成 `serverchan.batch_size` 个候选组成的批量汇总正文。
- 按 Auto V3 `alert_grade` 使用不同标题和正文强度。
- 发送推送。
- 返回可持久化结果。

### `excel_store.py`

职责：

- 初始化 workbook。
- 追加 `alerts`、`all_scored`、`skipped`、`cycles`。
- 保证列稳定。

### `scheduler.py`

职责：

- 常驻循环。
- 恢复未完成状态。
- 控制每轮 lifecycle。
- 写 heartbeat。
- 命中候选先写入告警队列，pending 达到批量阈值后再触发 ServerChan。
