# 03 代码清单

## 新增文件

```text
agent_core/
  __init__.py
  cli.py
  config.py
  models.py
  llm_client.py
  json_schema.py
  prompt_loader.py
  tools.py
  candidate_reviewer.py
  memory_store.py
  feedback.py
  daily_planner.py
  outcome_tracker.py
  digest.py
```

```text
agent_core/prompts/
  candidate_review_zh.md
  daily_plan_zh.md
  outcome_postmortem_zh.md
```

```text
agent_core/schemas/
  candidate_review.schema.json
  daily_plan.schema.json
  feedback_event.schema.json
  outcome_review.schema.json
```

```text
tests/
  test_agent_config.py
  test_agent_memory_store.py
  test_agent_schema_validation.py
  test_agent_candidate_reviewer.py
  test_agent_feedback.py
  test_agent_daily_planner.py
  test_agent_outcome_tracker.py
```

```text
agent_core_config.example.json
```

## 修改现有文件

| 文件 | 修改点 |
|---|---|
| `auto_screen/scheduler.py` | 在评分后可选调用 Agent reviewer |
| `auto_screen/excel_store.py` | 增加 agent 字段列 |
| `auto_screen/notifier.py` | 推送正文加入 Agent 摘要 |
| `auto_screen_config.example.json` | 增加 `agent.enabled`、agent 配置路径 |
| `docs/auto_screening/README.md` | 增加 Agent 文档链接 |

## 第一阶段最小代码闭环

必须先完成这些文件：

```text
agent_core/config.py
agent_core/models.py
agent_core/json_schema.py
agent_core/prompt_loader.py
agent_core/llm_client.py
agent_core/memory_store.py
agent_core/candidate_reviewer.py
agent_core/cli.py
```

必须先完成这些测试：

```text
tests/test_agent_memory_store.py
tests/test_agent_schema_validation.py
tests/test_agent_candidate_reviewer.py
```

## 复用现有代码

| 现有模块 | 复用方式 |
|---|---|
| `auto_screen/scorer.py` | 复用 analysis/report 路径和 payload |
| `auto_screen/state_store.py` | 可复用 SQLite 连接模式，但 Agent 建议独立 memory DB |
| `auto_screen/excel_store.py` | 增加 agent 字段或复用 append 逻辑 |
| `auto_screen/notifier.py` | 增加 AI 摘要字段 |
| `skill/.../analyze_account.py` | 不改评分主逻辑，只消费输出 |

