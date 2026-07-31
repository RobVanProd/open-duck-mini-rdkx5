# Weight-Transfer Target Gate Check

status: `HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET`

This is an executable offline check of the documented
`PASS_WEIGHT_TRANSFER_TARGET` gate. It reads compact score artifacts only;
it does not run simulation, training, robot SSH, deployment, or hardware tests.

## Gate Criteria

| metric | threshold |
|---|---:|
| `required_seeds` | `['2', '4']` |
| `min_mean_vx` | `0.04` |
| `min_forward_displacement_m` | `0.004` |
| `max_vy_abs_p95` | `0.12` |
| `max_pitch_abs_p95` | `0.35` |
| `min_base_height` | `0.145` |
| `max_double_support_pct` | `75.0` |
| `min_single_support_pct` | `20.0` |
| `min_each_single_support_pct` | `5.0` |
| `min_contact_transitions` | `2` |
| `max_sent_velocity_p95` | `2.5` |
| `max_tracking_p95` | `0.2` |

## Inputs

| artifact | status | window | robust | checked | pass |
|---|---|---:|---:|---:|---:|
| `phase2_foot_placement_mpc_rough_preflight_score_100` | `HOLD_NO_SEED_ROBUST_TARGETS` | 100 | 0 | 2 | 0 |
| `phase2_foot_placement_mpc_rough_preflight_score_150` | `HOLD_NO_SEED_ROBUST_TARGETS` | 150 | 0 | 2 | 0 |

## Top Candidates

| artifact | mode | pass | min score | seed | vx | dx | double | single | min side | failures |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---|
| `phase2_foot_placement_mpc_rough_preflight_score_100` | `fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p005_shp0p02_skp0_sap0p02_sbx0_sg0_vxg0_pl0_pp1_tvl2p5_plg0p1_pyg0p1_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5` | no | -1.7920 | `2` | 0.0046 | 0.0092 | 91.00 | 9.00 | 2.00 | `low_forward_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `phase2_foot_placement_mpc_rough_preflight_score_100` | `fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p005_shp0p02_skp0_sap0p02_sbx0_sg0_vxg0_pl0_pp1_tvl2p5_plg0p1_pyg0p1_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5` | no | -1.7920 | `4` | 0.0047 | 0.0093 | 98.00 | 2.00 | 0.00 | `low_forward_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `phase2_foot_placement_mpc_rough_preflight_score_150` | `fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p005_shp0p02_skp0_sap0p02_sbx0_sg0_vxg0_pl0_pp1_tvl2p5_plg0p1_pyg0p1_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5` | no | -1.8473 | `2` | 0.0079 | 0.0236 | 94.00 | 6.00 | 1.33 | `low_forward_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `phase2_foot_placement_mpc_rough_preflight_score_150` | `fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p005_shp0p02_skp0_sap0p02_sbx0_sg0_vxg0_pl0_pp1_tvl2p5_plg0p1_pyg0p1_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5` | no | -1.8473 | `4` | 0.0030 | 0.0089 | 98.67 | 1.33 | 0.00 | `low_forward_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `phase2_foot_placement_mpc_rough_preflight_score_100` | `fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p005_shp0p02_skp0_sap0p02_sbx0_sg0_vxg0_pl0_pp1_tvl2p5_plg0p1_pyg0p1_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5` | no | -2.2681 | `2` | 0.0061 | 0.0121 | 94.00 | 6.00 | 2.00 | `low_forward_velocity, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `phase2_foot_placement_mpc_rough_preflight_score_100` | `fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p005_shp0p02_skp0_sap0p02_sbx0_sg0_vxg0_pl0_pp1_tvl2p5_plg0p1_pyg0p1_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5` | no | -2.2681 | `4` | -0.0255 | -0.0510 | 97.00 | 3.00 | 1.00 | `low_forward_velocity, low_forward_displacement, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `phase2_foot_placement_mpc_rough_preflight_score_150` | `fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p005_shp0p02_skp0_sap0p02_sbx0_sg0_vxg0_pl0_pp1_tvl2p5_plg0p1_pyg0p1_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5` | no | -999.0000 | `2` | -0.0010 | -0.0031 | 94.67 | 5.33 | 2.00 | `low_forward_velocity, low_forward_displacement, double_support_dominates, too_little_single_support, single_support_not_balanced` |
| `phase2_foot_placement_mpc_rough_preflight_score_150` | `fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p005_shp0p02_skp0_sap0p02_sbx0_sg0_vxg0_pl0_pp1_tvl2p5_plg0p1_pyg0p1_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5` | no | -999.0000 | `4` | NA | NA | NA | NA | NA | `low_forward_velocity:missing, low_forward_displacement:missing, high_lateral_velocity:missing, high_body_pitch:missing, low_base_height:missing, double_support_dominates:missing, too_little_single_support:missing, single_support_not_balanced:missing, too_few_contact_transitions:missing, high_sent_target_velocity:missing, high_tracking_error:missing` |

## Decision

```text
HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET
```

No checked target source currently proves sustained, seed-robust weight transfer. Do not use these artifacts as permission for BC/PPO or robot validation.
