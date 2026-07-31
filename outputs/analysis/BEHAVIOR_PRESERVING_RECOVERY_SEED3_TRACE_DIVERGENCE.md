# Closed-Loop Trace Comparison

Offline trace comparison. This does not run robot tests, deploy, SSH, or change runtime behavior.

## Inputs

- left: `baseline_step0` `outputs/analysis/behavior_preserving_recovery_finetune/seed3_trace_compare/baseline/seed_003/trace.jsonl`
- right: `behavior_prior_smoke` `outputs/analysis/behavior_preserving_recovery_finetune/seed3_trace_compare/behavior_smoke/seed_003/trace.jsonl`
- common_samples: `74`

## Trace Summary

| trace | samples | duration_s | vx_mean | vx_p05 | vx_p95 | abs_vy_p95 | abs_pitch_p95 | base_height_min | base_x_delta | base_y_delta | double_support_pct | left_only_pct | right_only_pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `baseline_step0` | 750 | 15.0000 | 0.0293 | -0.0285 | 0.0899 | 0.1338 | 0.1209 | 0.1554 | 0.3920 | -0.1796 | 68.5333 | 16.8000 | 14.4000 |
| `behavior_prior_smoke` | 74 | 1.4800 | -0.2708 | -1.1407 | -0.0459 | 0.0959 | 1.1691 | 0.0684 | -0.1881 | 0.2335 | 78.3784 | 5.4054 | 9.4595 |

## Common-Window Delta

Common window uses the first `74` samples from each trace.

| metric | left_mean | right_mean | right_minus_left_mean | abs_delta_p95 |
|---|---:|---:|---:|---:|
| `local_vx` | -0.0170 | -0.2708 | -0.2538 | 1.2267 |
| `local_vy` | 0.0036 | 0.0086 | 0.0049 | 0.1053 |
| `body_pitch` | 0.0402 | -0.2587 | -0.2989 | 1.1939 |
| `base_height` | 0.1641 | 0.1642 | 0.0002 | 0.0291 |
| `base_x` | -0.0792 | -0.1126 | -0.0334 | 0.1213 |
| `base_y` | 0.0288 | 0.0779 | 0.0491 | 0.1670 |
| `reward` | 0.4468 | 0.4203 | -0.0264 | 0.1213 |

## First Divergence

| metric | tick | time_s | left | right | delta | threshold |
|---|---:|---:|---:|---:|---:|---:|
| `local_vx` | 15 | 0.3000 | -0.1157 | -0.1761 | -0.0604 | 0.0500 |
| `local_vy` | 13 | 0.2600 | -0.0508 | 0.0209 | 0.0716 | 0.0500 |
| `body_pitch` | 23 | 0.4600 | -0.0068 | -0.0629 | -0.0560 | 0.0500 |
| `base_height` | 69 | 1.3800 | 0.1620 | 0.1382 | -0.0238 | 0.0200 |
| `base_x` | 52 | 1.0400 | -0.0827 | -0.1134 | -0.0306 | 0.0300 |
| `base_y` | 37 | 0.7400 | 0.0313 | 0.0620 | 0.0307 | 0.0300 |

## Pitch-Chain Joint Deltas

| joint | action_abs_delta_p95 | sent_target_abs_delta_p95_rad | actual_abs_delta_p95_rad |
|---|---:|---:|---:|
| `left_hip_pitch` | 0.4844 | 0.1211 | 0.1358 |
| `left_knee` | 0.7130 | 0.1782 | 0.1815 |
| `left_ankle` | 0.4944 | 0.1236 | 0.1662 |
| `right_hip_pitch` | 0.4544 | 0.1136 | 0.1228 |
| `right_knee` | 0.5538 | 0.1384 | 0.1447 |
| `right_ankle` | 0.5119 | 0.1280 | 0.1546 |
