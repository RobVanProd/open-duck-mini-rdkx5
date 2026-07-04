# Phase 2 z0.0075 Iter21 Reset-Settle10 Decision

status: `PASS_ITER21_RESET_SETTLE10_FOCUSED_GATE`

Offline-only evaluator/reset diagnostic. No robot tests, SSH, deploy, grounded
replay, runtime behavior change, policy edit, or training was performed.

## Context

Iter21 rate150 was the best static BC student:

- candidate: `policy/candidates/phase2_z0075_iter21_early_lunge_gain095_rate150_20260704/candidate.onnx`
- candidate_sha256: `72aa93c2ab249d2e9b22bb5415ef6c96c7407833fbfd21233892b6daa6afda14`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`

With canonical `home-support` reset and `reset_settle_ticks=0`, focused seeds
`0,2,6` all completed the 15s rough-push gate, but held on one repeated startup
max target-velocity spike:

| seed | status | samples | track_ratio | max target velocity excess |
|---:|---|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.3097 | 0.2014 |
| 2 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.3236 | 0.2014 |
| 6 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.3630 | 0.2014 |

Per-tick trace localized the violation to startup tick 11:

- joint: `left_hip_pitch`
- time: `0.22s`
- previous target: `-0.797172 rad`
- next target: `-0.743143 rad`
- velocity: `2.701429 rad/s`
- corrected limit: `2.500000 rad/s`
- push: inactive

Directly relabeling that startup point, or a short surrounding startup window,
removed the velocity violation but destabilized the policy into early lunge/fall.

## Reset-Settle Sweep

`reset_settle_ticks` steps the reset physics under home motor targets before the
policy loop starts. It does not advance policy state, action history, reward
counters, or sample counts.

Seed0 diagnostic sweep:

| reset_settle_ticks | status | samples | track_ratio | max target velocity excess | base height min |
|---:|---|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.3097 | 0.2014 | 0.1532 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 523 | -0.0641 | 0.0000 | 0.0690 |
| 10 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3391 | 0.0000 | 0.1593 |
| 25 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 529 | -0.0893 | 0.0000 | 0.0633 |

`reset_settle_ticks=10` is the only tested reset-settle value that both removes
the startup velocity excess and preserves the gait.

## Focused Gate With Reset-Settle10

Gate: rough terrain z-scale `0.0075`, fitted corrected bridge, command `x=0.08`,
15s, intermediate pushes, home-support reset, `reset_settle_ticks=10`.

| seed | status | samples | track_ratio | max pitch tracking p95 | max target velocity p95 | max target velocity excess | body pitch p95 | base height min | push success |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3391 | 0.1827 | 1.6164 | 0.0000 | 0.1628 | 0.1593 | 11/12 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3225 | 0.1839 | 1.6214 | 0.0000 | 0.1716 | 0.1589 | 12/13 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3567 | 0.1835 | 1.6211 | 0.0000 | 0.1662 | 0.1588 | 12/13 |

The left-hip-pitch max target velocity in the traced seed0 run dropped from
`2.7014 rad/s` at settle0 to `2.3305 rad/s` at settle10.

## Interpretation

- The remaining Iter21 failure is a reset/startup convention issue, not a
  steady-state gait-rate issue.
- Static BC relabeling of the startup action is the wrong fix because it moves
  the policy off its stable gait manifold.
- A short home-support physics settle before starting the policy loop is the
  first tested intervention that clears the velocity spike while preserving the
  gait on focused seeds.
- This is not yet a full Phase 2 pass. It only promotes `reset_settle_ticks=10`
  to the next full offline gate.

## Next Required Gate

Run the full Phase 2 offline gate with the same reset convention:

1. `x=0.08`, rough terrain z-scale `0.0075`, intermediate pushes, seeds `0-7`.
2. `x=0.0`, same reset convention, seeds `0-7`, command semantics preserved.

Promotion remains blocked until both pass. Robot validation remains blocked.
