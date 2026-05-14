# 02 技术架构

## 总体架构

新增一个 `auto_screen` 包，作为常驻扫描服务。它只调用公开 Data API，并复用现有评分脚本。

```text
auto_screen CLI
  -> scheduler
  -> leaderboard_scanner
  -> state_store
  -> prefilter
  -> collector
  -> scorer
  -> excel_store
  -> notifier
```

## 运行流程

1. 启动 CLI。
2. 读取配置。
3. 初始化 SQLite 和运行目录。
4. 创建或恢复当前 scan cycle。
5. 扫描 leaderboard shards，写入候选池。
6. 对候选池按优先级排序。
7. 逐账号预筛。
8. 通过预筛后完整取数。
9. 调用现有评分脚本。
10. 写入 SQLite 和 Excel。
11. 高分账号推送 ServerChan。
12. 当前候选池处理完后进入下一轮。

常驻运行必须区分“大周期”和“小批次”：`max_rank` 控制大周期扫描上限，`process_batch_size` 只控制每次从 pending 队列取多少个地址处理。小批次处理完后继续取下一批，直到本轮 pending 队列为空；只有此时才标记 cycle 完成、进入休眠并从排行榜开头开始下一大周期。

## 模块边界

### `config.py`

- 读取 `auto_screen_config.json`。
- 提供默认值。
- 校验字段范围。
- 将相对路径解析到仓库根目录。

### `data_api.py`

- 复用或移植 `F:\AI\copytrade_v5_muti-clob-v2\smartmoney_query\poly_martmoney_query\api_client.py` 的请求逻辑。
- 支持 leaderboard、activity、positions、closed-positions。
- 全局限速、429/5xx 重试、`Retry-After`、抖动回退。

### `leaderboard_scanner.py`

- 扫描多 shard。
- 检测 API cap。
- 生成候选账号。
- 合并同一钱包在多个 shard 的信息。
- 计算候选优先级。

### `state_store.py`

- 管理 SQLite schema。
- 提供 cycle、candidate、run、alert 的读写。
- 支持断点恢复和去重。

### `prefilter.py`

- 做轻量检查。
- 标记明显高频、低信号、数据过深账号。
- 输出可审计的跳过原因。

### `collector.py`

- 为单账号生成完整 activity CSV。
- 生成 `account_summary.json`。
- 管理 per-account 缓存目录。

### `scorer.py`

- 初版通过 subprocess 调用：
  - `analyze_account.py`
  - `render_report.py`
- 解析 `account_analysis.json`。
- 归一化结果给 SQLite、Excel 和 ServerChan。

### `excel_store.py`

- 用 `openpyxl` 维护 `polymarket_auto_screen.xlsx`。
- 写入 `alerts`、`all_scored`、`skipped`、`cycles`。

### `notifier.py`

- 读取 ServerChan SendKey。
- 格式化高分账号通知。
- 保存推送结果。

### `scheduler.py`

- 常驻循环。
- 控制 cycle 生命周期。
- 管理 sleep、重试、heartbeat。

### `cli.py`

建议命令：

```powershell
python -m auto_screen.cli run --config auto_screen_config.json
python -m auto_screen.cli once --config auto_screen_config.json --limit-candidates 50
python -m auto_screen.cli status --config auto_screen_config.json
python -m auto_screen.cli export --config auto_screen_config.json
```

## 初版集成方式

初版优先 subprocess 复用现有脚本，不直接改评分核心：

```text
collector -> activity.csv + account_summary.json
scorer -> analyze_account.py -> account_analysis.json
scorer -> render_report.py -> report_zh.md/report_en.md
```

优点：

- 风险低。
- 不改变现有评分结果。
- 方便和已有批处理产物对比。

第二阶段再把评分函数整理成可 import API。
