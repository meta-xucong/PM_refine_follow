# 06 LLM 输入输出与 Prompt

## 设计原则

- LLM 只输出结构化 JSON。
- JSON 必须通过 schema 校验。
- 业务代码必须应用硬边界修正。
- Prompt 版本号写入 memory，方便复盘。
- mock LLM 必须能跑完整测试。

## Candidate Review 输入

建议上下文：

```json
{
  "account": {
    "address": "0x...",
    "label": "...",
    "analysis_window": "..."
  },
  "auto_v3": {
    "final_score": 42.52,
    "decision": "selective_copying_only",
    "alert_grade": "C",
    "auto_action": "push_watchlist",
    "data_quality_score": 9,
    "pnl_quality_score": 13.32,
    "copy_capacity_score": 5,
    "score_flags": ["caution_risk_gate"]
  },
  "metrics": {},
  "pnl_curve": {},
  "keyword_profile": {},
  "memory": {
    "previous_reviews": [],
    "user_feedback": [],
    "followup_outcomes": []
  },
  "preference_profile": {}
}
```

输出必须匹配：

```text
schemas/candidate_review.schema.json
```

## Daily Plan 输入

```json
{
  "date": "2026-05-14",
  "recent_cycle_summary": {},
  "recent_feedback": [],
  "recent_outcomes": [],
  "deferred_accounts": [],
  "system_limits": {
    "max_rank": 100000,
    "max_process_accounts": 100,
    "allowed_shards": ["month_pnl", "month_vol", "week_pnl", "week_vol"]
  }
}
```

输出必须匹配：

```text
schemas/daily_plan.schema.json
```

## Outcome Review 输入

```json
{
  "account_address": "0x...",
  "original_review": {},
  "original_analysis": {},
  "fresh_analysis": {},
  "horizon_days": 7
}
```

输出必须匹配：

```text
schemas/outcome_review.schema.json
```

## Prompt 模板

Prompt 文件在：

```text
docs/agent_core/prompts/
```

落地代码时建议复制或引用到：

```text
agent_core/prompts/
```

## LLM Provider 抽象

建议接口：

```python
class LlmClient:
    def complete_json(
        self,
        *,
        prompt_name: str,
        system_prompt: str,
        user_payload: dict,
        schema: dict,
        temperature: float = 0.1,
    ) -> dict:
        ...
```

测试必须提供：

```python
class MockLlmClient:
    def __init__(self, response: dict): ...
```

## 输出修正规则

LLM 输出后，程序必须二次修正：

- `final_score <= 40` 且 `agent_verdict=strong_candidate` -> 改为 `watchlist` 或 `reject`。
- `auto_action=skip` -> 改为 `reject`。
- `data_quality_score < 4` -> 改为 `recheck_later`。
- `severe_risk_gate` -> 不允许 `strong_candidate`。
- `confidence` 超出 `0..1` 必须 clamp。
- `human_review_priority` 超出 `1..5` 必须 clamp。

