# Phase 2 z=0.0075 Live-Oracle Iter2 Failure Recovery Rate150 Decision

status: `HOLD_PUSH_WINDOW_PITCHOVER_SEED0`

## Scope

- Offline sim/data collection, BC fit, and corrected-bridge candidate screens only.
- No robot tests, SSH, deploy, grounded replay, runtime behavior changes, or PPO training were performed.

## Candidate

`policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_rate150_20260704/candidate.onnx`

- candidate sha256: `23b94150e2914bdb9cab5c90bbb27686cf4eaa6db24ce79000ae72724171a916`
- student npz sha256: `e1ab2e1d65c28d8952ee696fb9b9a49ae66114e27a4c0b7e04b0cabfc95a98c7`
- source manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_run/live_oracle_dagger_aggregate_manifest.json`
- dataset_id: `ad1f4a6a5446d648`
- samples: `48815`

## What Changed

This run added live-oracle labels from the iter1 student's actual failed
states under the z=0.0075 rough-terrain intermediate-push gate:

- x=0.08 seeds `1-5`
- x=0.0 seeds `0-1`
- fitted corrected bridge
- push magnitude `0.075-0.125`
- push interval `1.0-1.5 s`

The added data is useful but not sufficient for promotion.

## Fit Metrics

| metric | value |
|---|---:|
| action MAE | 0.009422 |
| action p95 abs error | 0.029820 |
| action max abs error | 0.487725 |
| fit target-rate p95 | 1.371563 rad/s |
| fit target-rate max | 2.462790 rad/s |
| ONNX max abs error | 0.00000030 |

## Compact Boundary Screen

z=0.0075 rough terrain, x=0.08, intermediate push:

| seed | status | samples | termination | track ratio | p95 velocity excess | max velocity excess | max tracking p95 |
|---:|---|---:|---|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 689 | `fall_or_nan` | 0.7277 | 0.0000 | 0.0638 | 0.1954 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3747 | 0.0000 | 0.0000 | 0.1873 |

## Seed 0 Failure Diagnostic

`HOLD_PHASE2_INTERMEDIATE_PUSH_WINDOW_PITCHOVER`

- last push tick: `670`
- pitch exceeded 0.8 rad at tick `681`
- base height fell below 0.08 m at tick `685`
- last push recovery window ended at tick `688`
- last push recovered: `False`
- max velocity excess: `0.0638 rad/s` on `right_ankle`

This is no longer the broad corrected-envelope spike failure from iter1. The
remaining compact blocker is a late seed-0 pitch/base-height collapse inside
an active push recovery window.

## Decision

`HOLD_PUSH_WINDOW_PITCHOVER_SEED0`

Do not promote this candidate. Do not run robot validation.

The iter2 recovery data improved the boundary behavior:

- seed 7 now passes the compact intermediate-push screen,
- seed 0 runs to 689 samples with clean p95 velocity envelope,
- the main remaining failure is push-window recovery stability, not a broad
  corrected-envelope regression.

## Next Step

Collect or weight recovery labels around seed 0's final push window, especially
ticks near `670-688`, while preserving:

- seed 7 pass behavior,
- x=0.0 command semantics,
- zero p95 corrected-envelope excess,
- compact no-spike behavior from iter1.

Do not return to global ankle smoothing or broad label replacement. The next
recipe should target active push-window pitch/base-height recovery.
