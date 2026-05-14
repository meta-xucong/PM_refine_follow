# 05 Memory Model

Agent memory 建议独立于 `auto_screen` 状态库，但可以放在同一目录：

```text
auto_screen_data/agent_memory.sqlite3
```

## 表：`agent_decisions`

记录每次 AI 复核。

```sql
CREATE TABLE agent_decisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_address TEXT NOT NULL,
  final_score REAL,
  alert_grade TEXT,
  auto_action TEXT,
  agent_verdict TEXT NOT NULL,
  confidence REAL NOT NULL,
  human_review_priority INTEGER NOT NULL,
  copy_style TEXT NOT NULL,
  reasoning_json TEXT NOT NULL,
  source_analysis_path TEXT,
  model_name TEXT,
  prompt_version TEXT,
  created_at TEXT NOT NULL
);
```

## 表：`user_feedback`

记录人工反馈。

```sql
CREATE TABLE user_feedback (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_address TEXT NOT NULL,
  feedback_type TEXT NOT NULL,
  note TEXT,
  source TEXT NOT NULL,
  source_ref TEXT,
  created_at TEXT NOT NULL
);
```

允许的 `feedback_type`：

- `like`
- `dislike`
- `blacklist`
- `watch`
- `false_positive`
- `good_candidate`
- `neutral`

## 表：`candidate_snapshots`

保存关键时间点快照。

```sql
CREATE TABLE candidate_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_address TEXT NOT NULL,
  snapshot_date TEXT NOT NULL,
  final_score REAL,
  alert_grade TEXT,
  data_quality_score REAL,
  pnl_quality_score REAL,
  copy_capacity_score REAL,
  realized_pnl_7d REAL,
  realized_pnl_30d REAL,
  traded_markets INTEGER,
  positions_value REAL,
  payload_json TEXT,
  created_at TEXT NOT NULL
);
```

## 表：`followup_outcomes`

记录推送后复查结果。

```sql
CREATE TABLE followup_outcomes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_address TEXT NOT NULL,
  pushed_at TEXT,
  horizon_days INTEGER NOT NULL,
  outcome_verdict TEXT NOT NULL,
  pnl_delta REAL,
  score_delta REAL,
  false_positive_reason TEXT,
  review_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
```

允许的 `outcome_verdict`：

- `validated_good`
- `still_watchlist`
- `false_positive`
- `data_insufficient`
- `deteriorated`

## 表：`preference_profile`

保存用户偏好画像。

```sql
CREATE TABLE preference_profile (
  key TEXT PRIMARY KEY,
  value_json TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL
);
```

建议 keys：

- `preferred_sectors`
- `blocked_sectors`
- `max_avg_trades_per_day`
- `min_copy_capacity_score`
- `preferred_copy_style`
- `disliked_score_flags`
- `liked_score_flags`
- `manual_notes`

## 记忆读取原则

- 单候选复核默认读取该账号最近 180 天记录。
- Daily planner 读取最近 30 天 alerts、feedback、outcomes。
- 反馈权重高于 AI 自评。
- `blacklist` 永久生效，除非人工删除。
- `false_positive` 要进入后续 prompt 上下文。

