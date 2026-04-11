---
name: polymarket-account-review
description: 自动执行 Polymarket V2.2 多账户筛选：读取 CSV、补齐官方 API 汇总、按锚点基线评分、输出中英文报告与总表。
---

# Polymarket 账户筛选 Skill（中文说明）

## 默认执行方式（无需手动逐步跑脚本）

触发 skill 后，直接执行一体化流程：

```bash
python scripts/run_full_screening.py \
  --csv <交易CSV> \
  --output-dir <输出目录> \
  --summary-dir <可选预拉取summary目录>
```

## 核心机制

- 支持多账户输入（自动发现 `account_address`）
- 评分基于锚点校准：
  - 基准地址：`0x39d0f1dca6fb7e5514858c1a337724a426764fe8`
  - `anchored_score = clamp(60 + (raw - anchor_raw_base) * calibration_scale, 0, 100)`
- 结论采用风险分层而非一刀切硬拒：
  - 高分且低风险：`relative_copyable`
  - 大部分 `40+`：`selective_copying_only`
  - 极低分/重风险：`not_recommended`
- 黑名单关键词增强：
  - 输出 `hard_blacklist_keywords` 和 `soft_blacklist_keywords`
  - 默认用于“筛选着跟”模式

## 输出产物

- `accounts/<address>/account_analysis.json`
- `accounts/<address>/report_en.md`
- `accounts/<address>/report_zh.md`
- `summary_all_accounts.csv`
- `summary_all_accounts.md`
- `summary_all_accounts.json`
- `baseline/baseline_anchor.json`

## 报告形态（已优化）

每个账户报告固定为：
1. 账户身份（名称醒目）
2. 执行结论（描述性文字）
3. 行为解读 / 优势 / 风险
4. 板块与黑白名单关键词
5. 指标与评分拆解
