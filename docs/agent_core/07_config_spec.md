# 07 Agent 配置规范

配置模板位于：

```text
agent_core_config.example.json
```

## 顶层字段

```json
{
  "enabled": true,
  "memory_db": "auto_screen_data/agent_memory.sqlite3",
  "prompt_dir": "docs/agent_core/prompts",
  "schema_dir": "docs/agent_core/schemas",
  "llm": {},
  "review": {},
  "feedback": {},
  "planner": {},
  "outcome_tracking": {},
  "safety": {}
}
```

## `llm`

```json
{
  "provider": "mock",
  "model": "mock-json",
  "temperature": 0.1,
  "timeout_seconds": 60,
  "max_retries": 2
}
```

说明：

- 初始实现必须支持 `mock` provider。
- 真实 provider 后续再接入，不能影响测试。

## `review`

```json
{
  "enabled": true,
  "prompt": "candidate_review_zh.md",
  "schema": "candidate_review.schema.json",
  "min_score_for_review": 35,
  "write_excel": true,
  "append_to_serverchan": true
}
```

说明：

- `min_score_for_review=35` 是为了让 35-40 的边缘账号也能被标注为 `reject/recheck_later`，但不能推送正候选。

## `feedback`

```json
{
  "enabled": true,
  "excel_import_enabled": true,
  "accepted_values": ["like", "dislike", "blacklist", "watch", "false_positive", "good_candidate", "neutral"]
}
```

## `planner`

```json
{
  "enabled": false,
  "prompt": "daily_plan_zh.md",
  "schema": "daily_plan.schema.json",
  "recent_days": 7,
  "max_recheck_accounts": 50,
  "requires_human_approval": true
}
```

第一版默认关闭 planner。Agent Review MVP 稳定后再打开。

## `outcome_tracking`

```json
{
  "enabled": false,
  "horizons_days": [7, 30],
  "prompt": "outcome_postmortem_zh.md",
  "schema": "outcome_review.schema.json"
}
```

## `safety`

```json
{
  "read_only": true,
  "forbid_trading": true,
  "require_confirmation_for_config_write": true,
  "max_accounts_per_agent_run": 100,
  "hard_block_score_flags": ["severe_risk_gate", "hft_suspected"],
  "never_promote_when_data_quality_below": 4
}
```

