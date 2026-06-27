# Closed-Loop Trace Comparison

Offline trace comparison. This does not run robot tests, deploy, SSH, or change runtime behavior.

## Inputs

- left: `baseline_step0` `outputs/analysis/behavior_preserving_recovery_finetune/seed1_seed7_trace_compare/baseline/seed_007/trace.jsonl`
- right: `behavior_prior_smoke` `outputs/analysis/behavior_preserving_recovery_finetune/seed1_seed7_trace_compare/behavior_smoke/seed_007/trace.jsonl`
- common_samples: `750`

## Trace Summary

| trace | samples | duration_s | vx_mean | vx_p05 | vx_p95 | abs_vy_p95 | abs_pitch_p95 | base_height_min | base_x_delta | base_y_delta | double_support_pct | left_only_pct | right_only_pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `baseline_step0` | 750 | 15.0000 | 0.0374 | -0.0083 | 0.0919 | 0.1375 | 0.1177 | 0.1559 | -0.3672 | -0.4268 | 65.2000 | 18.0000 | 16.8000 |
| `behavior_prior_smoke` | 750 | 15.0000 | 0.0001 | -0.0373 | 0.0367 | 0.0288 | 0.0395 | 0.1559 | -0.0039 | 0.0012 | 98.8000 | 0.0000 | 1.2000 |

## Common-Window Delta

Common window uses the first `750` samples from each trace.

| metric | left_mean | right_mean | right_minus_left_mean | abs_delta_p95 |
|---|---:|---:|---:|---:|
| `local_vx` | 0.0374 | 0.0001 | -0.0373 | 0.1041 |
| `local_vy` | 0.0054 | -0.0004 | -0.0058 | 0.1463 |
| `body_pitch` | 0.0866 | -0.0079 | -0.0946 | 0.1420 |
| `base_height` | 0.1630 | 0.1608 | -0.0023 | 0.0071 |
| `base_x` | -0.1905 | 0.0113 | 0.2019 | 0.3446 |
| `base_y` | -0.1546 | 0.0370 | 0.1916 | 0.4030 |
| `reward` | 0.4582 | 0.4963 | 0.0381 | 0.1470 |

## First Divergence

| metric | tick | time_s | left | right | delta | threshold |
|---|---:|---:|---:|---:|---:|---:|
| `local_vx` | 10 | 0.2000 | 0.0531 | 0.0028 | -0.0503 | 0.0500 |
| `local_vy` | 13 | 0.2600 | 0.0474 | 0.2098 | 0.1624 | 0.0500 |
| `body_pitch` | 21 | 0.4200 | 0.0839 | 0.0221 | -0.0618 | 0.0500 |
| `base_height` | NA | NA | NA | NA | NA | NA |
| `base_x` | 40 | 0.8000 | -0.0157 | 0.0144 | 0.0301 | 0.0300 |
| `base_y` | 88 | 1.7600 | 0.0061 | 0.0383 | 0.0321 | 0.0300 |

## Pitch-Chain Joint Deltas

| joint | action_abs_delta_p95 | sent_target_abs_delta_p95_rad | actual_abs_delta_p95_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 0.4349 | 0.1087 | 0.1087 |
| `left_knee` | 0.4682 | 0.1171 | 0.1295 |
| `left_ankle` | 0.5659 | 0.1415 | 0.1595 |
| `right_hip_pitch` | 0.4231 | 0.1058 | 0.1043 |
| `right_knee` | 0.5411 | 0.1353 | 0.1266 |
| `right_ankle` | 0.4644 | 0.1161 | 0.1391 |
