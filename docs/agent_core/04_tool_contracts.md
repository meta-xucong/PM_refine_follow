# 04 Agent Tool 契约

Agent 的工具必须是确定性的 Python 函数，不让 LLM 自由执行 shell。LLM 只能提出结构化请求，程序根据白名单执行。

## Tool: `load_candidate_analysis`

输入：

```json
{
  "account_address": "0x...",
  "analysis_path": "auto_screen_data/accounts/0x.../account_analysis.json"
}
```

输出：

```json
{
  "analysis": {},
  "exists": true,
  "error": null
}
```

要求：

- 校验地址一致。
- 缺字段时补默认值。
- 不抛出裸异常给 LLM。

## Tool: `load_recent_memory`

输入：

```json
{
  "account_address": "0x...",
  "lookback_days": 90
}
```

输出：

```json
{
  "previous_reviews": [],
  "user_feedback": [],
  "followup_outcomes": [],
  "preference_hits": []
}
```

## Tool: `review_candidate`

输入：

```json
{
  "analysis": {},
  "memory": {},
  "preference_profile": {}
}
```

输出必须匹配：

```text
docs/agent_core/schemas/candidate_review.schema.json
```

硬边界：

- 如果 `final_score <= 40`，不能输出 `strong_candidate`。
- 如果 `auto_action=skip`，只能输出 `reject` 或 `recheck_later`。
- 如果 `data_quality_score < 4`，只能输出 `recheck_later` 或 `reject`。
- 如果 `score_flags` 包含 `severe_risk_gate`，不能输出 `strong_candidate`。

## Tool: `write_agent_review`

输入：

```json
{
  "account_address": "0x...",
  "review": {},
  "source_analysis_path": "..."
}
```

输出：

```json
{
  "stored": true,
  "decision_id": 123
}
```

## Tool: `update_excel_agent_fields`

输入：

```json
{
  "account_address": "0x...",
  "review": {}
}
```

输出：

```json
{
  "updated": true,
  "excel_path": "auto_screen_data/polymarket_candidates.xlsx"
}
```

## Tool: `send_agent_alert`

输入：

```json
{
  "analysis": {},
  "review": {},
  "dry_run": true
}
```

输出：

```json
{
  "sent": false,
  "reason": "dry_run",
  "title": "...",
  "message": "..."
}
```

要求：

- 使用现有 ServerChan 配置。
- 不打印完整 SendKey。
- AI 摘要只能作为解释，不能覆盖 Auto V3 硬结论。

## Tool: `import_feedback`

输入：

```json
{
  "source": "excel",
  "path": "auto_screen_data/polymarket_candidates.xlsx"
}
```

输出：

```json
{
  "imported": 12,
  "ignored": 3,
  "errors": []
}
```

反馈项必须匹配 `feedback_event.schema.json`。

## Tool: `build_daily_plan`

输入：

```json
{
  "date": "2026-05-14",
  "recent_days": 7
}
```

输出必须匹配 `daily_plan.schema.json`。

计划执行前必须由程序二次校验：

- shard 白名单。
- 阈值上下限。
- 最大处理账号数。
- 是否需要人工确认。

