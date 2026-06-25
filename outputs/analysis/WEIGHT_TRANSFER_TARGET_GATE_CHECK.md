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
| `closed_loop_weight_transfer_teacher_leg_extension_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `closed_loop_weight_transfer_teacher_leg_extension_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
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
| `contact_weight_transfer_sequence_optimizer_smoke_iteration_00_score` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_smoke_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_smoke_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_smoke_v3_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_smoke_v3_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
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
| `foot_placement_mpc_teacher_smoke_v3_score_100` | `fpm_ism1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sapm0p02_rg1p5_vyg0p5_byg0p5` | no | -0.3138 | `0` | 0.0007 | 0.0014 | 95.00 | 5.00 | 2.00 | `low_forward_velocity, low_forward_displacement, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `foot_placement_mpc_teacher_smoke_v3_score_100` | `fpm_ism1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sapm0p02_rg1p5_vyg0p5_byg0p5` | no | -0.3138 | `2` | 0.0165 | 0.0329 | 84.00 | 16.00 | 6.00 | `low_forward_velocity, double_support_dominates, too_little_single_support` |
| `foot_placement_mpc_teacher_smoke_v3_score_100` | `fpm_ism1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sapm0p02_rg1p5_vyg1_byg0p5` | no | -0.3167 | `0` | 0.0004 | 0.0007 | 93.00 | 6.00 | 3.00 | `low_forward_velocity, low_forward_displacement, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `foot_placement_mpc_teacher_smoke_v3_score_100` | `fpm_ism1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sapm0p02_rg1p5_vyg1_byg0p5` | no | -0.3167 | `2` | 0.0164 | 0.0327 | 78.00 | 22.00 | 9.00 | `low_forward_velocity, double_support_dominates` |
| `foot_placement_mpc_teacher_smoke_v3_score_100` | `fpm_is1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sap0p02_rg1p5_vyg1_byg0p5` | no | -0.3197 | `0` | 0.0000 | 0.0001 | 95.00 | 5.00 | 2.00 | `low_forward_velocity, low_forward_displacement, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `foot_placement_mpc_teacher_smoke_v3_score_100` | `fpm_is1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sap0p02_rg1p5_vyg1_byg0p5` | no | -0.3197 | `2` | 0.0137 | 0.0275 | 88.00 | 12.00 | 5.00 | `low_forward_velocity, double_support_dominates, too_little_single_support` |
| `staged_weight_transfer_planner_score_100` | `planner_p0p64_bf0p4_rs0p02_lg0p06_byg0p06_pg0p24_sk0p16_sa0_shr0p03_srs0p5_spg1_pt0_pd1_lfg1_bygf0p5` | no | -0.3212 | `0` | 0.0012 | NA | 89.00 | 11.00 | 2.00 | `low_forward_velocity, low_forward_displacement:missing, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `staged_weight_transfer_planner_score_100` | `planner_p0p64_bf0p4_rs0p02_lg0p06_byg0p06_pg0p24_sk0p16_sa0_shr0p03_srs0p5_spg1_pt0_pd1_lfg1_bygf0p5` | no | -0.3212 | `2` | -0.0002 | NA | 83.00 | 17.00 | 6.00 | `low_forward_velocity, low_forward_displacement:missing, double_support_dominates, too_little_single_support` |
| `foot_placement_mpc_teacher_smoke_v3_score_150` | `fpm_is1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sap0p02_rg1p5_vyg1_byg0p5` | no | -0.3236 | `0` | 0.0003 | 0.0010 | 95.33 | 4.67 | 1.33 | `low_forward_velocity, low_forward_displacement, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `foot_placement_mpc_teacher_smoke_v3_score_150` | `fpm_is1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sap0p02_rg1p5_vyg1_byg0p5` | no | -0.3236 | `2` | 0.0127 | 0.0382 | 81.33 | 18.67 | 8.67 | `low_forward_velocity, double_support_dominates, too_little_single_support` |
| `staged_weight_transfer_planner_score_150` | `planner_p0p64_bf0p25_rs0p06_lg0p1_byg0p06_pg0p18_sk0p08_sa0p02_shr0p03_srs0p5_spg0p5_pt0p03_pd2_lfgm1_bygfm0p5` | no | -0.3236 | `0` | -0.0004 | NA | 88.67 | 10.67 | 4.67 | `low_forward_velocity, low_forward_displacement:missing, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `staged_weight_transfer_planner_score_150` | `planner_p0p64_bf0p25_rs0p06_lg0p1_byg0p06_pg0p18_sk0p08_sa0p02_shr0p03_srs0p5_spg0p5_pt0p03_pd2_lfgm1_bygfm0p5` | no | -0.3236 | `2` | 0.0004 | NA | 82.67 | 16.67 | 7.33 | `low_forward_velocity, low_forward_displacement:missing, double_support_dominates, too_little_single_support` |

## Decision

```text
HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET
```

No checked target source currently proves sustained, seed-robust weight transfer. Do not use these artifacts as permission for BC/PPO or robot validation.
