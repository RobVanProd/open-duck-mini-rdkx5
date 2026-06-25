# Weight-Transfer Target Campaign Summary

status: `HOLD_FORWARD_LATERAL_SUPPORT_TRADEOFF`

This is an offline summary of compact target-source score artifacts. It
does not run simulation, training, robot SSH, deployment, or hardware tests.

## Score Artifacts

| label | window | status | robust | modes | top seed0 vx/dx | top seed2 vx/dx | top seed0/seed2 vy95 | top failures |
|---|---:|---|---:|---:|---:|---:|---:|---|
| `target_objective_score_weight_transfer_dynamic_roll_lateral_fix_100` | 100 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 160 | 0.0176/NA | 0.0213/NA | 0.0911/0.1076 | double_support_dominates, low_base_height, low_forward_velocity, too_little_single_support |
| `target_objective_score_weight_transfer_dynamic_roll_lateral_fix_150` | 150 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 160 | 0.0093/NA | 0.0117/NA | 0.0716/0.0736 | double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced |
| `target_objective_score_weight_transfer_probe_100` | 100 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 72 | 0.0045/NA | 0.0043/NA | 0.1018/0.0590 | low_forward_velocity |
| `target_objective_score_weight_transfer_probe_150` | 150 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 72 | 0.0018/NA | 0.0035/NA | 0.1199/0.1126 | low_forward_velocity |
| `target_objective_score_stance_push_probe_100` | 100 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 48 | 0.0089/NA | 0.0108/NA | 0.1059/0.0768 | double_support_dominates, low_forward_velocity |
| `target_objective_score_stance_push_probe_150` | 150 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 48 | 0.0028/NA | 0.0061/NA | 0.1049/0.0890 | double_support_dominates, low_forward_velocity |
| `target_objective_score_velocity_feedback_probe_100` | 100 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 32 | 0.0070/NA | 0.0061/NA | 0.1159/0.0997 | low_forward_velocity |
| `target_objective_score_velocity_feedback_probe_150` | 150 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 32 | 0.0031/NA | 0.0058/NA | 0.1027/0.0831 | double_support_dominates, low_forward_velocity |
| `closed_loop_weight_transfer_teacher_score_100` | 100 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 24 | -0.0012/NA | 0.0050/NA | 0.1172/0.1164 | double_support_dominates, low_forward_velocity, too_little_single_support |
| `closed_loop_weight_transfer_teacher_score_150` | 150 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 24 | 0.0028/NA | 0.0047/NA | 0.1512/0.1360 | double_support_dominates, high_lateral_velocity, low_forward_velocity |
| `closed_loop_weight_transfer_teacher_v2_score_100` | 100 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 32 | -0.0006/NA | 0.0002/NA | 0.0963/0.1166 | low_forward_velocity |
| `closed_loop_weight_transfer_teacher_v2_score_150` | 150 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 32 | 0.0003/NA | 0.0011/NA | 0.0928/0.1039 | double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support |
| `closed_loop_weight_transfer_teacher_v3_score_100` | 100 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 40 | 0.0104/NA | 0.0155/NA | 0.1371/0.1341 | high_lateral_velocity, low_forward_velocity |
| `closed_loop_weight_transfer_teacher_v3_score_150` | 150 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 40 | 0.0072/NA | 0.0102/NA | 0.1369/0.1416 | high_lateral_velocity, low_forward_velocity |
| `staged_weight_transfer_planner_score_100` | 100 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 30 | 0.0015/NA | 0.0034/NA | 0.1149/0.1197 | low_forward_velocity |
| `staged_weight_transfer_planner_score_150` | 150 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 30 | -0.0004/NA | 0.0004/NA | 0.0980/0.1069 | low_forward_velocity |
| `closed_loop_weight_transfer_teacher_forward_intent_score_100` | 100 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 36 | 0.0259/0.0518 | 0.0210/0.0420 | 0.1917/0.1859 | high_lateral_velocity, low_forward_velocity |
| `closed_loop_weight_transfer_teacher_forward_intent_score_150` | 150 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 36 | 0.0252/0.0757 | 0.0216/0.0648 | 0.2578/0.2530 | high_lateral_velocity, low_forward_velocity |
| `closed_loop_weight_transfer_teacher_lateral_refine_score_100` | 100 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 48 | 0.0131/0.0261 | 0.0186/0.0371 | 0.1270/0.1093 | double_support_dominates, high_lateral_velocity, low_forward_displacement, low_forward_velocity |
| `closed_loop_weight_transfer_teacher_lateral_refine_score_150` | 150 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 48 | 0.0137/0.0411 | 0.0124/0.0372 | 0.1562/0.1650 | high_lateral_velocity, low_forward_displacement, low_forward_velocity |
| `support_state_weight_transfer_probe_score_100` | 100 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 4 | 0.0137/0.0273 | 0.0115/0.0230 | 0.1479/0.1483 | high_lateral_velocity, low_forward_displacement, low_forward_velocity |
| `support_state_weight_transfer_probe_score_150` | 150 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 4 | 0.0102/0.0306 | 0.0103/0.0309 | 0.1548/0.1635 | high_lateral_velocity, low_forward_displacement, low_forward_velocity |
| `support_loaded_weight_transfer_probe_score_100` | 100 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 3 | 0.0115/0.0230 | 0.0129/0.0258 | 0.1424/0.1543 | high_lateral_velocity, low_forward_displacement, low_forward_velocity |
| `support_loaded_weight_transfer_probe_score_150` | 150 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 3 | 0.0103/0.0309 | 0.0121/0.0362 | 0.1586/0.1635 | high_lateral_velocity, low_forward_displacement, low_forward_velocity |
| `com_weight_transfer_controller_probe_score_100` | 100 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 16 | 0.0037/0.0074 | 0.0066/0.0132 | 0.0591/0.0937 | double_support_dominates, low_forward_displacement, low_forward_velocity, single_contact_pattern_dominates |
| `com_weight_transfer_controller_probe_score_150` | 150 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 16 | -0.0001/-0.0003 | 0.0030/0.0091 | 0.1008/0.1248 | double_support_dominates, high_lateral_velocity, low_forward_displacement, low_forward_velocity |
| `com_weight_transfer_controller_relaxed_probe_score_100` | 100 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 12 | 0.0044/0.0088 | 0.0060/0.0121 | 0.0621/0.0768 | double_support_dominates, low_forward_displacement, low_forward_velocity, single_contact_pattern_dominates |
| `com_weight_transfer_controller_relaxed_probe_score_150` | 150 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 12 | 0.0005/0.0015 | 0.0032/0.0096 | 0.1008/0.1195 | double_support_dominates, low_forward_displacement, low_forward_velocity, single_contact_pattern_dominates |
| `com_weight_transfer_controller_stance_probe_score_100` | 100 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 16 | 0.0073/0.0145 | 0.0065/0.0129 | 0.0568/0.0585 | low_forward_displacement, low_forward_velocity |
| `com_weight_transfer_controller_stance_probe_score_150` | 150 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 16 | -0.0004/-0.0012 | 0.0021/0.0064 | 0.0662/0.0804 | low_forward_displacement, low_forward_velocity |
| `com_weight_transfer_controller_stance_aggressive_probe_score_100` | 100 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 24 | 0.0127/0.0254 | 0.0105/0.0209 | 0.0926/0.0960 | low_forward_displacement, low_forward_velocity |
| `com_weight_transfer_controller_stance_aggressive_probe_score_150` | 150 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 24 | 0.0006/0.0018 | 0.0039/0.0117 | 0.1093/0.1238 | high_lateral_velocity, low_forward_displacement, low_forward_velocity |
| `com_weight_transfer_controller_stance_reverse_push_probe_score_100` | 100 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 16 | 0.0104/0.0209 | 0.0109/0.0218 | 0.0913/0.0865 | low_forward_displacement, low_forward_velocity |
| `com_weight_transfer_controller_stance_reverse_push_probe_score_150` | 150 | `HOLD_NO_SEED_ROBUST_TARGETS` | 0 | 16 | 0.0004/0.0013 | 0.0029/0.0088 | 0.0715/0.0887 | low_forward_displacement, low_forward_velocity |

