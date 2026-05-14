# 07 开发路线图

## Phase 0: 文档冻结

交付物：

- 产品需求文档
- 技术架构文档
- API 与数据源文档
- 状态库设计
- 代码清单
- 配置规范
- 测试验收文档
- 运维手册
- Auto V3 目标评分机制规格

完成标准：

- 所有关键默认策略明确。
- 无待定阻塞项。

## Phase 1: 工程骨架

交付物：

- `auto_screen/` 包
- `auto_screen_config.example.json`
- CLI 基础命令
- 日志初始化

完成标准：

- `python -m auto_screen.cli status --config auto_screen_config.example.json` 可运行。
- 配置校验覆盖核心字段。

## Phase 2: SQLite 状态库

交付物：

- schema 初始化
- cycle 管理
- candidate upsert
- account run 状态更新
- alert 记录

完成标准：

- 单元测试覆盖 schema、upsert、resume。
- 可从中断状态恢复。

## Phase 3: Leaderboard 多 shard 扫描

交付物：

- Data API 客户端
- shard 生成
- API cap 检测
- 候选合并
- 优先级排序

完成标准：

- mock 测试覆盖 rank cap 和重复页。
- live smoke 可扫描前 100 个候选。

## Phase 4: 预筛

交付物：

- 7 天浅层 activity 拉取
- 高频判断
- 低信号判断
- 跳过结果入库和 Excel

完成标准：

- mock HFT 测试通过。
- live smoke 能产生 `passed` 和 `skipped` 结果。

## Phase 5: 完整取数

交付物：

- 单账号 activity CSV 拉取
- account summary JSON 拉取
- 缓存目录管理

完成标准：

- 对 1 到 3 个 live 账号可完整产出 `activity.csv` 和 `account_summary.json`。
- 请求失败能进入 retryable 状态。

## Phase 6: Auto V3 评分与报告

交付物：

- 修复 recent PnL 拉取方向和 coverage 标记
- `data_quality_score`
- `pnl_quality_score`
- `copy_capacity_score`
- `automation_risk_penalty`
- `alert_grade`
- `auto_action`
- `baseline_anchor_auto_v3.json`
- subprocess 调用 `analyze_account.py`
- subprocess 调用 `render_report.py`
- 解析 `account_analysis.json`
- 写入 `all_scored`

完成标准：

- live 账号可完整评分。
- Auto V3 输出字段完整。
- V2.2 旧字段仍兼容。
- 新锚点账号按 Auto V3 校准到 60 分。
- recent 7d/30d PnL 不会被早期 closed-positions 截断。

## Phase 7: 推送与 Excel

交付物：

- ServerChan 推送
- Excel 四个 sheet
- 推送去重
- 按 `alert_grade` 分级推送

完成标准：

- dry-run 推送可打印 payload。
- 真推送可记录结果。
- Excel 可打开且列稳定。
- Excel 包含 Auto V3 新字段。

## Phase 8: 常驻运行硬化

交付物：

- `run` 常驻模式
- heartbeat
- retry budget
- cycle reset
- Windows 启停脚本

完成标准：

- 小规模 `candidate_pool_target=50` 连续跑完一轮。
- 重启后能续跑或开启下一轮。
