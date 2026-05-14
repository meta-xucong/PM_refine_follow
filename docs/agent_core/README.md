# Polymarket AI Agent 开发文档索引

本目录定义把当前 `auto_screen` 自动筛选流水线升级为“Polymarket 跟单研究 AI Agent”的开发框架。目标是让后续编码工作可以直接照文档开工，而不是重新讨论架构。

## Agent 定位

Agent 是只读研究助理，不是交易机器人。

它负责：

- 读取 `auto_screen` 产出的候选、评分、报告和运行状态。
- 对 Auto V3 结果做 AI 复核、解释、二次排序。
- 记录人工反馈，形成偏好记忆。
- 跟踪已推送账号 7d/30d 后续表现。
- 生成每日扫描计划、复查计划和候选摘要。

它不负责：

- 自动下单。
- 管理私钥。
- 绕过 Auto V3 硬风险门槛。
- 在未经确认时修改长期评分权重。

## 文档清单

| 文档 | 用途 |
|---|---|
| `01_agent_goal_and_scope.md` | Agent 目标、边界、MVP 范围 |
| `02_architecture.md` | 模块架构、数据流、与 `auto_screen` 的关系 |
| `03_code_inventory.md` | 需要新增/修改的代码文件清单 |
| `04_tool_contracts.md` | Agent tools 的输入输出契约 |
| `05_memory_model.md` | 长期记忆、反馈、复盘表结构 |
| `06_llm_io_and_prompts.md` | LLM 输入输出、JSON Schema、Prompt 使用方式 |
| `07_config_spec.md` | Agent 配置字段与默认策略 |
| `08_development_roadmap.md` | 分阶段落地计划 |
| `09_testing_acceptance.md` | 单元、集成、live smoke、验收标准 |
| `10_operations_runbook.md` | 启停、反馈导入、复查、故障处理 |
| `11_decision_policy.md` | Agent 决策规则、硬边界、人工确认点 |

## 配套材料

- 配置模板：`agent_core_config.example.json`
- Prompt 模板：
  - `prompts/candidate_review_zh.md`
  - `prompts/daily_plan_zh.md`
  - `prompts/outcome_postmortem_zh.md`
- JSON Schema：
  - `schemas/candidate_review.schema.json`
  - `schemas/daily_plan.schema.json`
  - `schemas/feedback_event.schema.json`
  - `schemas/outcome_review.schema.json`

## 第一阶段推荐目标

先做 `Agent Review MVP`：

```text
auto_screen 完整评分
  -> agent_core 读取 account_analysis.json
  -> LLM 输出结构化复核 JSON
  -> 写入 SQLite memory
  -> 更新 Excel agent 字段
  -> ServerChan 推送加入 AI 复核摘要
```

完成后，Agent 先成为“解释、排序、记忆”的研究助理。等反馈数据积累后，再进入每日规划和权重建议阶段。

## 已落地入口

- 配置模板：`agent_core_config.example.json`
- Agent CLI 状态检查：

```powershell
python -m agent_core.cli --config agent_core_config.example.json status
```

- 单账号 AI 复核 dry-run：

```powershell
python -m agent_core.cli --config agent_core_config.example.json review --analysis auto_screen_data/accounts/<account>/account_analysis.json --dry-run
```

- 单账号 AI 复核并写入 memory：

```powershell
python -m agent_core.cli --config agent_core_config.example.json review --analysis auto_screen_data/accounts/<account>/account_analysis.json
```

- 每日计划 dry-run：

```powershell
python -m agent_core.cli --config agent_core_config.example.json plan daily --dry-run
```

`auto_screen` 已支持可选 Agent 集成。默认关闭；需要开启时在 `auto_screen_config.example.json` 或运行配置中设置：

```json
{
  "agent": {
    "enabled": true,
    "config_path": "agent_core_config.example.json",
    "dry_run": false,
    "fail_open": true
  }
}
```

当前 LLM provider 默认为离线可测的 `mock` / `mock-json`，用于保证流水线、memory、schema、Excel 和 ServerChan payload 稳定。后续接真实模型时，只需要扩展 `agent_core/llm_client.py` 的 provider。
