# Weight-Transfer Target Gate Check

status: `HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET`

This is an executable offline check of the documented
`PASS_WEIGHT_TRANSFER_TARGET` gate. It reads compact score artifacts only;
it does not run simulation, training, robot SSH, deployment, or hardware tests.

## Gate Criteria

| metric | threshold |
|---|---:|
| `required_seeds` | `['0', '2']` |
| `min_mean_vx` | `0.04` |
| `min_forward_displacement_m` | `0.004` |
| `max_vy_abs_p95` | `0.12` |
| `max_pitch_abs_p95` | `0.35` |
| `min_base_height` | `0.145` |
| `max_double_support_pct` | `75.0` |
| `min_single_support_pct` | `20.0` |
| `min_each_single_support_pct` | `5.0` |
| `min_contact_transitions` | `2` |
| `max_sent_velocity_p95` | `3.75` |
| `max_tracking_p95` | `0.12` |

## Inputs

| artifact | status | window | robust | checked | pass |
|---|---|---:|---:|---:|---:|
| `closed_loop_weight_transfer_teacher_forward_intent_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `closed_loop_weight_transfer_teacher_forward_intent_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `closed_loop_weight_transfer_teacher_lateral_refine_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `closed_loop_weight_transfer_teacher_lateral_refine_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `closed_loop_weight_transfer_teacher_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `closed_loop_weight_transfer_teacher_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `closed_loop_weight_transfer_teacher_v2_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `closed_loop_weight_transfer_teacher_v2_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `closed_loop_weight_transfer_teacher_v3_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `closed_loop_weight_transfer_teacher_v3_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `com_weight_transfer_controller_probe_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `com_weight_transfer_controller_probe_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `com_weight_transfer_controller_relaxed_probe_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `com_weight_transfer_controller_relaxed_probe_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `com_weight_transfer_controller_sagittal_probe_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `com_weight_transfer_controller_sagittal_probe_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `com_weight_transfer_controller_stance_aggressive_probe_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `com_weight_transfer_controller_stance_aggressive_probe_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `com_weight_transfer_controller_stance_probe_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `com_weight_transfer_controller_stance_probe_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `com_weight_transfer_controller_stance_reverse_push_probe_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `com_weight_transfer_controller_stance_reverse_push_probe_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `com_weight_transfer_controller_stateful_strict_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `com_weight_transfer_controller_stateful_strict_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `com_weight_transfer_controller_stateful_timeout_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `com_weight_transfer_controller_stateful_timeout_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `com_weight_transfer_controller_support_gated_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `com_weight_transfer_controller_support_gated_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `score` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `staged_weight_transfer_planner_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `staged_weight_transfer_planner_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `support_loaded_weight_transfer_probe_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `support_loaded_weight_transfer_probe_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `support_state_weight_transfer_probe_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `support_state_weight_transfer_probe_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `target_generator_single_support_probe_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `target_generator_single_support_probe_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |

## Top Candidates

