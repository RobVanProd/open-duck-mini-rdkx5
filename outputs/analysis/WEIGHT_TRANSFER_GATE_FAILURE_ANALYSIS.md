# Weight-Transfer Gate Failure Analysis

status: `HOLD_FORWARD_IMPULSE_PRIMARY`

This offline report scans compact target-source score artifacts and
summarizes which parts of `PASS_WEIGHT_TRANSFER_TARGET` are currently
binding. It does not run simulation, training, robot SSH, deployment, or
hardware tests.

## Dataset

- score artifacts: `37`
- seed rows scanned: `1884`

## Constraint Pass Rates

| constraint | threshold | observed | pass rows | pass pct | best | worst |
|---|---|---:|---:|---:|---:|---:|
| forward_velocity | `>= 0.0400` | 1798 | 15 | 0.80 | 0.1340 | -0.0066 |
| forward_displacement | `>= 0.0040` | 1294 | 724 | 38.43 | 0.2680 | -0.0159 |
| lateral_velocity | `<= 0.1200` | 1798 | 984 | 52.23 | 0.0234 | 0.4311 |
| body_pitch | `<= 0.3500` | 1798 | 1773 | 94.11 | 0.0031 | 0.9207 |
| base_height | `>= 0.1450` | 1798 | 1745 | 92.62 | 0.1602 | 0.0734 |
| double_support | `<= 75.0000` | 1798 | 439 | 23.30 | 36.0000 | 100.0000 |
| single_support | `>= 20.0000` | 1798 | 626 | 33.23 | 64.0000 | 0.0000 |
| support_balance | `>= 5.0000` | 1798 | 850 | 45.12 | 30.6667 | 0.0000 |
| contact_transitions | `>= 2.0000` | 1798 | 1778 | 94.37 | 56.0000 | 0.0000 |
| target_velocity | `<= 3.7500` | 1798 | 1789 | 94.96 | 0.0000 | 4.2949 |
| joint_tracking | `<= 0.1200` | 1798 | 1797 | 95.38 | 0.0375 | 0.1223 |

## Combination Counts

| bucket | rows |
|---|---:|
| stable_actuator_rows | 964 |
| support_ready_rows | 437 |
| forward_ready_rows | 15 |
| stable_and_support_rows | 7 |
| stable_and_forward_rows | 0 |
| support_and_forward_rows | 1 |
| all_three_rows | 0 |

## Best Forward Rows Among Stable/Actuator-Safe Rows

| artifact | seed | vx | dx | double | single | min side | failures |
|---|---|---:|---:|---:|---:|---:|---|
| `target_generator_single_support_probe_score_100` | `seed_002` | 0.0270 | 0.0540 | 96.00 | 4.00 | 2.00 | `forward_velocity, double_support, single_support, support_balance` |
| `target_generator_single_support_probe_score_100` | `seed_002` | 0.0267 | 0.0533 | 96.00 | 4.00 | 2.00 | `forward_velocity, double_support, single_support, support_balance` |
| `target_generator_single_support_probe_score_100` | `seed_002` | 0.0265 | 0.0531 | 96.00 | 4.00 | 2.00 | `forward_velocity, double_support, single_support, support_balance` |
| `target_generator_single_support_probe_score_100` | `seed_002` | 0.0265 | 0.0530 | 96.00 | 4.00 | 2.00 | `forward_velocity, double_support, single_support, support_balance` |
| `target_generator_single_support_probe_score_100` | `seed_002` | 0.0264 | 0.0527 | 96.00 | 4.00 | 2.00 | `forward_velocity, double_support, single_support, support_balance` |

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
| `com_weight_transfer_controller_stance_reverse_push_probe_score_150` | `seed_002` | 10 | 0.0038 | 74.00 | 26.00 | 12.00 | `forward_velocity` |
| `closed_loop_weight_transfer_teacher_lateral_refine_score_100` | `seed_002` | 9 | 0.0425 | 66.00 | 34.00 | 7.00 | `lateral_velocity, body_pitch` |
| `closed_loop_weight_transfer_teacher_forward_intent_score_100` | `seed_002` | 9 | 0.0395 | 62.00 | 38.00 | 14.00 | `forward_velocity, lateral_velocity` |
| `closed_loop_weight_transfer_teacher_forward_intent_score_100` | `seed_002` | 9 | 0.0346 | 53.00 | 47.00 | 14.00 | `forward_velocity, lateral_velocity` |
| `closed_loop_weight_transfer_teacher_forward_intent_score_100` | `seed_000` | 9 | 0.0345 | 67.00 | 33.00 | 9.00 | `forward_velocity, lateral_velocity` |
| `closed_loop_weight_transfer_teacher_forward_intent_score_100` | `seed_002` | 9 | 0.0343 | 43.00 | 57.00 | 17.00 | `forward_velocity, lateral_velocity` |
| `closed_loop_weight_transfer_teacher_forward_intent_score_150` | `seed_002` | 9 | 0.0336 | 43.33 | 56.67 | 18.00 | `forward_velocity, lateral_velocity` |
| `closed_loop_weight_transfer_teacher_forward_intent_score_100` | `seed_002` | 9 | 0.0335 | 69.00 | 31.00 | 7.00 | `forward_velocity, lateral_velocity` |
| `closed_loop_weight_transfer_teacher_forward_intent_score_150` | `seed_002` | 9 | 0.0325 | 55.33 | 44.67 | 14.67 | `forward_velocity, lateral_velocity` |
| `closed_loop_weight_transfer_teacher_forward_intent_score_150` | `seed_002` | 9 | 0.0316 | 59.33 | 40.67 | 16.67 | `forward_velocity, lateral_velocity` |

## Decision

```text
HOLD_FORWARD_IMPULSE_PRIMARY
```

The closest rows are generally stable and actuator-safe, but forward velocity/displacement remains far below the gate. The next target source needs an explicit propulsion mechanism after support loading, not only stronger contact alternation.
