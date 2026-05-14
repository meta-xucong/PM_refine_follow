# 02 Agent 架构

## 总体架构

```text
auto_screen
  Data API -> leaderboard -> prefilter -> collection -> Auto V3 -> report/excel/push

agent_core
  observe -> candidate review -> memory -> feedback -> planning -> outcome tracking
```

`auto_screen` 继续负责确定性数据工程和硬评分。`agent_core` 负责解释、复核、记忆和计划。

## 推荐目录

```text
agent_core/
  __init__.py
  cli.py
  config.py
  models.py
  llm_client.py
  json_schema.py
  tools.py
  candidate_reviewer.py
  memory_store.py
  feedback.py
  daily_planner.py
  outcome_tracker.py
  digest.py
  prompt_loader.py
  prompts/
    candidate_review_zh.md
    daily_plan_zh.md
    outcome_postmortem_zh.md
  schemas/
    candidate_review.schema.json
    daily_plan.schema.json
    feedback_event.schema.json
    outcome_review.schema.json
```

## 数据流

### 单候选复核

```text
account_analysis.json
leaderboard_context.json
existing memory
user preference profile
        |
        v
candidate_reviewer.review_candidate()
        |
        v
candidate_review JSON
        |
        +--> memory_store.agent_decisions
        +--> Excel all_scored agent columns
        +--> ServerChan message summary
```

### 人工反馈

```text
Excel human_feedback / CLI feedback
        |
        v
feedback.import_feedback()
        |
        v
memory_store.user_feedback
        |
        v
preference_profile refresh
```

### 每日计划

```text
recent cycles + alerts + feedback + deferred accounts + outcomes
        |
        v
daily_planner.build_plan()
        |
        v
daily_plan JSON
        |
        +--> recommended scan shards
        +--> recheck account list
        +--> temporary thresholds
```

### 结果追踪

```text
alerts pushed at T0
        |
        v
outcome_tracker due at T+7/T+30
        |
        v
collect fresh summary/activity
        |
        v
outcome_review JSON
        |
        +--> followup_outcomes
        +--> false positive learning
```

## 模块职责

### `llm_client.py`

- 封装模型调用。
- 支持 dry-run 和 mock。
- 不在业务代码中散落 prompt 拼接。
- 所有输出必须过 JSON Schema 校验。

### `tools.py`

把现有程序能力封装为 Agent tools：

- `load_candidate_analysis`
- `load_recent_memory`
- `write_agent_review`
- `update_excel_agent_fields`
- `send_agent_alert`
- `list_recheck_due_accounts`
- `collect_outcome_snapshot`

### `candidate_reviewer.py`

- 构建候选复核上下文。
- 调用 LLM。
- 校验输出。
- 应用硬边界修正。
- 写入 memory。

### `memory_store.py`

- 建表和迁移。
- 写入 AI 决策。
- 写入人工反馈。
- 查询历史候选。
- 查询偏好画像。

### `daily_planner.py`

- 汇总最近运行结果。
- 读取人工反馈。
- 输出每日扫描和复查计划。
- 计划仅作为建议，实际执行仍由程序校验。

### `outcome_tracker.py`

- 找到已推送且到期复查的账号。
- 拉新数据。
- 生成 outcome review。
- 标注 false positive / good candidate。