| artifact | mode | pass | min score | seed | vx | dx | double | single | min side | failures |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---|
| `staged_weight_transfer_planner_score_100` | `planner_p0p56_bf0p55_rs0p06_lg0p1_byg0p06_pg0p12_sk0p16_sa0p02_shr0p09_srs0p5_spg1p5_pt0_pd1_lfgm1_bygf0p5` | no | -0.3064 | `0` | 0.0015 | NA | 89.00 | 11.00 | 4.00 | `low_forward_velocity, low_forward_displacement:missing, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `staged_weight_transfer_planner_score_100` | `planner_p0p56_bf0p55_rs0p06_lg0p1_byg0p06_pg0p12_sk0p16_sa0p02_shr0p09_srs0p5_spg1p5_pt0_pd1_lfgm1_bygf0p5` | no | -0.3064 | `2` | 0.0034 | NA | 85.00 | 15.00 | 7.00 | `low_forward_velocity, low_forward_displacement:missing, double_support_dominates, too_little_single_support` |
| `staged_weight_transfer_planner_score_100` | `planner_p0p64_bf0p25_rs0p06_lg0p1_byg0p06_pg0p18_sk0p08_sa0p02_shr0p03_srs0p5_spg0p5_pt0p03_pd2_lfgm1_bygfm0p5` | no | -0.3077 | `0` | 0.0014 | NA | 89.00 | 10.00 | 2.00 | `low_forward_velocity, low_forward_displacement:missing, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `staged_weight_transfer_planner_score_100` | `planner_p0p64_bf0p25_rs0p06_lg0p1_byg0p06_pg0p18_sk0p08_sa0p02_shr0p03_srs0p5_spg0p5_pt0p03_pd2_lfgm1_bygfm0p5` | no | -0.3077 | `2` | 0.0035 | NA | 83.00 | 16.00 | 7.00 | `low_forward_velocity, low_forward_displacement:missing, double_support_dominates, too_little_single_support` |
| `staged_weight_transfer_planner_score_100` | `planner_p0p64_bf0p4_rs0p02_lg0p06_byg0p06_pg0p24_sk0p16_sa0_shr0p03_srs0p5_spg1_pt0_pd1_lfg1_bygf0p5` | no | -0.3212 | `0` | 0.0012 | NA | 89.00 | 11.00 | 2.00 | `low_forward_velocity, low_forward_displacement:missing, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `staged_weight_transfer_planner_score_100` | `planner_p0p64_bf0p4_rs0p02_lg0p06_byg0p06_pg0p24_sk0p16_sa0_shr0p03_srs0p5_spg1_pt0_pd1_lfg1_bygf0p5` | no | -0.3212 | `2` | -0.0002 | NA | 83.00 | 17.00 | 6.00 | `low_forward_velocity, low_forward_displacement:missing, double_support_dominates, too_little_single_support` |
| `staged_weight_transfer_planner_score_150` | `planner_p0p64_bf0p25_rs0p06_lg0p1_byg0p06_pg0p18_sk0p08_sa0p02_shr0p03_srs0p5_spg0p5_pt0p03_pd2_lfgm1_bygfm0p5` | no | -0.3236 | `0` | -0.0004 | NA | 88.67 | 10.67 | 4.67 | `low_forward_velocity, low_forward_displacement:missing, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `staged_weight_transfer_planner_score_150` | `planner_p0p64_bf0p25_rs0p06_lg0p1_byg0p06_pg0p18_sk0p08_sa0p02_shr0p03_srs0p5_spg0p5_pt0p03_pd2_lfgm1_bygfm0p5` | no | -0.3236 | `2` | 0.0004 | NA | 82.67 | 16.67 | 7.33 | `low_forward_velocity, low_forward_displacement:missing, double_support_dominates, too_little_single_support` |
| `staged_weight_transfer_planner_score_150` | `planner_p0p56_bf0p25_rs0p06_lg0p1_byg0p02_pg0p24_sk0p08_sa0_shr0p09_srs1_spg0p5_ptm0p03_pd2_lfgm1_bygf0p5` | no | -0.3236 | `0` | -0.0005 | NA | 88.67 | 11.33 | 4.67 | `low_forward_velocity, low_forward_displacement:missing, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `staged_weight_transfer_planner_score_150` | `planner_p0p56_bf0p25_rs0p06_lg0p1_byg0p02_pg0p24_sk0p08_sa0_shr0p09_srs1_spg0p5_ptm0p03_pd2_lfgm1_bygf0p5` | no | -0.3236 | `2` | 0.0017 | NA | 85.33 | 14.00 | 4.00 | `low_forward_velocity, low_forward_displacement:missing, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `closed_loop_weight_transfer_teacher_v2_score_100` | `teacher_p0p56_rs0p04_sk0p08_sa0_spg1p5_pd1_lg0p5_byg0p5_plg0p12_clb0` | no | -0.3248 | `0` | -0.0006 | NA | 89.00 | 11.00 | 5.00 | `low_forward_velocity, low_forward_displacement:missing, double_support_dominates, too_little_single_support` |
| `closed_loop_weight_transfer_teacher_v2_score_100` | `teacher_p0p56_rs0p04_sk0p08_sa0_spg1p5_pd1_lg0p5_byg0p5_plg0p12_clb0` | no | -0.3248 | `2` | 0.0002 | NA | 90.00 | 10.00 | 4.00 | `low_forward_velocity, low_forward_displacement:missing, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `closed_loop_weight_transfer_teacher_v2_score_100` | `teacher_p0p56_rs0p04_sk0p08_sam0p02_spg1_pd1_lg1_bygm1_plg0p12_clb0` | no | -0.3594 | `0` | -0.0024 | NA | 91.00 | 9.00 | 3.00 | `low_forward_velocity, low_forward_displacement:missing, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `closed_loop_weight_transfer_teacher_v2_score_100` | `teacher_p0p56_rs0p04_sk0p08_sam0p02_spg1_pd1_lg1_bygm1_plg0p12_clb0` | no | -0.3594 | `2` | 0.0011 | NA | 84.00 | 16.00 | 8.00 | `low_forward_velocity, low_forward_displacement:missing, high_lateral_velocity, double_support_dominates, too_little_single_support` |
| `closed_loop_weight_transfer_teacher_v3_score_100` | `teacher_p0p48_rs0p04_sk0p08_sam0p02_shr0p06_srs1_spg1p5_pt0p06_pd2_lgm1_byg0_plg0p06_clb0p5` | no | -0.3636 | `0` | 0.0104 | NA | 88.00 | 12.00 | 3.00 | `low_forward_velocity, low_forward_displacement:missing, high_lateral_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `closed_loop_weight_transfer_teacher_v3_score_100` | `teacher_p0p48_rs0p04_sk0p08_sam0p02_shr0p06_srs1_spg1p5_pt0p06_pd2_lgm1_byg0_plg0p06_clb0p5` | no | -0.3636 | `2` | 0.0155 | NA | 88.00 | 12.00 | 3.00 | `low_forward_velocity, low_forward_displacement:missing, high_lateral_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |

## Decision

```text
HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET
```

No checked target source currently proves sustained, seed-robust weight transfer. Do not use these artifacts as permission for BC/PPO or robot validation.
