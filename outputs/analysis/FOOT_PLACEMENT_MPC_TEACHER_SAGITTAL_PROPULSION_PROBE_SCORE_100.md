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
- `single_contact_pattern_dominates`: `12`
- `high_lateral_velocity`: `2`

### seed_002
- `low_forward_velocity`: `64`
- `high_lateral_velocity`: `63`
- `high_sent_target_velocity`: `37`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg0p8_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.2623 | -0.2434 | 0.0064 | 0.0128 | 0.0041 | 0.0106 | 0.0212 | -0.0428 | 0.1159 | 0.1209 | 90.0000 | 4 | 0.0078 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg0p8_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.5477 | -0.4195 | 0.0032 | 0.0064 | 0.0125 | 0.0123 | 0.0247 | -0.0524 | 0.1623 | 0.1003 | 78.0000 | 19 | 0.0073 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg0p8_vxg0p5_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.5982 | -0.4673 | -0.0020 | -0.0041 | 0.0341 | 0.0058 | 0.0115 | -0.0401 | 0.1613 | 0.0619 | 82.0000 | 10 | 0.0088 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.6529 | -0.4720 | 0.0032 | 0.0064 | 0.0125 | 0.0115 | 0.0229 | -0.0522 | 0.1745 | 0.1168 | 78.0000 | 16 | 0.0068 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg0p5_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.6960 | -0.4841 | 0.0053 | 0.0106 | 0.0110 | 0.0107 | 0.0215 | -0.0563 | 0.1791 | 0.0904 | 77.0000 | 14 | 0.0070 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg0p8_vxg0p5_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.7640 | -0.5488 | -0.0017 | -0.0034 | 0.0339 | 0.0092 | 0.0183 | -0.0565 | 0.1858 | 0.2690 | 77.0000 | 16 | 0.0083 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg0p5_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.7660 | -0.5405 | 0.0050 | 0.0100 | 0.0088 | -0.0035 | -0.0070 | -0.0199 | 0.1722 | 0.1343 | 81.0000 | 19 | 0.0108 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg0p8_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.7684 | -0.5517 | -0.0019 | -0.0037 | 0.0332 | 0.0039 | 0.0078 | -0.0329 | 0.1805 | 0.0714 | 86.0000 | 8 | 0.0082 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.7953 | -0.5327 | 0.0055 | 0.0111 | 0.0091 | -0.0003 | -0.0006 | -0.0335 | 0.1791 | 0.1707 | 83.0000 | 14 | 0.0076 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg0p5_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.8297 | -0.5671 | 0.0017 | 0.0034 | 0.0145 | 0.0099 | 0.0197 | -0.0570 | 0.1948 | 0.1209 | 80.0000 | 13 | 0.0069 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.8974 | -0.5726 | 0.0080 | 0.0161 | 0.0009 | 0.0038 | 0.0076 | -0.0461 | 0.1965 | 0.2365 | 70.0000 | 19 | 0.0099 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg0p8_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.9448 | -0.6072 | 0.0056 | 0.0112 | 0.0085 | 0.0156 | 0.0312 | -0.0838 | 0.2156 | 0.1498 | 73.0000 | 19 | 0.0071 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg0p8_vxg0p5_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.0111 | -0.6766 | 0.0020 | 0.0040 | 0.0145 | 0.0161 | 0.0323 | -0.0885 | 0.2245 | 0.1798 | 66.0000 | 22 | 0.0069 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg0p8_vxg0p5_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.0336 | -0.6807 | 0.0014 | 0.0027 | 0.0167 | 0.0034 | 0.0068 | -0.0560 | 0.2130 | 0.0943 | 68.0000 | 26 | 0.0065 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.0430 | -0.6891 | -0.0019 | -0.0038 | 0.0328 | 0.0188 | 0.0375 | -0.0776 | 0.2315 | 0.1252 | 71.0000 | 14 | 0.0078 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg0p5_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1221 | -0.7121 | 0.0020 | 0.0040 | 0.0152 | 0.0108 | 0.0216 | -0.0639 | 0.2324 | 0.0750 | 70.0000 | 19 | 0.0062 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg0p8_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1444 | -0.7708 | -0.0097 | -0.0193 | 0.0233 | 0.0104 | 0.0207 | -0.0578 | 0.2347 | 0.1710 | 72.0000 | 22 | 0.0062 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg0p8_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1472 | -0.7593 | -0.0064 | -0.0128 | 0.0243 | 0.0136 | 0.0272 | -0.0651 | 0.2387 | 0.1610 | 69.0000 | 19 | 0.0062 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg0p8_vxg0p5_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1557 | -0.7040 | 0.0075 | 0.0150 | -0.0031 | 0.0086 | 0.0173 | -0.0649 | 0.2342 | 0.0969 | 70.0000 | 19 | 0.0065 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg0p5_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1613 | -0.7165 | 0.0054 | 0.0107 | 0.0120 | 0.0143 | 0.0285 | -0.0716 | 0.2412 | 0.1014 | 72.0000 | 11 | 0.0062 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg0p8_vxg0p5_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1702 | -0.8552 | -0.0073 | -0.0147 | 0.0326 | 0.0106 | 0.0212 | -0.0722 | 0.2382 | 0.0875 | 59.0000 | 25 | 0.0062 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1977 | -0.7666 | 0.0005 | 0.0010 | -0.0005 | -0.0042 | -0.0085 | -0.0451 | 0.2220 | 0.0853 | 72.0000 | 24 | 0.0067 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2167 | -0.7298 | 0.0086 | 0.0171 | 0.0010 | 0.0046 | 0.0091 | -0.0442 | 0.2372 | 0.1214 | 67.0000 | 18 | 0.0061 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg0p8_vxg0p5_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2196 | -0.7351 | 0.0077 | 0.0154 | -0.0036 | 0.0119 | 0.0238 | -0.0699 | 0.2459 | 0.0917 | 71.0000 | 19 | 0.0068 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg0p5_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2479 | -0.7659 | 0.0040 | 0.0080 | 0.0274 | 0.0170 | 0.0341 | -0.0744 | 0.2552 | 0.1727 | 67.0000 | 15 | 0.0108 | `high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
