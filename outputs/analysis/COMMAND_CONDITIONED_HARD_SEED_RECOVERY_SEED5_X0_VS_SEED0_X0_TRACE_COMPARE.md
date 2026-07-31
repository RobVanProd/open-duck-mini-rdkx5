# Closed-Loop Trace Comparison

Offline trace comparison. This does not run robot tests, deploy, SSH, or change runtime behavior.

## Inputs

- left: `seed5_x0_fail` `outputs/analysis/command_conditioned_hard_seed_recovery/seed5_x0_trace/command_conditioned_hard_seed_recovery_candidate/seed_005/trace.jsonl`
- right: `seed0_x0_pass` `outputs/analysis/command_conditioned_hard_seed_recovery/x0_pass_traces/command_conditioned_hard_seed_recovery_candidate/seed_000/trace.jsonl`
- common_samples: `73`

## Trace Summary

| trace | samples | duration_s | vx_mean | vx_p05 | vx_p95 | abs_vy_p95 | abs_pitch_p95 | base_height_min | base_x_delta | base_y_delta | double_support_pct | left_only_pct | right_only_pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed5_x0_fail` | 73 | 1.4600 | -0.2176 | -1.2001 | 0.1672 | 0.1349 | 1.2413 | 0.0464 | 0.1452 | 0.1451 | 79.4521 | 6.8493 | 6.8493 |
| `seed0_x0_pass` | 500 | 10.0000 | 0.0003 | -0.0187 | 0.0169 | 0.0241 | 0.0246 | 0.1520 | -0.0077 | 0.0022 | 98.4000 | 0.6000 | 1.0000 |

## Common-Window Delta

Common window uses the first `73` samples from each trace.

| metric | left_mean | right_mean | right_minus_left_mean | abs_delta_p95 |
|---|---:|---:|---:|---:|
| `local_vx` | -0.2176 | 0.0029 | 0.2204 | 1.2041 |
| `local_vy` | -0.0105 | -0.0002 | 0.0104 | 0.0578 |
| `body_pitch` | -0.3742 | 0.0103 | 0.3845 | 1.2566 |
| `base_height` | 0.1636 | 0.1609 | -0.0027 | 0.0425 |
| `base_x` | -0.0330 | -0.0563 | -0.0233 | 0.1222 |
| `base_y` | -0.0258 | -0.0443 | -0.0185 | 0.1176 |
| `reward` | 0.4110 | 0.4726 | 0.0616 | 0.1700 |

## First Divergence

| metric | tick | time_s | left | right | delta | threshold |
|---|---:|---:|---:|---:|---:|---:|
| `local_vx` | 0 | 0.0000 | 0.0369 | -0.0313 | -0.0683 | 0.0500 |
| `local_vy` | 1 | 0.0200 | 0.0235 | 0.1149 | 0.0914 | 0.0500 |
| `body_pitch` | 2 | 0.0400 | -0.0299 | 0.0340 | 0.0639 | 0.0500 |
| `base_height` | 67 | 1.3400 | 0.1355 | 0.1607 | 0.0252 | 0.0200 |
| `base_x` | 57 | 1.1400 | -0.0247 | -0.0582 | -0.0335 | 0.0300 |
| `base_y` | 57 | 1.1400 | -0.0133 | -0.0441 | -0.0308 | 0.0300 |

## Pitch-Chain Joint Deltas

| joint | action_abs_delta_p95 | sent_target_abs_delta_p95_rad | actual_abs_delta_p95_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 0.1332 | 0.0333 | 0.0820 |
| `left_knee` | 0.1731 | 0.0433 | 0.0566 |
| `left_ankle` | 0.2528 | 0.0632 | 0.0697 |
| `right_hip_pitch` | 0.2109 | 0.0527 | 0.0661 |
| `right_knee` | 0.2114 | 0.0528 | 0.0862 |
| `right_ankle` | 0.1573 | 0.0393 | 0.1316 |
