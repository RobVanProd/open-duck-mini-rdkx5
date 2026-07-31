# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
bridge_mode: `fitted`
duration_s: `15.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `movement_bootstrap_v7_checkpoint_anchor_20260623` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 59 | `fall_or_nan` | 0.2654 | 3.3171 | 1.2927 | 0.0388 | 1.8118 | 0.2108 |
| `movement_bootstrap_v7_checkpoint_anchor_20260623` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 32 | `fall_or_nan` | 0.0005 | 0.0060 | 0.0063 | 0.0688 | 1.7057 | 0.1796 |
| `movement_bootstrap_v7_checkpoint_anchor_20260623` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0021 | 0.0258 | 0.2074 | 0.1507 | 0.2481 | 0.0775 |
| `movement_bootstrap_v7_checkpoint_anchor_20260623` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0003 | 0.0035 | 0.2074 | 0.1507 | 0.2501 | 0.0775 |
| `movement_bootstrap_v7_checkpoint_anchor_20260623` | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0032 | 0.0394 | 0.2076 | 0.1483 | 0.2358 | 0.0777 |
| `movement_bootstrap_v7_checkpoint_anchor_20260623` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 54 | `fall_or_nan` | -0.3151 | -3.9390 | 0.0814 | 0.0301 | 1.8253 | 0.1650 |
| `movement_bootstrap_v7_checkpoint_anchor_20260623` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 71 | `fall_or_nan` | 0.2066 | 2.5819 | 1.2123 | 0.0425 | 2.3966 | 0.1352 |
| `movement_bootstrap_v7_checkpoint_anchor_20260623` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 28 | `fall_or_nan` | -0.0123 | -0.1539 | 0.1097 | 0.0798 | 2.2417 | 0.4984 |
| `movement_bootstrap_v9_progress_balanced_standstill_20260623` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 73 | `fall_or_nan` | 0.2217 | 2.7707 | 1.2604 | 0.0305 | 2.3669 | 0.1498 |
| `movement_bootstrap_v9_progress_balanced_standstill_20260623` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 32 | `fall_or_nan` | 0.0185 | 0.2314 | 0.0477 | 0.0672 | 1.7712 | 0.1850 |
| `movement_bootstrap_v9_progress_balanced_standstill_20260623` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0020 | 0.0252 | 0.2060 | 0.1503 | 0.2751 | 0.0827 |
| `movement_bootstrap_v9_progress_balanced_standstill_20260623` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0003 | 0.0031 | 0.2061 | 0.1503 | 0.2758 | 0.0826 |
| `movement_bootstrap_v9_progress_balanced_standstill_20260623` | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0032 | 0.0395 | 0.2061 | 0.1485 | 0.2680 | 0.0827 |
| `movement_bootstrap_v9_progress_balanced_standstill_20260623` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 56 | `fall_or_nan` | -0.3045 | -3.8057 | 0.0747 | 0.0298 | 2.1837 | 0.1647 |
| `movement_bootstrap_v9_progress_balanced_standstill_20260623` | 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 58 | `fall_or_nan` | 0.2749 | 3.4361 | 1.3675 | 0.0233 | 2.5044 | 0.1616 |
| `movement_bootstrap_v9_progress_balanced_standstill_20260623` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 27 | `fall_or_nan` | -0.0060 | -0.0752 | 0.1007 | 0.0919 | 2.3741 | 0.5010 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `movement_bootstrap_v7_checkpoint_anchor_20260623` | 8 | 5 | 3 | 311.7500 | 28 | 750 | 0.2351 | 0.0188 | 0.4156 | 0.0887 |
| `movement_bootstrap_v9_progress_balanced_standstill_20260623` | 8 | 5 | 3 | 312.0000 | 27 | 750 | 0.3282 | 0.0263 | 0.4336 | 0.0865 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
