# 09 测试与验收标准

## 单元测试

必须覆盖：

- 配置加载与默认值合并。
- Prompt 文件加载。
- JSON Schema 加载和校验。
- Mock LLM 调用。
- Candidate review 输出修正。
- Memory 建表、写入、查询。
- Feedback schema 校验。
- Planner schema 校验。
- Outcome schema 校验。

## Mock 集成测试

### 场景 1: 正常候选复核

输入：

- `final_score=66`
- `alert_grade=B`
- `data_quality_score=8`
- mock LLM 输出 `watchlist`

验收：

- review JSON 通过 schema。
- memory 写入 1 条 `agent_decisions`。
- Excel agent 字段可更新。

### 场景 2: LLM 试图越权

输入：

- `final_score=31`
- LLM 输出 `strong_candidate`

验收：

- 程序修正为 `reject` 或 `recheck_later`。
- `safety_overrides` 记录原因。

### 场景 3: Data quality 不足

输入：

- `data_quality_score=3`
- LLM 输出 `watchlist`

验收：

- 输出改为 `recheck_later`。
- 不推送正候选。

### 场景 4: 高频账号

输入：

- `auto_action=skip`
- `score_flags=["hft_suspected"]`

验收：

- 输出只能是 `reject`。
- memory 记录 hard block。

### 场景 5: 人工反馈导入

输入：

- feedback JSON/CSV/Excel sidecar 含 `blacklist`

验收：

- 写入 `user_feedback`。
- 下一次 review 上下文包含 blacklist。

## Live Smoke

第一轮：

```powershell
python -m agent_core.cli --config agent_core_config.example.json review --analysis auto_screen_data/accounts/<account>/account_analysis.json --dry-run
```

验收：

- 输出结构化 review。
- 不写数据库。
- 不发推送。

第二轮：

```powershell
python -m agent_core.cli --config agent_core_config.example.json review --analysis auto_screen_data/accounts/<account>/account_analysis.json
```

验收：

- 写入 memory。
- 可查询该账号历史 review。

第三轮：

```powershell
python -m auto_screen.cli --config auto_screen_config.example.json once --limit-candidates 1 --process-limit 1 --dry-run-alerts
```

验收：

- auto_screen 完整跑通。
- Agent review 被自动调用。
- ServerChan dry-run payload 包含 Agent 摘要。

## 正式验收

- 原有 `pytest -q` 通过。
- 新增 Agent tests 全部通过。
- `python -m compileall -q auto_screen agent_core tests` 通过。
- LLM provider 为 mock 时完全离线可测。
- LLM provider 失败时，auto_screen 不失败，只记录 `agent_review_failed`。
- Agent 不调用交易接口。
- Agent 不写长期配置，除非显式命令确认。

