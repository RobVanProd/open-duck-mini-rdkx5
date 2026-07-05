# Phase 2 z0.0075 Iter25 Dual-Anchor Weight4 History-Context Rate150 Decision

status: `HOLD_ITER25_DUAL_ANCHOR_REGRESSES_SEEDS0_7`

## Context

Iter24 recovered the active seed2 failure but regressed seed6. A trace
comparison showed this was a seed-conditioned stability trade, not an actuator
envelope issue. Iter25 tested a targeted anti-regression aggregate:

- base aggregate: iter24 live-oracle aggregate
- added anchors:
  - iter23 candidate seed6 pass trace
  - iter24 candidate seed2 pass trace
- anchor entry sample weight: `4.0`

No robot tests, SSH, deploy, runtime behavior changes, grounded replay, or PPO
training were performed.

## Candidate

- path: `policy/candidates/phase2_z0075_iter25_dual_anchor_weight4_history_context_rate150_20260704/candidate.onnx`
- ONNX sha256: `4e6b462a0daac0c624044bee58951846340e6382c960d194dd06de16763e9b3d`
- NPZ sha256: `e58c985d11b01a250f5f09640a23581b0fed0fcca72ed5426452fc6fa2d7afde`
- aggregate manifest: `outputs/analysis/phase2_z0075_iter25_dual_anchor_weight4_aggregate_manifest.json`
- aggregate manifest sha256: `d6ddd98a535aec2147db157f978eae80669a9718076cf926b2e8f85db9e02467`
- x=0.08 screen JSON sha256: `ec6e2b9ef4f76263248c97bc80269bfa25db397de0dfba9ca14c443d17d1ff74`
- training status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

## Fit Metrics

- samples: `68719`
- target-rate p95: `1.361899 rad/s`
- target-rate max: `9.124381 rad/s`

## Compact x=0.08 Screen

| seed | status | samples | termination | track_ratio | mean_local_vx | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 | max_vel_excess |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 525 | `fall_or_nan` | 0.7229 | 0.0578 | 0.3231 | 0.0048 | 1.5498 | 0.1831 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3567 | 0.0285 | 0.1739 | 0.1579 | 1.5635 | 0.1892 | 0.0000 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3816 | 0.0305 | 0.1878 | 0.1567 | 1.5450 | 0.1836 | 0.0000 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3273 | 0.0262 | 0.1904 | 0.1580 | 1.5479 | 0.1881 | 0.0000 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 470 | `fall_or_nan` | 0.8327 | 0.0666 | 0.3586 | 0.0108 | 1.5580 | 0.1875 | 0.0000 |

## Interpretation

The dual-anchor weighting did its narrow job: seed2 and seed6 both pass.
However, the stronger anchor pressure regressed seeds 0 and 7 into higher-speed
pitch/base-height failures. This is worse than iter24's 4/5 distribution and is
not promotable.

The failed seeds still have zero corrected velocity-envelope excess. The
failure remains a learned stability distribution problem, not an actuator-rate
or tracking violation.

## Decision

Do not promote this candidate and do not run x=0.0 or robot validation.

Recommended next step:

- do not use strong global dual-anchor weighting as the next default;
- if continuing BC aggregation, use a lower anchor weight or a loss/selection
  scheme that protects seeds2 and6 without increasing seed0/7 lunge behavior;
- consider gating candidate selection by full five-seed distribution rather
  than chasing the latest failed seed.
