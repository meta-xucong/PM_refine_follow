# PnL Curve Stability Rules (V2.2 Operational)

## 1) Time Windows

Evaluate three windows:
- all-time (highest weight)
- 30d
- 7d

Preferred data source order:
1. `closed-positions` realized PnL timeline (official API)
2. current `value` and `positions` snapshot as context
3. local CSV-derived approximation if API data is missing

## 2) Window Features

For each window compute:
- `total_return`
- `trend_slope`
- `max_drawdown`
- `daily_volatility`
- `points_count`

## 3) Shape Classification

For each window classify as one of:
- `smooth_up`
- `volatile_up`
- `flat`
- `down`
- `insufficient_data`

Suggested baseline thresholds:
- `smooth_up`:
  - `total_return > 0`
  - `trend_slope > 0`
  - `max_drawdown <= 0.35 * max(total_return, 1)`
- `volatile_up`:
  - `total_return > 0`
  - `trend_slope > 0`
  - drawdown larger than smooth threshold
- `flat`:
  - absolute return below significance floor
- `down`:
  - `total_return < 0` and `trend_slope <= 0`

## 4) Score Table

All-time window:
- `smooth_up`: `+12`
- `volatile_up`: `+6`
- `flat`: `+1`
- `down`: `-10`

30d window:
- `smooth_up` or clear `up`: `+6`
- `flat`: `+1`
- `down`: `-6`

7d window:
- `up`: `+2`
- `flat`: `0..+1`
- `down`: `-2`

Implementation scales the summed 3-window score by `1.35` and clamps to `[-22, +22]` to increase PnL impact vs pure structure-only scoring.

## 5) Interpretation Tags

Map final 3-window result to one summary tag:
- `long_mid_short_strong`
- `long_strong_recent_weak`
- `long_moderate_recent_improving`
- `long_and_recent_weak`

## 6) Guardrails

- PnL score is an adjustment, not a replacement for behavior quality.
- Bad structural behavior cannot be promoted solely by recent positive PnL.
- Missing API data must be declared and scored as neutral (`0`).
