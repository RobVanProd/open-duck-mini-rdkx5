# Closed-Loop Trace Comparison

Offline trace comparison. This does not run robot tests, deploy, SSH, or change runtime behavior.

## Inputs

- left: `baseline_step0` `outputs/analysis/behavior_preserving_recovery_finetune/seed1_seed7_trace_compare/baseline/seed_001/trace.jsonl`
- right: `behavior_prior_smoke` `outputs/analysis/behavior_preserving_recovery_finetune/seed1_seed7_trace_compare/behavior_smoke/seed_001/trace.jsonl`
- common_samples: `750`

## Trace Summary

| trace | samples | duration_s | vx_mean | vx_p05 | vx_p95 | abs_vy_p95 | abs_pitch_p95 | base_height_min | base_x_delta | base_y_delta | double_support_pct | left_only_pct | right_only_pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `baseline_step0` | 750 | 15.0000 | 0.0335 | -0.0132 | 0.0935 | 0.1443 | 0.1165 | 0.1556 | -0.3423 | 0.3635 | 66.6667 | 18.0000 | 15.2000 |
| `behavior_prior_smoke` | 750 | 15.0000 | -0.0014 | -0.0372 | 0.0321 | 0.0307 | 0.0405 | 0.1556 | -0.0033 | -0.0207 | 98.4000 | 0.6667 | 0.8000 |

## Common-Window Delta

Common window uses the first `750` samples from each trace.

| metric | left_mean | right_mean | right_minus_left_mean | abs_delta_p95 |
|---|---:|---:|---:|---:|
| `local_vx` | 0.0335 | -0.0014 | -0.0349 | 0.1069 |
| `local_vy` | 0.0076 | 0.0021 | -0.0055 | 0.1388 |
| `body_pitch` | 0.0840 | -0.0101 | -0.0942 | 0.1332 |
| `base_height` | 0.1630 | 0.1609 | -0.0021 | 0.0072 |
| `base_x` | -0.1476 | -0.0109 | 0.1367 | 0.3248 |
| `base_y` | 0.2048 | -0.0181 | -0.2229 | 0.3741 |
| `reward` | 0.4566 | 0.4977 | 0.0411 | 0.1484 |

## First Divergence

| metric | tick | time_s | left | right | delta | threshold |
|---|---:|---:|---:|---:|---:|---:|
| `local_vx` | 10 | 0.2000 | -0.0159 | -0.0848 | -0.0689 | 0.0500 |
| `local_vy` | 12 | 0.2400 | -0.1767 | -0.0671 | 0.1096 | 0.0500 |
| `body_pitch` | 22 | 0.4400 | 0.0102 | -0.0474 | -0.0576 | 0.0500 |
| `base_height` | NA | NA | NA | NA | NA | NA |
| `base_x` | 158 | 3.1600 | -0.0401 | -0.0099 | 0.0302 | 0.0300 |
| `base_y` | 23 | 0.4600 | 0.0068 | -0.0238 | -0.0306 | 0.0300 |

## Pitch-Chain Joint Deltas

| joint | action_abs_delta_p95 | sent_target_abs_delta_p95_rad | actual_abs_delta_p95_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 0.4299 | 0.1075 | 0.1083 |
| `left_knee` | 0.4628 | 0.1157 | 0.1288 |
| `left_ankle` | 0.5690 | 0.1422 | 0.1602 |
| `right_hip_pitch` | 0.4117 | 0.1029 | 0.1000 |
| `right_knee` | 0.5372 | 0.1343 | 0.1254 |
| `right_ankle` | 0.4618 | 0.1154 | 0.1407 |
