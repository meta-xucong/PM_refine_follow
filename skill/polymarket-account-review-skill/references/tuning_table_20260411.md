# Tuning Table (2026-04-11, Finalized Skill Behavior)

Purpose: align scripted outputs with descriptive manual review style while keeping a stable anchor baseline.

## Major Adjustments

| Area | Previous behavior | Final behavior |
|---|---|---|
| Anchor baseline raw level | anchor raw could drift too low | rebuilt anchor with current formula; baseline raw around high-40s and anchored to 60 |
| Decision policy | `<60` often directly `not_recommended` | risk-gated policy: most `40+` accounts default to `selective_copying_only`; only very low / severe-risk cases become `not_recommended` |
| Hard exclusion | one-shot force reject | split into `caution_risk_gate` and `severe_risk_gate` with layered downgrade logic |
| PnL impact | underweighted in mixed windows | confidence-weighted and upscaled (`*1.85`) so curve quality affects rank materially |
| Frequency impact | some low-activity accounts remained too high | stronger risk penalties and stricter low-frequency caps (`48/56/64`) |
| Blacklist extraction | conservative hard/soft trigger | weighted dirty-ratio + dirty-event boost, generating stronger hard/soft blacklist themes |
| Report readability | metric-heavy blocks first | identity + conclusion + behavior/strength/risk + keyword filters first, then metrics |

## Decision Mapping (Implementation)

1. Base mapping on calibrated `final_score`:
- `>=78` and clean risk gate -> `relative_copyable`
- `40..77.99` -> `selective_copying_only`
- `<40` -> `not_recommended`

2. Risk-gate adjustments:
- caution gate downgrades broad-copy eligibility
- severe gate + low score forces `not_recommended`
- floor safeguard: very low calibrated score always `not_recommended`

## Anchor Freeze

- Anchor account: `0x39d0f1dca6fb7e5514858c1a337724a426764fe8`
- Baseline file: `baseline/baseline_anchor.json`
- Current anchor version: `anchor_v2_20260411`
- Rebuild only when explicitly requested (`--rebuild-anchor`)

## Expected Output Shape

- Per-account reports (EN + ZH) emphasize:
  - account identity,
  - executive conclusion,
  - behavior interpretation,
  - copy strengths/risks,
  - whitelist/hard-blacklist/soft-blacklist themes.
- Batch summary includes account names, raw score, calibrated decision score, decision label, and report links.
