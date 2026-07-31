# Closed-Loop Trace Comparison

Offline trace comparison. This does not run robot tests, deploy, SSH, or change runtime behavior.

## Inputs

- left: `seed5_x0_fail` `outputs/analysis/command_conditioned_hard_seed_recovery/seed5_x0_trace/command_conditioned_hard_seed_recovery_candidate/seed_005/trace.jsonl`
- right: `seed5_x008_survive` `outputs/analysis/command_conditioned_hard_seed_recovery/seed5_x008_trace/command_conditioned_hard_seed_recovery_candidate/seed_005/trace.jsonl`
- common_samples: `73`

## Trace Summary

| trace | samples | duration_s | vx_mean | vx_p05 | vx_p95 | abs_vy_p95 | abs_pitch_p95 | base_height_min | base_x_delta | base_y_delta | double_support_pct | left_only_pct | right_only_pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed5_x0_fail` | 73 | 1.4600 | -0.2176 | -1.2001 | 0.1672 | 0.1349 | 1.2413 | 0.0464 | 0.1452 | 0.1451 | 79.4521 | 6.8493 | 6.8493 |
| `seed5_x008_survive` | 500 | 10.0000 | 0.0371 | -0.0187 | 0.1044 | 0.1403 | 0.1283 | 0.1462 | -0.2010 | -0.3067 | 69.8000 | 16.0000 | 13.6000 |

## Common-Window Delta

Common window uses the first `73` samples from each trace.

| metric | left_mean | right_mean | right_minus_left_mean | abs_delta_p95 |
|---|---:|---:|---:|---:|
| `local_vx` | -0.2176 | 0.0437 | 0.2613 | 1.1925 |
| `local_vy` | -0.0105 | -0.0079 | 0.0026 | 0.0818 |
| `body_pitch` | -0.3742 | -0.0479 | 0.3263 | 1.2039 |
| `base_height` | 0.1636 | 0.1655 | 0.0020 | 0.0441 |
| `base_x` | -0.0330 | -0.0686 | -0.0356 | 0.1399 |
| `base_y` | -0.0258 | -0.0720 | -0.0462 | 0.1541 |
| `reward` | 0.4110 | 0.4487 | 0.0378 | 0.1284 |

## First Divergence

| metric | tick | time_s | left | right | delta | threshold |
|---|---:|---:|---:|---:|---:|---:|
| `local_vx` | 7 | 0.1400 | 0.0919 | 0.1450 | 0.0532 | 0.0500 |
| `local_vy` | 16 | 0.3200 | 0.0413 | 0.0959 | 0.0546 | 0.0500 |
| `body_pitch` | 20 | 0.4000 | -0.1828 | -0.1294 | 0.0534 | 0.0500 |
| `base_height` | 67 | 1.3400 | 0.1355 | 0.1627 | 0.0272 | 0.0200 |
| `base_x` | 43 | 0.8600 | -0.0487 | -0.0801 | -0.0314 | 0.0300 |
| `base_y` | 29 | 0.5800 | -0.0482 | -0.0793 | -0.0311 | 0.0300 |

## Pitch-Chain Joint Deltas

| joint | action_abs_delta_p95 | sent_target_abs_delta_p95_rad | actual_abs_delta_p95_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 0.4485 | 0.1121 | 0.1086 |
| `left_knee` | 0.5273 | 0.1318 | 0.1397 |
| `left_ankle` | 0.5243 | 0.1311 | 0.1629 |
| `right_hip_pitch` | 0.4149 | 0.1037 | 0.0990 |
| `right_knee` | 0.5349 | 0.1337 | 0.1354 |
| `right_ankle` | 0.3774 | 0.0943 | 0.1287 |
