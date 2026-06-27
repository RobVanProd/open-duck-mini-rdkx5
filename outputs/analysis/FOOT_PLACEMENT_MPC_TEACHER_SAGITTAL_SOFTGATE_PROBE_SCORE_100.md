# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `128`
- mode_count: `64`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `100`

## Criteria

- min_mean_vx: `0.04`
- min_forward_displacement_m: `-1.0`
- max_vy_abs_p95: `0.12`
- max_contact_dominance_pct: `95.0`
- max_double_support_pct: `100.0`
- max_no_support_pct: `100.0`
- min_single_support_pct: `0.0`
- min_each_single_support_pct: `0.0`
- max_pitch_abs_p95: `0.35`
- min_base_height: `0.145`
- max_sent_velocity_p95: `2.5`
- max_tracking_p95: `0.12`
- min_done_margin: `50`
- min_contact_transitions: `0`
- min_foot_site_z_p95: `-1.0`

## Seed Failure Counts

### seed_000
- `low_forward_velocity`: `64`
- `single_contact_pattern_dominates`: `17`
- `high_lateral_velocity`: `12`

### seed_002
- `high_lateral_velocity`: `64`
- `low_forward_velocity`: `64`
- `high_sent_target_velocity`: `43`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg0p2_pyg0p35_pms0p4_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.4636 | -0.3968 | -0.0012 | -0.0025 | 0.0162 | 0.0084 | 0.0169 | -0.0495 | 0.1474 | 0.0945 | 84.0000 | 11 | 0.0072 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.6088 | -0.4617 | 0.0028 | 0.0056 | 0.0110 | 0.0101 | 0.0201 | -0.0508 | 0.1674 | 0.0958 | 83.0000 | 16 | 0.0072 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg0p2_pyg0p35_pms0p6_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.8668 | -0.5963 | 0.0016 | 0.0032 | 0.0120 | 0.0157 | 0.0315 | -0.0369 | 0.2061 | 0.1541 | 85.0000 | 13 | 0.0074 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.9259 | -0.6309 | 0.0005 | 0.0009 | 0.0161 | 0.0078 | 0.0155 | -0.0530 | 0.2045 | 0.0584 | 77.0000 | 25 | 0.0063 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.9474 | -0.6420 | -0.0021 | -0.0041 | 0.0339 | 0.0091 | 0.0183 | -0.0694 | 0.2087 | 0.1440 | 63.0000 | 33 | 0.0070 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.9668 | -0.6333 | 0.0022 | 0.0045 | 0.0294 | 0.0061 | 0.0122 | -0.0485 | 0.2077 | 0.1301 | 69.0000 | 20 | 0.0070 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.9888 | -0.6627 | -0.0021 | -0.0042 | 0.0336 | 0.0062 | 0.0123 | -0.0624 | 0.2105 | 0.1436 | 67.0000 | 16 | 0.0067 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.0361 | -0.6460 | 0.0071 | 0.0142 | 0.0037 | 0.0099 | 0.0199 | -0.0590 | 0.2207 | 0.0646 | 69.0000 | 22 | 0.0067 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.0798 | -0.6804 | 0.0054 | 0.0108 | 0.0065 | 0.0129 | 0.0258 | -0.0712 | 0.2295 | 0.0823 | 73.0000 | 23 | 0.0066 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1370 | -0.6959 | 0.0072 | 0.0145 | -0.0030 | 0.0125 | 0.0250 | -0.0501 | 0.2362 | 0.0872 | 70.0000 | 21 | 0.0072 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1385 | -0.7294 | -0.0000 | -0.0001 | 0.0115 | 0.0055 | 0.0109 | -0.0657 | 0.2285 | 0.0627 | 74.0000 | 20 | 0.0063 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1632 | -0.7723 | -0.0032 | -0.0063 | 0.0257 | 0.0085 | 0.0170 | -0.0756 | 0.2350 | 0.0733 | 75.0000 | 18 | 0.0067 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2023 | -0.7681 | -0.0017 | -0.0035 | 0.0354 | 0.0110 | 0.0220 | -0.0699 | 0.2427 | 0.1257 | 69.0000 | 21 | 0.0064 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2162 | -0.7677 | 0.0045 | 0.0090 | -0.0058 | 0.0015 | 0.0030 | -0.0528 | 0.2337 | 0.0646 | 70.0000 | 20 | 0.0070 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg0p2_pyg0p35_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2199 | -0.7648 | 0.0011 | 0.0023 | 0.0144 | 0.0106 | 0.0213 | -0.0602 | 0.2046 | 0.1546 | 55.0000 | 31 | 0.0091 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2367 | -0.7565 | 0.0049 | 0.0097 | 0.0072 | 0.0097 | 0.0194 | -0.0695 | 0.2455 | 0.1228 | 71.0000 | 16 | 0.0065 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2558 | -0.7791 | 0.0019 | 0.0039 | -0.0017 | 0.0103 | 0.0206 | -0.0714 | 0.2348 | 0.0456 | 62.0000 | 24 | 0.0064 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg0p2_pyg0p35_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.3335 | -0.8510 | 0.0012 | 0.0025 | 0.0073 | 0.0026 | 0.0052 | -0.0637 | 0.2366 | 0.0963 | 71.0000 | 21 | 0.0060 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.3341 | -0.8013 | 0.0057 | 0.0115 | -0.0028 | 0.0037 | 0.0074 | -0.0622 | 0.2509 | 0.0309 | 68.0000 | 21 | 0.0062 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg0p2_pyg0p35_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.3458 | -0.8404 | 0.0094 | 0.0189 | -0.0062 | 0.0156 | 0.0312 | -0.0528 | 0.2247 | 0.1565 | 73.0000 | 19 | 0.0070 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.3484 | -0.8062 | 0.0081 | 0.0162 | -0.0062 | 0.0056 | 0.0111 | -0.0633 | 0.2395 | 0.0502 | 64.0000 | 25 | 0.0062 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.3513 | -0.8484 | -0.0032 | -0.0064 | 0.0175 | 0.0045 | 0.0089 | -0.0667 | 0.2539 | 0.0835 | 75.0000 | 18 | 0.0073 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg0p2_pyg0p35_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.3790 | -0.8602 | 0.0087 | 0.0175 | -0.0043 | 0.0176 | 0.0351 | -0.0458 | 0.2210 | 0.1619 | 71.0000 | 24 | 0.0065 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4075 | -0.8388 | 0.0055 | 0.0111 | -0.0044 | 0.0198 | 0.0395 | -0.0827 | 0.2393 | 0.0827 | 54.0000 | 32 | 0.0072 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg0p2_pyg0p35_pms0p4_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4437 | -0.8945 | 0.0083 | 0.0166 | -0.0035 | 0.0166 | 0.0331 | -0.0564 | 0.2520 | 0.1721 | 70.0000 | 24 | 0.0088 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
