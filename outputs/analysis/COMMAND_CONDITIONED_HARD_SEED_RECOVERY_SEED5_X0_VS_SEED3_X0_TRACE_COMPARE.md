# Closed-Loop Trace Comparison

Offline trace comparison. This does not run robot tests, deploy, SSH, or change runtime behavior.

## Inputs

- left: `seed5_x0_fail` `outputs/analysis/command_conditioned_hard_seed_recovery/seed5_x0_trace/command_conditioned_hard_seed_recovery_candidate/seed_005/trace.jsonl`
- right: `seed3_x0_pass` `outputs/analysis/command_conditioned_hard_seed_recovery/x0_pass_traces/command_conditioned_hard_seed_recovery_candidate/seed_003/trace.jsonl`
- common_samples: `73`

## Trace Summary

| trace | samples | duration_s | vx_mean | vx_p05 | vx_p95 | abs_vy_p95 | abs_pitch_p95 | base_height_min | base_x_delta | base_y_delta | double_support_pct | left_only_pct | right_only_pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed5_x0_fail` | 73 | 1.4600 | -0.2176 | -1.2001 | 0.1672 | 0.1349 | 1.2413 | 0.0464 | 0.1452 | 0.1451 | 79.4521 | 6.8493 | 6.8493 |
| `seed3_x0_pass` | 500 | 10.0000 | -0.0056 | -0.0399 | 0.0172 | 0.0235 | 0.0498 | 0.1548 | -0.0384 | 0.0393 | 98.8000 | 0.6000 | 0.2000 |

## Common-Window Delta

Common window uses the first `73` samples from each trace.

| metric | left_mean | right_mean | right_minus_left_mean | abs_delta_p95 |
|---|---:|---:|---:|---:|
| `local_vx` | -0.2176 | -0.0387 | 0.1789 | 1.2030 |
| `local_vy` | -0.0105 | 0.0046 | 0.0152 | 0.1803 |
| `body_pitch` | -0.3742 | 0.0343 | 0.4085 | 1.2388 |
| `base_height` | 0.1636 | 0.1617 | -0.0019 | 0.0430 |
| `base_x` | -0.0330 | -0.0851 | -0.0521 | 0.1547 |
| `base_y` | -0.0258 | 0.0422 | 0.0679 | 0.1021 |
| `reward` | 0.4110 | 0.4518 | 0.0408 | 0.1481 |

## First Divergence

| metric | tick | time_s | left | right | delta | threshold |
|---|---:|---:|---:|---:|---:|---:|
| `local_vx` | 0 | 0.0000 | 0.0369 | -0.1535 | -0.1904 | 0.0500 |
| `local_vy` | 1 | 0.0200 | 0.0235 | 0.0869 | 0.0634 | 0.0500 |
| `body_pitch` | 1 | 0.0200 | -0.0076 | 0.0669 | 0.0745 | 0.0500 |
| `base_height` | 1 | 0.0200 | 0.1463 | 0.1667 | 0.0204 | 0.0200 |
| `base_x` | 16 | 0.3200 | -0.0559 | -0.0876 | -0.0316 | 0.0300 |
| `base_y` | 0 | 0.0000 | -0.0281 | 0.0071 | 0.0352 | 0.0300 |

## Pitch-Chain Joint Deltas

| joint | action_abs_delta_p95 | sent_target_abs_delta_p95_rad | actual_abs_delta_p95_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 0.1571 | 0.0393 | 0.0688 |
| `left_knee` | 0.1505 | 0.0376 | 0.1688 |
| `left_ankle` | 0.2580 | 0.0645 | 0.0431 |
| `right_hip_pitch` | 0.2461 | 0.0615 | 0.0730 |
| `right_knee` | 0.1818 | 0.0454 | 0.1419 |
| `right_ankle` | 0.1432 | 0.0358 | 0.1149 |
