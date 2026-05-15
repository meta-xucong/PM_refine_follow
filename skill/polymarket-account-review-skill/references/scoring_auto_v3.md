# Auto V3 Scoring Target

This is the implemented scoring spec for the auto leaderboard screening workflow. The account-review skill defaults to `--score-version auto_v3`; V2.2 remains available for compatibility through `--score-version v2_2`.

## Main Changes From V2.2

- Keep behavior and copyability risk as the core.
- Add `discovery_score` for candidate ordering.
- Add `data_quality_score` so incomplete API data can cap alerts.
- Add `pnl_quality_score` with recent-window coverage and normalized return quality.
- Add lifetime PnL eligibility: total account PnL must be non-negative and account age must be at least 270 days.
- Add lifetime PnL smoothness and activity-continuity adjustment.
- Add `copy_capacity_score` for practical followability.
- Add automation-specific HFT penalties and caps.
- Add `alert_grade` and `auto_action`.
- Rebuild a new `baseline_anchor_auto_v3.json`; do not reuse the V2.2 raw anchor base.

## 2026-05-15 Follow-Copy Quality Tightening

Auto V3 now treats the final score as a follow-copy suitability score, not a pure recent leaderboard score. The practical calibration target is:

- Stable, long-lived, smooth, medium-scale accounts can score `70+`.
- Accounts that were old but only became meaningfully active recently should be capped around `40..58`.
- Accounts with material recent 7d loss, extreme lifetime drawdown, or obvious spiky PnL should not reach B grade.
- Small-capital recent outperformers should remain watchlist/C unless they prove longer, smoother activity.

Implemented rule changes:

- `/closed-positions` pagination continues through API-silent 50-row page caps before treating lifetime history as complete.
- `leaderboard_consistency_adj` is capped at `+2`; discovery/leaderboard strength is mostly for ordering, not final copy quality.
- `normalized_return_quality` is discounted when 30d buy notional is below `20,000` USDC.
- `copy_capacity_score` includes 30d buy notional and current positions value.
- `late_activity_ramp` detects accounts with account age >= 270d, active-month ratio `<0.45`, active days `<45`, and >=65% of lifetime active days inside the recent 90d window.
- `final_score` now has quality-gate caps:
  - recent 30d and 7d both negative: cap `45`
  - 30d positive but 7d materially negative: cap `55` or `48`
  - extreme lifetime drawdown or daily volatility: cap `52`
  - late activity ramp: cap `58`, or `48` when also small scale
  - low copy capacity: cap `48`
  - incomplete closed-position history: cap `58`

## Primary Output Fields

- `score_version = auto_v3`
- `legacy_v2_score`
- `discovery_score`
- `raw_score_v3`
- `anchored_score_v3`
- `final_score`
- `data_quality_score`
- `pnl_quality_score`
- `copy_capacity_score`
- `alert_grade`
- `auto_action`
- `score_flags`

## Raw Score V3

```text
raw_score_v3_before_cap =
  copyability_score_v3          # 0..30
+ deployability_score_v3        # 0..15
+ structure_score_v3            # 0..15
+ pnl_quality_score             # -20..25
+ copy_capacity_adjustment      # -10..10
+ data_quality_adjustment       # -10..3
+ leaderboard_consistency_adj   # -5..5
+ lifetime_pnl_adjustment       # -12..9
+ automation_risk_penalty       # -25..0
- concentration_penalty_v3      # 0..10
```

Then apply low-frequency, high-frequency, data-quality, and lifetime eligibility caps, then clamp to `0..100`.

## Lifetime PnL Eligibility And Smoothness

Hard reject:

- total account PnL `< 0`: force `decision=not_recommended`, `alert_grade=none`, `auto_action=skip`, final cap `39`
- account age `< 270` days or unknown: force `decision=not_recommended`, `alert_grade=none`, `auto_action=skip`, final cap `39`

Soft adjustment:

- smooth all-time upward PnL, low drawdown, and no single-day spike add points
- volatile all-time PnL, large drawdown relative to total PnL, single-day spike concentration, or high daily volatility subtract points
- long account age with broad month-to-month activity adds points
- long account age with sparse history and a recent activity spike subtracts points

New flags include `negative_total_pnl`, `account_age_under_9m`, `account_age_unknown`, `pnl_smooth_up`, `pnl_spiky`, `pnl_single_spike`, `pnl_drawdown_high`, `long_consistent_activity`, and `dormant_recent_spike`.

## Anchor V3

Anchor account remains:

```text
0x39d0f1dca6fb7e5514858c1a337724a426764fe8
```

Target score remains `60`.

New baseline file:

```text
baseline/baseline_anchor_auto_v3.json
```

```text
anchored_score_v3 = clamp(60 + (raw_score_v3 - anchor_raw_base_score_v3) * 0.65, 0, 100)
final_score = anchored_score_v3
```

## Alert Grades

- `A`: `final_score >= 78`, no caution/severe gate, `data_quality >= 8`, `copy_capacity >= 7`
- `B`: `final_score >= 65`, no severe gate, `data_quality >= 7`, `copy_capacity >= 5`
- `C`: `final_score > 40`, `data_quality >= 4`, not skipped, no severe risk gate
- `none`: no push

Grade caps:

- caution gate: max B
- `data_quality < 6`: max C
- `avg_trades_per_active_day > 300`: max C
- severe gate: no alert push; force `decision=not_recommended`, `alert_grade=none`, `auto_action=skip`
- negative total PnL or account age under 9 months: no alert push; force `decision=not_recommended`, `alert_grade=none`, `auto_action=skip`

See `docs/auto_screening/11_scoring_v3_target_spec.md` for full implementation details.
