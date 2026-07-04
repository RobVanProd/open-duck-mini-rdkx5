# Phase 2 z=0.0075 Control-Preserving Recovery Rate150 Decision

status: `HOLD_SEED7_RESTORED_SEED0_EARLY_LUNGE`

## Scope

- offline sim/data curation only; no robot, SSH, deploy, grounded replay, runtime behavior changes, or PPO training.

## Candidate

`policy/candidates/phase2_z0075_control_preserving_recovery_rate150_20260704/candidate.onnx`

- candidate sha256: `290a4dc13c37396d3556d7a0425951374f4597646b419331ced9f8d21c38cd9c`
- student npz sha256: `26a154bf437daf91af3bb534e0f1a2357788046e8fbae4a29a9eba36c99d13fb`
- manifest: `outputs/analysis/phase2_z0075_iter4_control_preserving_recovery_manifest.json`
- dataset samples: `50253`

## What Changed

This run kept the iter3 seed-0 recovery relabel data and added the iter2 seed-7 passing trace as an explicit weighted control. The goal was to recover seed-7 stability while keeping seed-0 recovery pressure.

## Fit Metrics

| metric | value |
|---|---:|
| MAE | 0.00897255 |
| p95 abs error | 0.02970443 |
| max abs error | 0.56353477 |
| target-rate p95 rad/s | 1.36687715 |
| target-rate max rad/s | 2.32152748 |
| ONNX max abs error | 0.00000030 |
| sample weight max | 8.00000000 |

## Compact Boundary Screen

z=0.0075 rough terrain, x=0.08, intermediate push, seeds 0 and 7.

| seed | status | samples | termination | track ratio | p95 velocity excess | max velocity excess | max tracking p95 | push success |
|---:|---|---:|---|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 142 | `fall_or_nan` | 1.9118 | 0.0000 | 0.0000 | 0.2180 | 0.5000 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.4123 | 0.0000 | 0.0000 | 0.1914 | 0.9000 |

## Seed 0 Failure Diagnostic

`HOLD_PHASE2_INTERMEDIATE_PUSH_WINDOW_PITCHOVER`

| seed | classification | last push tick | pitch>0.8 tick | height<0.08 tick | max excess | final vx | final pitch | final height |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `PUSH_WINDOW_PITCHOVER` | None | 132 | 138 | 0.0000 | 1.4909 | 1.2816 | -0.0004 |

## Decision

`HOLD_SEED7_RESTORED_SEED0_EARLY_LUNGE`

Do not promote. Seed7 pass behavior was restored, but seed0 regressed to an early high-track-ratio lunge and fall at sample 142 with zero corrected-envelope excess.

Do not run robot validation. Do not use this candidate as a Phase 2 promotion artifact.

## Next Recommendation

Preserve the iter4 seed7 control result, but target seed0 anti-lunge/pitch recovery explicitly. Do not add more forward-progress or seed0 push-window weighting without a mechanism that caps track-ratio overshoot during push recovery.
