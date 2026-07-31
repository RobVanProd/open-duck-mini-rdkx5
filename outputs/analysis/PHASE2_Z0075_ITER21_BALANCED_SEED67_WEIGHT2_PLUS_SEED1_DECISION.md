# Phase 2 z0.0075 Iter21 Seed6/7 Weight2 + Seed1 Decision

status: `HOLD_SEED1_RECOVERED_SEED2_REGRESSED_REVERSE`

## Context

The seed6/7 weight2 candidate passed seeds 0, 6, and 7, but failed seed1 in the full
x=0.08 gate. A full-observation seed1 trace was collected, one failed push window was
extracted, and the window was relabelled with the source-VX live-oracle selector at the
same low weight cap of 2.0.

## Candidate

- path: `policy/candidates/phase2_z0075_iter21_balanced_seed67_weight2_plus_seed1_rate150_20260704/candidate.onnx`
- ONNX sha256: `2706d5ad727bd1fa0499a0aa3c66042c9942f75c7d591f1301734cc56d6a6960`
- NPZ sha256: `90210ca4d019677465ec2fa5fb8765d18ea2bdbe34f21e1f38aad7e39c2438e6`
- merged manifest sha256: `98dacdabc03a664bd07fa568145ef18cd8ce2f0422d675c01e0632d85a64f67d`
- training status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

## Compact 0/1/6/7 Screen

| seed | status | samples | termination | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 | max_vel_excess |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3136 | 0.1641 | 0.1586 | 1.5551 | 0.1851 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3545 | 0.1775 | 0.1586 | 1.5414 | 0.1863 | 0.0000 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3061 | 0.1824 | 0.1579 | 1.5533 | 0.1854 | 0.0000 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3405 | 0.1662 | 0.1586 | 1.5599 | 0.1846 | 0.0000 |

This confirms seed1 recovery transferred without breaking the prior 0/6/7 compact pass.

## Missing-Seed Screen

The missing-seed screen was started for seeds 2, 3, 4, and 5. It was stopped after seed2
failed:

| seed | status | samples | termination | track_ratio | mean_local_vx | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 | max_vel_excess |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 282 | `fall_or_nan` | -0.4738 | -0.0379 | 0.1803 | 0.0816 | 1.5591 | 0.1842 | 0.0000 |

## Interpretation

The low-weight recovery loop is directionally useful but still not robust. The candidate
can preserve and recover targeted seeds, but the behavior remains brittle across the full
seed distribution. The seed2 failure is reverse/low-progress collapse, not corrected
actuator-envelope violation.

## Decision

Do not run x=0.0, do not promote, and do not validate on the robot.

Recommended next step:

- collect a full-observation seed2 trace for this candidate;
- treat seed2 as a reverse-motion recovery case rather than another high-track-ratio
  lunge case;
- consider escalating representation or adding an explicit recovery-mode/context signal if
  the next low-weight patch continues the seed-whack-a-mole pattern.
