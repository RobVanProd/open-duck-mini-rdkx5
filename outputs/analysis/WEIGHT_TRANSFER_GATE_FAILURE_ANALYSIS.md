# Weight-Transfer Gate Failure Analysis

status: `HOLD_FORWARD_IMPULSE_PRIMARY`

This offline report scans compact target-source score artifacts and
summarizes which parts of `PASS_WEIGHT_TRANSFER_TARGET` are currently
binding. It does not run simulation, training, robot SSH, deployment, or
hardware tests.

## Dataset

- score artifacts: `66`
- seed rows scanned: `3896`

## Constraint Pass Rates

| constraint | threshold | observed | pass rows | pass pct | best | worst |
|---|---|---:|---:|---:|---:|---:|
| forward_velocity | `>= 0.0400` | 3779 | 23 | 0.59 | 0.1340 | -0.0960 |
| forward_displacement | `>= 0.0040` | 3275 | 2250 | 57.75 | 0.2680 | -0.2880 |
| lateral_velocity | `<= 0.1200` | 3779 | 1400 | 35.93 | 0.0234 | 0.4311 |
| body_pitch | `<= 0.3500` | 3779 | 3740 | 96.00 | 0.0031 | 0.9207 |
| base_height | `>= 0.1450` | 3779 | 3721 | 95.51 | 0.1602 | 0.0568 |
| double_support | `<= 75.0000` | 3779 | 1466 | 37.63 | 30.0000 | 100.0000 |
| single_support | `>= 20.0000` | 3779 | 1780 | 45.69 | 68.6667 | 0.0000 |
| support_balance | `>= 5.0000` | 3779 | 2160 | 55.44 | 32.6667 | 0.0000 |
| contact_transitions | `>= 2.0000` | 3779 | 3730 | 95.74 | 63.0000 | 0.0000 |
| target_velocity | `<= 3.7500` | 3779 | 3582 | 91.94 | 0.0000 | 4.2949 |
| joint_tracking | `<= 0.1200` | 3779 | 3778 | 96.97 | 0.0355 | 0.1223 |

## Combination Counts

| bucket | rows |
|---|---:|
| stable_actuator_rows | 1380 |
| support_ready_rows | 1464 |
| forward_ready_rows | 23 |
| stable_and_support_rows | 9 |
| stable_and_forward_rows | 0 |
| support_and_forward_rows | 9 |
| all_three_rows | 0 |

## Best Forward Rows Among Stable/Actuator-Safe Rows

| artifact | seed | vx | dx | double | single | min side | failures |
|---|---|---:|---:|---:|---:|---:|---|
| `foot_placement_mpc_teacher_push_probe_score_100` | `seed_002` | 0.0275 | 0.0551 | 82.00 | 18.00 | 8.00 | `forward_velocity, double_support, single_support` |
| `target_generator_single_support_probe_score_100` | `seed_002` | 0.0270 | 0.0540 | 96.00 | 4.00 | 2.00 | `forward_velocity, double_support, single_support, support_balance` |
| `target_generator_single_support_probe_score_100` | `seed_002` | 0.0267 | 0.0533 | 96.00 | 4.00 | 2.00 | `forward_velocity, double_support, single_support, support_balance` |
| `target_generator_single_support_probe_score_100` | `seed_002` | 0.0265 | 0.0531 | 96.00 | 4.00 | 2.00 | `forward_velocity, double_support, single_support, support_balance` |
| `target_generator_single_support_probe_score_100` | `seed_002` | 0.0265 | 0.0530 | 96.00 | 4.00 | 2.00 | `forward_velocity, double_support, single_support, support_balance` |

## Best Support Rows Among Stable/Actuator-Safe Rows

| artifact | seed | vx | dx | double | single | min side | failures |
|---|---|---:|---:|---:|---:|---:|---|
| `com_weight_transfer_controller_stance_aggressive_probe_score_150` | `seed_000` | -0.0009 | -0.0026 | 74.00 | 26.00 | 12.00 | `forward_velocity, forward_displacement` |
| `com_weight_transfer_controller_stance_aggressive_probe_score_150` | `seed_000` | -0.0009 | -0.0026 | 74.00 | 26.00 | 12.00 | `forward_velocity, forward_displacement` |
| `com_weight_transfer_controller_stance_reverse_push_probe_score_150` | `seed_002` | 0.0038 | 0.0113 | 74.00 | 26.00 | 12.00 | `forward_velocity` |
| `com_weight_transfer_controller_stance_reverse_push_probe_score_150` | `seed_000` | -0.0009 | -0.0026 | 74.00 | 26.00 | 12.00 | `forward_velocity, forward_displacement` |
| `com_weight_transfer_controller_support_gated_score_100` | `seed_002` | 0.0009 | 0.0017 | 73.00 | 26.00 | 9.00 | `forward_velocity, forward_displacement` |

## Closest Rows By Gate Count

| artifact | seed | pass count | vx | double | single | min side | failures |
|---|---|---:|---:|---:|---:|---:|---|
| `foot_placement_mpc_teacher_stance_relative_velocity_cap_probe_score_100` | `seed_002` | 10 | 0.0464 | 51.00 | 49.00 | 24.00 | `lateral_velocity` |
| `foot_placement_mpc_teacher_stance_relative_velocity_cap_probe_score_100` | `seed_002` | 10 | 0.0461 | 53.00 | 47.00 | 22.00 | `lateral_velocity` |
| `foot_placement_mpc_teacher_stance_relative_velocity_cap_probe_score_100` | `seed_002` | 10 | 0.0453 | 61.00 | 39.00 | 19.00 | `lateral_velocity` |
| `foot_placement_mpc_teacher_stance_relative_velocity_cap_probe_score_150` | `seed_002` | 10 | 0.0436 | 49.33 | 50.67 | 24.67 | `lateral_velocity` |
| `foot_placement_mpc_teacher_stance_relative_velocity_cap_probe_score_100` | `seed_002` | 10 | 0.0420 | 54.00 | 46.00 | 22.00 | `lateral_velocity` |
| `foot_placement_mpc_teacher_push_probe_score_100` | `seed_002` | 10 | 0.0182 | 74.00 | 26.00 | 11.00 | `forward_velocity` |
| `foot_placement_mpc_teacher_smoke_score_100` | `seed_002` | 10 | 0.0169 | 75.00 | 25.00 | 9.00 | `forward_velocity` |
| `com_weight_transfer_controller_stance_reverse_push_probe_score_150` | `seed_002` | 10 | 0.0038 | 74.00 | 26.00 | 12.00 | `forward_velocity` |
| `foot_placement_mpc_teacher_stance_relative_lateral_probe_score_100` | `seed_002` | 9 | 0.0492 | 56.00 | 44.00 | 22.00 | `lateral_velocity, target_velocity` |
| `foot_placement_mpc_teacher_stance_relative_lateral_probe_score_150` | `seed_002` | 9 | 0.0489 | 50.67 | 49.33 | 21.33 | `lateral_velocity, target_velocity` |

## Decision

```text
HOLD_FORWARD_IMPULSE_PRIMARY
```

The closest rows are generally stable and actuator-safe, but forward velocity/displacement remains far below the gate. The next target source needs an explicit propulsion mechanism after support loading, not only stronger contact alternation.
