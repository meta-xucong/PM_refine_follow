# Multi-Market Typing Rules (V2.2 Operational)

## 1) Event Relation Types

For each `eventSlug` cluster with 2+ distinct `conditionId`:

1. `exclusive`
- outcomes are mutually exclusive and only one YES can settle true
- common title patterns:
  - `who will win`
  - `winner`
  - `highest grossing`
  - `top scorer`
  - clear range buckets (`<`, `>`, `between`, `X-Y`)

2. `nested_deadline`
- monotonic deadline containment patterns
- common title patterns:
  - `by <date>`
  - `before <date>`
  - `on or before <date>`

3. `independent`
- same broad topic but not mutually exclusive and not deadline-contained

4. `unknown`
- insufficient text/structure to classify reliably

## 2) Concurrent-Leg First Principle

For `exclusive` and `nested_deadline`, risk is determined by whether related legs are materially held at the same time.

Material overlap defaults:
- overlap duration >= `3` minutes
- overlapping notional >= max(`$10`, `10%` of event BUY notional)
- concurrent active legs >= `2`

Allowed transient overlap (do not auto-mark dirty):
- very short overlap
- tiny overlap notional
- old leg almost fully exited while rolling to a new leg

## 3) Event Subtype Mapping

For `exclusive`:
- `exclusive_concurrent_multi_leg`: concurrent material overlap of 2+ legs
- `exclusive_sequential_switch`: mostly one active leg at a time, switching after near-exit

For `nested_deadline`:
- `nested_concurrent_ladder`: concurrent material overlap of multiple deadline legs
- `nested_sequential_roll`: sequential roll from near deadline to further deadline

## 4) Risk Interpretation

- `exclusive_concurrent_multi_leg`: high risk, strong penalty
- `nested_concurrent_ladder`: medium-high risk, penalize less than exclusive concurrent
- `exclusive_sequential_switch`: medium-low risk, can remain `semiclean`
- `nested_sequential_roll`: medium-low risk, can remain `semiclean`
- `independent`: low structural risk unless combined with fast rebalance behavior
- `unknown`: neutral-to-conservative handling

## 5) Required Output Fields per Event

- `eventSlug`
- `relation_type`
- `event_subtype`
- `distinct_conditions`
- `event_buy_usdc`
- `concurrent_buy_usdc`
- `concurrent_ratio`
- `sequential_switch_count`
- `classification` (`clean` / `semiclean` / `dirty`)
