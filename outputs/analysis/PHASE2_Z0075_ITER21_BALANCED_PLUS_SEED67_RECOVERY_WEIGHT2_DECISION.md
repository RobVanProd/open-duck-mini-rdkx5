# Phase 2 z0.0075 Iter21 Balanced + Seed6/7 Recovery Weight2 Decision

status: `HOLD_WEIGHT2_RECOVERS_0_6_7_BUT_FAILS_SEED1`

## Context

The full-weight seed6/7 recovery candidate regressed seed0, showing that the seed6/7
failure snippets were useful but too strong when appended at weight 5.0. This follow-up
kept the same snippets and teacher labels, but capped their gate-aware sample weights at
2.0 before merging them into the balanced manifest.

## Candidate

- path: `policy/candidates/phase2_z0075_iter21_balanced_plus_seed67_recovery_weight2_rate150_20260704/candidate.onnx`
- ONNX sha256: `4977b1ae2928e44d1059047b7b26d6e1815dcd8dff2a8cb84695fe75be61caed`
- NPZ sha256: `493403a1ca1af8b0140d352d6914015bb5d71a3d35aa0a4d89debd2f8038f7e5`
- merged manifest sha256: `6dc64894ac8b5c4a44f1d2b8f05c7d92af771835c48d24e3c3eb80d53495841d`
- training status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

## Compact 0/6/7 Screen

The compact recovery/regression screen passed:

| seed | status | samples | termination | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 | max_vel_excess |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3618 | 0.1813 | 0.1582 | 1.5992 | 0.1842 | 0.0000 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3438 | 0.1889 | 0.1580 | 1.6013 | 0.1853 | 0.0000 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3514 | 0.1612 | 0.1582 | 1.6103 | 0.1876 | 0.0000 |

This is a real improvement over the full-weight variant:

- seed0 no longer regresses;
- seed6 recovers from the prior 212-sample fall;
- seed7 recovers from the prior 619-sample fall;
- all three remain inside the corrected velocity envelope.

## Full x=0.08 Gate

The full 8-seed gate was started and stopped after seed1 failed:

| seed | status | samples | termination | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 | max_vel_excess |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3618 | 0.1813 | 0.1582 | 1.5992 | 0.1842 | 0.0000 |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 454 | `fall_or_nan` | 0.7801 | 0.3562 | 0.0153 | 1.6065 | 0.1918 | 0.0000 |

## Interpretation

Down-weighting the seed6/7 recovery snippets fixed the specific 0/6/7 tradeoff, but the
full seed distribution still exposes a new post-push stability failure on seed1. The
failure remains inside the corrected actuator envelope. This narrows the remaining issue
to seed-distribution stability transfer under rough-terrain pushes, not velocity budget.

## Decision

Do not promote to x=0.0 gate, full deployable candidate, or robot validation.

Recommended next step:

- collect a full-observation trace for seed1 on this weight2 candidate;
- extract the failed push window;
- add seed1 recovery with low weighting while preserving the compact 0/6/7 pass as an
  anti-regression screen.
