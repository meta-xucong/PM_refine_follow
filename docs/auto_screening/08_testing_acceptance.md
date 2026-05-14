# 08 测试与验收标准

## 单元测试

必须覆盖：

- 配置读取和默认值。
- SQLite schema 初始化。
- candidate upsert 和 dedupe。
- leaderboard shard 生成。
- API cap 检测。
- candidate priority 计算。
- prefilter 高频跳过。
- scorer 解析 `account_analysis.json`。
- Auto V3 data quality caps。
- Auto V3 high-frequency caps。
- Auto V3 alert grade 上限。
- Auto V3 anchor 文件字段。
- ServerChan payload 格式。
- Excel sheet 初始化和追加。

## Mock 集成测试

场景：

1. 正常账号
   - leaderboard 返回候选。
   - prefilter 通过。
   - collector 产出文件。
   - scorer 返回 `final_score=45`。
   - notifier 和 Excel 记录成功。
   - Auto V3 字段完整。

2. 高频账号
   - prefilter 浅层 activity 达到 cap。
   - 不进入完整取数。
   - 写入 `skipped`。

3. leaderboard cap
   - offset 增长但 rank 不再增长。
   - shard 标记 `capped`。
   - scheduler 进入下一个 shard。

4. API 429/5xx
   - 请求重试。
   - 超过 retry 后进入 retryable 状态。

5. 进程重启
   - 已完成账号不重复处理。
   - 未完成账号可恢复。

6. PnL 截断防护
   - mock 超过 5000 条 closed positions。
   - 最近 7d/30d 仍能被正确覆盖。
   - coverage 不足时 `data_quality_score` 和 PnL confidence 降级。

## Live Smoke 测试

第一轮真实环境只跑小规模：

```powershell
python -m auto_screen.cli once --config auto_screen_config.json --limit-candidates 10 --dry-run-alerts
```

验收：

- 能扫描 leaderboard。
- 能至少预筛 10 个候选。
- 能完整评分 1 到 3 个正常账号。
- 能写 SQLite。
- 能写 Excel。
- dry-run ServerChan payload 正常。
- Auto V3 的 `alert_grade`、`auto_action`、`data_quality_score` 正常。

第二轮扩大：

```powershell
python -m auto_screen.cli once --config auto_screen_config.json --limit-candidates 50
```

验收：

- 不崩溃。
- 跳过原因可解释。
- 评分结果有报告路径。
- Excel 可打开。

## 正式验收标准

1. 功能验收
   - 可常驻运行。
   - 可多 shard 构建候选池。
   - 可预筛高频账号。
   - 可完整取数和评分。
   - `final_score > 40` 可推送并写 Excel。
   - 推送按 A/B/C 分级。
   - 扫完一轮可自动重启下一轮。

2. 数据验收
   - SQLite 中候选、运行、推送状态完整。
   - Excel 四个 sheet 均可读。
   - 报告文件存在且可打开。
   - `baseline_anchor_auto_v3.json` 存在并可复算标杆 60 分。

3. 稳定性验收
   - 断网或 429 不导致进程退出。
   - 单账号失败不影响后续账号。
   - 进程重启不重复大量处理已完成账号。

4. 安全验收
   - 不读取私钥。
   - 不调用交易接口。
   - 不输出完整 ServerChan SendKey。
