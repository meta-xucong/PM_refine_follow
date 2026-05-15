# Polymarket 自动筛选系统开发文档索引

本目录是“定时/常驻扫描 Polymarket 高表现、高活跃账号，并自动筛出适合跟单目标”的开工前文档包。

目标不是新增交易功能，而是构建一个只读筛选服务：持续访问 Polymarket 官方公开 Data API，生成候选池，预筛高频或低价值账号，复用当前仓库的锚点评分模型，发现 `final_score > 50` 的账号后推送 ServerChan 并写入 Excel。

## 文档清单

| 文档 | 用途 |
|---|---|
| `01_product_requirements.md` | 产品目标、范围、默认策略、非目标 |
| `02_technical_architecture.md` | 系统架构、运行流程、模块边界 |
| `03_api_and_data_sources.md` | 官方 API、外部仓库可复用逻辑、API 限制 |
| `04_data_model_and_storage.md` | SQLite 状态库、Excel 输出、文件缓存结构 |
| `05_code_inventory.md` | 待新增代码清单、复用代码清单、模块职责 |
| `06_config_spec.md` | 配置文件字段、默认值、调优口径 |
| `07_development_roadmap.md` | 分阶段开发计划和交付物 |
| `08_testing_acceptance.md` | 测试计划、验收标准、首轮试运行标准 |
| `09_operations_runbook.md` | 启停、恢复、日志、告警和日常运维 |
| `10_scoring_review_and_optimization.md` | 当前评分机制评估、标准总结、优化方向 |
| `11_scoring_v3_target_spec.md` | Auto V3 目标评分机制规格，程序和 skill 落地时按此实现 |

## 核心决策

- 候选来源采用多 shard 发现，而不是单一 `MONTH + PNL + OVERALL` 月榜。
- 单 shard 官方 leaderboard 当前无法可靠暴露完整前 10 万名，因此系统目标定义为“从官方 leaderboard 多周期、多分类、多排序 shard 中发现最多 10 万个近期优秀且活跃的唯一账号”。
- 初版严格只读 Data API，不接 CLOB 交易端点。
- 初版评分通过 subprocess 复用现有 `analyze_account.py`，降低评分漂移风险。
- SQLite 是运行状态源，Excel 是人工查看表。
- 推送阈值为严格 `final_score > 50`。
- ServerChan 默认批量推送：命中候选先写入 SQLite/Excel，待 `serverchan.batch_size=10` 个 pending 告警凑满后发送一条汇总推送，避免单账号刷屏。评分/消息结构升级后，缺少当前要求字段的旧 pending 告警会自动归档，不和新规则候选混批。
- 从排行榜开头重新扫描时，若地址曾经出现过，会在候选池标记为 `refresh_score`，并在上下文和前端提示“刷新分数”；它仍会进入待处理队列，用新数据刷新评分。
- 常驻 `run` 采用“大周期 + 小批次”模式：每个大周期先扫描候选池，然后按 `process_batch_size` 分批处理，直到本轮 pending 候选处理完，才休眠并从排行榜开头开启下一大周期。`process_batch_size=25` 只是每个内部批次大小，不是一整轮上限。

## 已落地入口

- 配置模板：`auto_screen_config.example.json`
- 自动扫描 CLI：`python -m auto_screen.cli --config auto_screen_config.example.json status`
- 单轮扫描 + 浅预筛：`python -m auto_screen.cli --config auto_screen_config.example.json once --limit-candidates 10 --process-limit 10 --prefilter-only --dry-run-alerts`
- 单轮完整 dry-run：`python -m auto_screen.cli --config auto_screen_config.example.json once --limit-candidates 1 --process-limit 1 --dry-run-alerts`
- 常驻运行：`python -m auto_screen.cli --config auto_screen_config.example.json run`

运行产物默认写入 `auto_screen_data/`：SQLite 状态库、Excel 表、账户 activity CSV、summary JSON、analysis JSON 和中英文报告。该目录已加入 `.gitignore`。

Skill 默认评分版本已切换为 `auto_v3`，旧版可通过 `--score-version v2_2` 保留兼容。

## 相关背景文档

- `docs/AUTO_LEADERBOARD_SCREENING_DESIGN.md`
- `docs/CLOB_V2_MIGRATION_ASSESSMENT.md`
- `docs/CLOB_V2_EXECUTION_PLAN.md`
- `docs/agent_core/README.md`
