# 08 开发路线图

## Phase 0: 文档与材料冻结

交付物：

- `docs/agent_core/` 文档包。
- Prompt 模板。
- JSON Schema。
- `agent_core_config.example.json`。

完成标准：

- 后续实现者可以直接按文档创建 `agent_core/`。
- MVP 边界清晰。

## Phase 1: Agent 工程骨架

交付物：

- `agent_core/` 包。
- `config.py`
- `models.py`
- `json_schema.py`
- `prompt_loader.py`
- `llm_client.py`
- `cli.py`

完成标准：

- `python -m agent_core.cli --config agent_core_config.example.json status` 可运行。
- mock LLM 可返回固定 JSON。
- schema 文件能被加载并校验。

## Phase 2: Memory Store

交付物：

- `memory_store.py`
- `agent_decisions`
- `user_feedback`
- `candidate_snapshots`
- `followup_outcomes`
- `preference_profile`

完成标准：

- 单元测试覆盖建表、写入、查询、重复反馈处理。
- 不污染 `auto_screen` 运行状态库。

## Phase 3: Candidate Review MVP

交付物：

- `candidate_reviewer.py`
- `tools.load_candidate_analysis`
- `tools.load_recent_memory`
- `tools.write_agent_review`
- `candidate_review_zh.md`
- `candidate_review.schema.json`

完成标准：

- 可对一个已有 `account_analysis.json` 生成结构化 AI 复核。
- 输出通过 schema。
- 硬边界修正生效。
- 复核写入 memory。

## Phase 4: auto_screen 集成

交付物：

- `auto_screen/scheduler.py` 可选调用 Agent reviewer。
- `auto_screen/notifier.py` 推送正文加入 Agent 摘要。
- `auto_screen/excel_store.py` 增加 Agent 字段。

完成标准：

- `python -m auto_screen.cli ... --dry-run-alerts` 能产出 Agent review。
- Excel 里可看到 `agent_verdict`、`agent_confidence`、`agent_reason`。
- ServerChan dry-run payload 包含 AI 摘要。

## Phase 5: Feedback 导入

交付物：

- `feedback.py`
- CLI: `python -m agent_core.cli feedback import-excel`
- `feedback_event.schema.json`

完成标准：

- 能从 Excel sidecar 或指定 CSV/JSON 导入反馈。
- `blacklist`、`false_positive` 能在后续 review 上下文出现。

## Phase 6: Daily Planner

交付物：

- `daily_planner.py`
- `daily_plan_zh.md`
- `daily_plan.schema.json`

完成标准：

- 生成每日扫描/复查建议。
- 计划默认只输出，不自动改配置。
- 若要写配置，必须人工确认。

## Phase 7: Outcome Tracker

交付物：

- `outcome_tracker.py`
- `outcome_postmortem_zh.md`
- `outcome_review.schema.json`

完成标准：

- 对已推送账号按 7d/30d 复查。
- 写入 `followup_outcomes`。
- 能识别 `validated_good` 和 `false_positive`。

## Phase 8: 稳定化

交付物：

- 全量测试。
- live smoke。
- 运维文档更新。
- 失败恢复策略。

完成标准：

- Agent review 不影响原有 auto_screen 稳定运行。
- LLM 失败时降级为规则推送。
- 所有 Agent 输出可追溯到 prompt/version/schema/model。

