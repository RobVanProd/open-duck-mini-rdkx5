# Closed-Loop Trace Comparison

Offline trace comparison. This does not run robot tests, deploy, SSH, or change runtime behavior.

## Inputs

- left: `command_gated_seed5_lunge` `outputs/analysis/phase2_command_gated_zero0020_seed5_failure_trace/command_gated_zero0020/seed_005/trace.jsonl`
- right: `rate160_seed5_stable_hold` `outputs/analysis/phase2_rate160_z0075_intermediate_push_seed5_trace/phase_mod_rate160/seed_005/trace.jsonl`
- common_samples: `158`

## Trace Summary

| trace | samples | duration_s | vx_mean | vx_p05 | vx_p95 | abs_vy_p95 | abs_pitch_p95 | base_height_min | base_x_delta | base_y_delta | double_support_pct | left_only_pct | right_only_pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `command_gated_seed5_lunge` | 158 | 3.1600 | 0.1367 | -0.0525 | 0.7435 | 0.1370 | 0.8743 | -0.0058 | 0.2410 | 0.0926 | 88.6076 | 7.5949 | 1.8987 |
| `rate160_seed5_stable_hold` | 750 | 15.0000 | 0.0282 | -0.0501 | 0.0929 | 0.1568 | 0.1777 | 0.1577 | 0.2312 | 0.3203 | 76.6667 | 16.0000 | 7.3333 |

## Common-Window Delta

Common window uses the first `158` samples from each trace.

| metric | left_mean | right_mean | right_minus_left_mean | abs_delta_p95 |
|---|---:|---:|---:|---:|
| `local_vx` | 0.1367 | 0.0291 | -0.1076 | 0.7766 |
| `local_vy` | -0.0050 | 0.0112 | 0.0162 | 0.1324 |
| `body_pitch` | 0.2554 | 0.1288 | -0.1267 | 0.8207 |
| `base_height` | 0.1564 | 0.1642 | 0.0078 | 0.0435 |
| `base_x` | 0.0592 | 0.0479 | -0.0113 | 0.1012 |
| `base_y` | 0.0182 | 0.0200 | 0.0018 | 0.0175 |
| `reward` | 0.4439 | 0.4589 | 0.0150 | 0.1112 |

## First Divergence

| metric | tick | time_s | left | right | delta | threshold |
|---|---:|---:|---:|---:|---:|---:|
| `local_vx` | 80 | 1.6000 | -0.0717 | -0.0184 | 0.0533 | 0.0500 |
| `local_vy` | 95 | 1.9000 | 0.0123 | -0.0412 | -0.0534 | 0.0500 |
| `body_pitch` | 109 | 2.1800 | 0.2199 | 0.1643 | -0.0556 | 0.0500 |
| `base_height` | 145 | 2.9000 | 0.1453 | 0.1655 | 0.0202 | 0.0200 |
| `base_x` | 137 | 2.7400 | 0.1030 | 0.0716 | -0.0314 | 0.0300 |
| `base_y` | 156 | 3.1200 | 0.0893 | 0.0588 | -0.0305 | 0.0300 |

## Pitch-Chain Joint Deltas

| joint | action_abs_delta_p95 | sent_target_abs_delta_p95_rad | actual_abs_delta_p95_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 0.1135 | 0.0284 | 0.0395 |
| `left_knee` | 0.1168 | 0.0292 | 0.0372 |
| `left_ankle` | 0.0978 | 0.0244 | 0.0326 |
| `right_hip_pitch` | 0.0764 | 0.0191 | 0.0211 |
| `right_knee` | 0.1238 | 0.0310 | 0.0320 |
| `right_ankle` | 0.0933 | 0.0233 | 0.0295 |
