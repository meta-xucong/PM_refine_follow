---
name: polymarket-account-review
description: Automatically run end-to-end Polymarket V2.2 screening for one or multiple accounts from CSV, fetch official API account summaries, generate English reports and translated Chinese reports, and output a final all-account summary table.
---

# Polymarket Account Review Skill (V2.2, Auto Batch)

Use this skill when you need to evaluate copy-trading suitability for one or many Polymarket accounts from CSV.

## Default Behavior (No Manual Steps)

When this skill is triggered, the agent should **directly execute** the full workflow and return results, not ask the user to run scripts manually.

Preferred one-shot command:
```bash
python scripts/run_full_screening.py \
  --csv <trade_csv_path> \
  --output-dir <output_dir> \
  --summary-dir <optional_prefetched_summary_dir>
```

This command automatically:
- discovers all unique `account_address` in CSV
- enforces a **frozen 60-point anchor baseline** (`0x39d0f1dca6fb7e5514858c1a337724a426764fe8`)
- fetches official Polymarket API summaries for each account
- runs V2.2 scoring and classification for each account
- generates **English report + Chinese translated report** for each account
- produces a final all-account summary table
- uses dual-layer account PnL summary sourcing:
  - layer 1: reuse prefetched summary JSON files (if provided)
  - layer 2: if missing/incomplete, analysis stage performs one live API fallback

## 60-Point Anchor Baseline (Stable Scoring)

Anchor account:
- `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`

Anchor file:
- `baseline/baseline_anchor.json`

Mechanism:
- score model first computes `raw_score` from V2.2 rules
- then applies baseline calibration around frozen anchor:
  - `anchored_score = clamp(60 + (raw_score - anchor_raw_base_score) * calibration_scale, 0, 100)`
- `final_score` (decision basis) uses calibrated `anchored_score`
- decision uses risk-gated mapping (not single hard-force reject):
  - `>=78` and clean risk gate: `relative_copyable`
  - `40..77.99`: mostly `selective_copying_only`
  - `<40`: `not_recommended`
  - severe-risk gate + low score still forces `not_recommended`

Auto behavior:
- if anchor file exists: reuse it directly
- if anchor file is missing: auto-build and freeze it before batch scoring
- if CSV lacks anchor rows: auto-pull anchor account recent window (default 30d) and freeze baseline

Do not rebuild anchor unless explicitly requested:
- use `--rebuild-anchor` only when you intentionally update benchmark generation

## Input Contract

Required CSV columns:
- `timestamp`
- `conditionId`
- `title`
- `side`
- `outcome`
- `price`
- `size`
- `usdcSize`
- `transactionHash`
- `eventSlug`
- `account_address` (required for batch multi-account)

Preferred columns:
- `asset` (token id fallback)
- `account_name`

Fallback rules:
- if `asset` is missing, token key uses `conditionId|outcome`
- if no SELL rows exist, holding-time metrics are `null` and report must state limitation
- if key numeric fields are missing or unparsable, stop scoring and emit diagnostic caveat

## Required References

Read and enforce:
- [`references/scoring.md`](references/scoring.md)
- [`references/multi_market_typing.md`](references/multi_market_typing.md)
- [`references/pnl_curve_rules.md`](references/pnl_curve_rules.md)
- [`references/polymarket_api.md`](references/polymarket_api.md)
- [`references/tuning_table_20260411.md`](references/tuning_table_20260411.md) (parameter-change rationale and expected impact)

## Output Structure

Batch output directory contains:
- `accounts/<account>/account_summary.json`
- `accounts/<account>/account_analysis.json`
- `accounts/<account>/report_en.md`
- `accounts/<account>/report_zh.md`
- `baseline/baseline_anchor.json`
- `summary_all_accounts.csv`
- `summary_all_accounts.md`
- `summary_all_accounts.json`

## Quality Gates

Before finishing:
- ensure all discovered accounts are analyzed exactly once
- ensure each account has both `report_en.md` and `report_zh.md`
- ensure anchor baseline exists and is attached to scoring
- ensure summary table is sorted by `final_score` (calibrated decision score, descending)
- ensure report order is human-readable: identity -> conclusion -> behavior -> strengths/risks -> keyword filters -> metrics
- ensure percentage metrics are `[0,1]` in JSON and `%` in report
- ensure low-frequency caps and concentration penalties are applied
- ensure strengthened hard/soft blacklist keywords are generated for selective follow filtering
- ensure missing data assumptions are explicitly listed

## Schema + Templates

- Metrics schema: [`schemas/metrics_schema.json`](schemas/metrics_schema.json)
- Output schema: [`schemas/output_schema.json`](schemas/output_schema.json)
- English template: [`templates/report_template.md`](templates/report_template.md)
- Chinese template: [`templates/report_template_zh.md`](templates/report_template_zh.md)

## Chinese Skill Docs

- Chinese workflow guide: [`zh/SKILL_zh.md`](zh/SKILL_zh.md)
- Chinese scoring summary: [`zh/references_scoring_zh.md`](zh/references_scoring_zh.md)
