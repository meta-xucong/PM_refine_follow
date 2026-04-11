# Tuning Table (2026-04-11)

Purpose: make skill scores closer to manual descriptive judgment, especially on:
- low-frequency over-scoring
- over-optimistic PnL contribution with sparse recent windows
- nested concurrent risk under-penalization

## Parameter Changes

| Area | Before | After | Why |
|---|---:|---:|---|
| `copyability` nested penalty coef | 12 | 18 | strengthen penalty on nested concurrent-heavy accounts |
| `structure` nested penalty coef | 14 | 22 | reduce chance that nested ladders still rank near top |
| hard exclusion: `noncopyable_token_fast_sell_ratio` | >0.35 | >0.70 | avoid false hard-reject when only sell-side exits are fast |
| risk penalty: `nested_conc > 0.55` | none | -4 | treat high nested concurrency as meaningful risk even without rebalance |
| risk penalty: `nested_conc > 0.75` | none | -3 extra | extra penalty for extreme ladder-style overlap |
| risk penalty: `noncopy_sell` | >0.35 => -5 | >0.45 => -4; >0.65 => -3 | smoother sell-side penalty curve |
| low-freq cap tier1 (`active/trade`) | `<4 / <40` | same | keep strict floor |
| low-freq cap tier2 (`active/trade`) | `<8 / <100` | same | medium strict |
| low-freq cap tier3 (`active/trade`) | `<12 / <180` + cap 66 | from `<10 / <90` + cap 68 | stronger cap for moderate-low activity |
| PnL confidence factor | none | by available windows: `1.0 / 0.75 / 0.45 / 0.0` | prevent all-time-only PnL from over-inflating score |
| PnL formula | `(sum)*1.35` | `(sum)*1.35*confidence` | reliability-aware scoring |

## Backtest Snapshot (same dataset)

- Previous run: `analysis_reports_20260411_revised_v2`
  - decisions: `selective_copying_only=4`, `not_recommended=23`
- Tuned run: `analysis_reports_20260411_tuned`
  - decisions: `selective_copying_only=1`, `not_recommended=26`

Notable score moves:
- `0xd5b97...`: `73.51 -> 52.04` (nested concurrent risk now fully reflected)
- `0x52f518...`: `61.89 -> 33.69` (extreme nested concurrent ratio no longer passes)
- `0x0f37cb...`: `68.00 -> 58.00` (low-frequency + sparse PnL windows reduce inflated score)

## Notes

- This tuning intentionally prefers recall of risky accounts over higher pass rate.
- If needed, a softer variant can be produced by:
  - raising tier3 low-freq cap `66 -> 70`
  - relaxing nested penalties (`18/22 -> 15/18`)
  - keeping PnL confidence scaling unchanged.
