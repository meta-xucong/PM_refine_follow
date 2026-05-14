# 11 Agent 决策策略

## 输出标签

`agent_verdict`：

- `strong_candidate`
- `watchlist`
- `reject`
- `recheck_later`

`copy_style`：

- `broad`
- `selective`
- `event_filtered`
- `manual_only`
- `none`

## 基础映射

| Auto V3 条件 | Agent 默认倾向 |
|---|---|
| `alert_grade=A` 且无硬风险 | `strong_candidate` |
| `alert_grade=B` | `watchlist` 或 `strong_candidate` |
| `alert_grade=C` | `watchlist` |
| `final_score <= 40` | `reject` |
| `data_quality_score < 4` | `recheck_later` |
| `auto_action=skip` | `reject` |

## 硬阻断

出现以下任一情况，Agent 不能输出 `strong_candidate`：

- `final_score < 65`
- `data_quality_score < 7`
- `score_flags` 包含 `severe_risk_gate`
- `score_flags` 包含 `hft_suspected`
- `auto_action=skip`
- 用户反馈存在 `blacklist`

出现以下任一情况，Agent 不能输出 `watchlist` 以上：

- `data_quality_score < 4`
- `final_score <= 40`
- 当前账号被人工 blacklist

## 优先人工复核等级

`human_review_priority` 范围 `1..5`：

- `1`: 立即看，强候选。
- `2`: 今日重点。
- `3`: 普通观察。
- `4`: 低优先级复查。
- `5`: 不建议看。

默认规则：

- A: `1`
- B: `2`
- C: `3`
- recheck_later: `4`
- reject: `5`

## 用户偏好优先级

优先级从高到低：

1. 人工 blacklist。
2. 人工 good_candidate / false_positive。
3. 后续 outcome 结果。
4. Auto V3 硬指标。
5. LLM 自己的语义解释。

## 配置修改策略

Agent 可以建议：

- 临时调低处理批量。
- 增加复查账号。
- 调整今日 shard 优先级。
- 提醒某类账号假阳性偏多。

Agent 不可以直接执行：

- 长期修改 Auto V3 权重。
- 长期修改 `max_rank`。
- 关闭 high-frequency cap。
- 降低 data-quality 推送门槛。

这些动作必须输出为 `requires_human_approval=true` 的 plan。