## Aggregate Failure Counts

| reason | count |
|---|---:|
| `low_forward_velocity` | 2429 |
| `double_support_dominates` | 1439 |
| `too_little_single_support` | 1206 |
| `single_support_not_balanced` | 879 |
| `high_lateral_velocity` | 879 |
| `single_contact_pattern_dominates` | 659 |
| `low_forward_displacement` | 581 |
| `high_sent_target_velocity` | 72 |
| `too_few_contact_transitions` | 67 |
| `action_saturation` | 52 |
| `low_base_height` | 45 |
| `missing_seed_trace_or_window` | 20 |
| `high_body_pitch` | 8 |
| `short_done_margin` | 1 |
| `done_inside_window` | 1 |
| `high_tracking_error` | 1 |

## Extremes

- best top-window forward displacement: `0.0757` from `closed_loop_weight_transfer_teacher_forward_intent_score_150` / `seed_000`
- lowest top-window lateral p95: `0.0568` from `com_weight_transfer_controller_stance_probe_score_100` / `seed_000`

## Decision

```text
HOLD_FORWARD_LATERAL_SUPPORT_TRADEOFF
```

Do not use these artifacts as training permission unless the status is
`PASS_TARGET_SOURCE_AVAILABLE`. Current holds should drive a new
contact/weight-transfer objective or controller structure, not another
nearby prior-scale or teacher-grid expansion.
