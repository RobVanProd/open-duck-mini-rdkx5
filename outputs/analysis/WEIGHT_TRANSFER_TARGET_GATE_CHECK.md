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
| `foot_placement_mpc_teacher_advance_probe_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_advance_probe_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_advance_wide_probe_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_advance_wide_probe_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_clearance_probe_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_clearance_probe_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_orientation_smoke_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 2 | 0 |
| `foot_placement_mpc_teacher_push_probe_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_push_probe_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_relative_yaw_recovery_probe_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_relative_yaw_recovery_probe_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_sagittal_propulsion_probe_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_sagittal_propulsion_probe_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_sagittal_softgate_probe_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_sagittal_softgate_probe_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_smoke_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_smoke_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_smoke_v3_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_smoke_v3_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_stability_probe_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_stability_probe_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_yaw_support_probe_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 3 | 0 |
| `foot_placement_mpc_teacher_yaw_support_probe_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 3 | 0 |
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
| `foot_placement_mpc_teacher_advance_wide_probe_score_100` | `fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5` | no | -0.2301 | `0` | 0.0100 | 0.0200 | 94.00 | 6.00 | 2.00 | `low_forward_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `foot_placement_mpc_teacher_advance_wide_probe_score_100` | `fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5` | no | -0.2301 | `2` | 0.0136 | 0.0272 | 88.00 | 12.00 | 5.00 | `low_forward_velocity, double_support_dominates, too_little_single_support` |
| `foot_placement_mpc_teacher_sagittal_propulsion_probe_score_100` | `fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg0p8_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5` | no | -0.2623 | `0` | 0.0064 | 0.0128 | 87.00 | 13.00 | 4.00 | `low_forward_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `foot_placement_mpc_teacher_sagittal_propulsion_probe_score_100` | `fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg0p8_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5` | no | -0.2623 | `2` | 0.0106 | 0.0212 | 90.00 | 10.00 | 3.00 | `low_forward_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `foot_placement_mpc_teacher_advance_wide_probe_score_100` | `fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5` | no | -0.2781 | `0` | 0.0107 | 0.0213 | 84.00 | 16.00 | 7.00 | `low_forward_velocity, high_lateral_velocity, double_support_dominates, too_little_single_support` |
| `foot_placement_mpc_teacher_advance_wide_probe_score_100` | `fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5` | no | -0.2781 | `2` | 0.0064 | 0.0129 | 88.00 | 12.00 | 5.00 | `low_forward_velocity, double_support_dominates, too_little_single_support` |
| `foot_placement_mpc_teacher_stability_probe_score_100` | `fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5` | no | -0.2791 | `0` | 0.0045 | 0.0091 | 94.00 | 6.00 | 2.00 | `low_forward_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `foot_placement_mpc_teacher_stability_probe_score_100` | `fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5` | no | -0.2791 | `2` | 0.0053 | 0.0106 | 92.00 | 8.00 | 2.00 | `low_forward_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `foot_placement_mpc_teacher_stability_probe_score_100` | `fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5` | no | -0.2791 | `0` | 0.0045 | 0.0091 | 94.00 | 6.00 | 2.00 | `low_forward_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `foot_placement_mpc_teacher_stability_probe_score_100` | `fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5` | no | -0.2791 | `2` | 0.0053 | 0.0106 | 92.00 | 8.00 | 2.00 | `low_forward_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `foot_placement_mpc_teacher_stability_probe_score_100` | `fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5` | no | -0.2796 | `0` | 0.0045 | 0.0090 | 94.00 | 6.00 | 2.00 | `low_forward_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `foot_placement_mpc_teacher_stability_probe_score_100` | `fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5` | no | -0.2796 | `2` | 0.0081 | 0.0162 | 92.00 | 8.00 | 2.00 | `low_forward_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `foot_placement_mpc_teacher_stability_probe_score_150` | `fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p5_rg1p5_vyg0p5_byg0p5` | no | -0.2864 | `0` | 0.0037 | 0.0112 | 94.67 | 5.33 | 0.67 | `low_forward_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `foot_placement_mpc_teacher_stability_probe_score_150` | `fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p5_rg1p5_vyg0p5_byg0p5` | no | -0.2864 | `2` | 0.0037 | 0.0112 | 92.00 | 8.00 | 4.00 | `low_forward_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `foot_placement_mpc_teacher_stability_probe_score_150` | `fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p5_rg1p5_vyg0p5_byg0p5` | no | -0.2864 | `0` | 0.0037 | 0.0112 | 94.67 | 5.33 | 0.67 | `low_forward_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `foot_placement_mpc_teacher_stability_probe_score_150` | `fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p5_rg1p5_vyg0p5_byg0p5` | no | -0.2864 | `2` | 0.0037 | 0.0112 | 92.00 | 8.00 | 4.00 | `low_forward_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |

## Decision

```text
HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET
```

No checked target source currently proves sustained, seed-robust weight transfer. Do not use these artifacts as permission for BC/PPO or robot validation.
