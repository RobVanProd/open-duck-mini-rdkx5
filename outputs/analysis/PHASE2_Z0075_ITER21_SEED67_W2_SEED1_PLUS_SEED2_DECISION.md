# Phase 2 z0.0075 Iter21 Seed6/7 Weight2 + Seed1 + Seed2 Decision

status: `HOLD_SEED2_RECOVERED_SEED7_REGRESSED_REVERSE`

## Context

The previous candidate recovered seeds 0, 1, 6, and 7 but failed seed2 with reverse motion.
A full-observation seed2 trace was collected, one failed push window was extracted, and the
window was relabelled with the source-VX live-oracle selector at low weight 2.0.

## Candidate

- path: `policy/candidates/phase2_z0075_iter21_seed67_w2_seed1_plus_seed2_rate150_20260704/candidate.onnx`
- ONNX sha256: `364cf5ce6c79cdd75a89ff3ee4dc77f8b062296ceeeeaefe1d0dccfb2212ed49`
- NPZ sha256: `ea928c23978047eb0853f12215aec883492eda94b4152e1e583f70b7d68ad671`
- merged manifest sha256: `3398b064c7454faae25d046c630450b4060e3dca58251d0e9c709adfb99029fa`
- training status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

## Compact Screen

| seed | status | samples | termination | track_ratio | mean_local_vx | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 | max_vel_excess |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3842 | 0.0307 | 0.1803 | 0.1580 | 1.5483 | 0.1802 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3679 | 0.0294 | 0.1722 | 0.1578 | 1.5496 | 0.1867 | 0.0000 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3398 | 0.0272 | 0.1787 | 0.1573 | 1.5593 | 0.1840 | 0.0000 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3100 | 0.0248 | 0.1816 | 0.1583 | 1.5644 | 0.1846 | 0.0000 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 288 | `fall_or_nan` | -0.5495 | -0.0440 | 0.1713 | 0.0549 | 1.5588 | 0.1761 | 0.0000 |

## Interpretation

The low-weight recovery approach is no longer producing monotonic distributional progress.
It can fix the most recent failed seed, but the same memoryless student then moves a
different seed into reverse/low-progress collapse. The sequence is now:

1. Full-weight seed6/7 recovery fixed neither the distribution nor seed0 stability.
2. Weight2 seed6/7 recovery preserved seed0 and recovered 6/7, but failed seed1.
3. Weight2 seed1 recovery recovered 0/1/6/7, but failed seed2.
4. Weight2 seed2 recovery recovered 0/1/2/6, but failed seed7.

All of these holds have zero corrected-envelope velocity excess.

## Decision

Do not run x=0.0, do not promote, and do not validate on the robot.

Recommended next branch:

- stop appending another memoryless low-weight snippet as the primary strategy;
- escalate representation or conditioning, such as recurrent student, short history,
  explicit recovery-mode context, or a stronger live-oracle DAgger loop that can preserve
  the whole sensitive seed set simultaneously;
- keep the compact sensitive-seed screen `0,1,2,6,7` as the anti-regression gate for the
  next representation experiment.
