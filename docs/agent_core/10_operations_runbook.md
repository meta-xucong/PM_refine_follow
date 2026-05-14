# 10 Agent 运维手册

## 查看状态

```powershell
python -m agent_core.cli --config agent_core_config.example.json status
```

输出应包含：

- memory DB 路径。
- agent decisions 数量。
- feedback 数量。
- due followups 数量。
- 最近一次 review 时间。

## 单账号复核

dry-run：

```powershell
python -m agent_core.cli --config agent_core_config.example.json review --analysis auto_screen_data/accounts/<account>/account_analysis.json --dry-run
```

写入 memory：

```powershell
python -m agent_core.cli --config agent_core_config.example.json review --analysis auto_screen_data/accounts/<account>/account_analysis.json
```

## 导入人工反馈

```powershell
python -m agent_core.cli --config agent_core_config.example.json feedback import-json --path feedback.json
```

后续可增加：

```powershell
python -m agent_core.cli --config agent_core_config.example.json feedback import-excel --path auto_screen_data/polymarket_candidates.xlsx
```

## 生成每日计划

```powershell
python -m agent_core.cli --config agent_core_config.example.json plan daily --dry-run
```

默认只打印建议，不写配置。

## 运行复查

```powershell
python -m agent_core.cli --config agent_core_config.example.json outcome due --dry-run
```

## 故障处理

### LLM 调用失败

处理：

- 记录 `agent_review_failed`。
- auto_screen 继续按 Auto V3 推送。
- 下轮可重试。

### Schema 校验失败

处理：

- 保存原始 LLM 输出到 debug log。
- 不写入正式 `agent_decisions`。
- 使用 fallback review：
  - `agent_verdict=watchlist` if `final_score > 40`
  - `agent_verdict=reject` otherwise

### Memory DB 损坏

处理：

- 停止 agent。
- 备份损坏文件。
- 从 `auto_screen_data` 历史 JSON 和 Excel sidecar 重建基础 memory。

### 人工反馈冲突

规则：

- `blacklist` 优先级最高。
- 最新 `good_candidate` 可以覆盖旧 `watch`，但不能覆盖 `blacklist`。
- 冲突保留所有记录，偏好画像按最新有效记录计算。

