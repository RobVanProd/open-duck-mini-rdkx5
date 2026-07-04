# Phase 2 z0.0075 Iter21 Balanced + Seed6/7 Recovery Decision

status: `HOLD_SEED67_RECOVERY_REGRESSED_SEED0`

## Context

The prior balanced post-push recovery candidate passed seeds 0, 2, 3, and 5, but still
failed seeds 6 and 7 under the x=0.08 rough-terrain intermediate-push focused screen.
Both failures had zero corrected-envelope velocity excess.

## Added Evidence

Full-observation traces were collected for the failed balanced-candidate seeds:

| seed | status | samples | track_ratio | max_vel_excess |
|---:|---|---:|---:|---:|
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 212 | 1.4723 | 0.0000 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 619 | 0.7163 | 0.0000 |

Failed push windows were extracted and relabelled with the source-VX live-oracle selector:

- snippets: `2`
- samples: `147`
- relabel manifest dataset_id: `d7864dacd35fae38`

The new recovery manifest was merged with the previous balanced manifest:

- merged dataset_id: `5c0a32e97e15aec6`
- kept entries: `96`
- merged manifest sha256: `a5a69c43f1f9e56d79549e39fba92262537876a0c7a1f914351818cd7cd174a9`

## Candidate

- path: `policy/candidates/phase2_z0075_iter21_balanced_plus_seed67_recovery_rate150_20260704/candidate.onnx`
- ONNX sha256: `a1e703d63d8aaf339fb804ed5f73c12f7412bc449278515e53c00e54256150bf`
- NPZ sha256: `9c402abc681a0689fa95aa55f2a6cfff6f5a2f6501e5be8705f7cb27012139e6`
- training status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`
- samples: `53706`

## Focused Screen

The x=0.08 rough-terrain intermediate-push focused screen was stopped after seed 0 failed,
because seed 0 was a regression guard that passed the previous balanced candidate.

| seed | status | samples | termination | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 | max_vel_excess |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 565 | `fall_or_nan` | 0.7615 | 0.3105 | 0.0054 | 1.5979 | 0.1836 | 0.0000 |

## Interpretation

The seed6/7 recovery labels were valid corrective data, but appending them at the same
weight over-corrected the student and regressed seed0 stability. The failure remains
inside the corrected actuator envelope, so this is still a post-push stability-transfer
problem rather than an actuator-velocity problem.

## Decision

Do not promote this candidate to a full gate. Do not run robot validation.

Recommended next branch:

- reduce or curriculum-weight the high-fall seed6/7 recovery snippets instead of adding
  them at full weight;
- preserve seed0/2/3/5 passing behavior as an explicit anti-regression term;
- consider a representation change or phase/recovery mode indicator before adding more
  late-fall snippets to the same memoryless map.
