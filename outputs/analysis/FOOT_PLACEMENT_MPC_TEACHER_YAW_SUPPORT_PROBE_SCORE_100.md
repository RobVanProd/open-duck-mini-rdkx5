# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `144`
- mode_count: `72`
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
- `low_forward_velocity`: `72`
- `single_contact_pattern_dominates`: `27`
- `high_lateral_velocity`: `8`

### seed_002
- `high_lateral_velocity`: `72`
- `low_forward_velocity`: `72`
- `high_sent_target_velocity`: `28`
- `short_done_margin`: `7`
- `high_body_pitch`: `3`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.3257 | -0.3234 | -0.0001 | -0.0003 | 0.0174 | 0.0052 | 0.0104 | -0.0347 | 0.1266 | 0.0959 | 90.0000 | 8 | 0.0070 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.3485 | -0.3466 | 0.0084 | 0.0167 | -0.0031 | 0.0046 | 0.0093 | -0.0329 | 0.1288 | 0.0851 | 91.0000 | 8 | 0.0069 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.4404 | -0.3387 | 0.0092 | 0.0184 | -0.0061 | 0.0072 | 0.0144 | -0.0408 | 0.1432 | 0.0615 | 88.0000 | 5 | 0.0069 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.9256 | -0.6160 | 0.0060 | 0.0119 | 0.0077 | 0.0026 | 0.0051 | -0.0468 | 0.1986 | 0.2179 | 76.0000 | 12 | 0.0106 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_ygm0p8_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.0596 | -0.6688 | 0.0047 | 0.0094 | 0.0058 | 0.0224 | 0.0447 | -0.0756 | 0.2376 | 0.1343 | 77.0000 | 12 | 0.0086 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_ygm0p8_yvg0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.0596 | -0.6688 | 0.0047 | 0.0094 | 0.0058 | 0.0224 | 0.0447 | -0.0756 | 0.2376 | 0.1343 | 77.0000 | 12 | 0.0086 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_ygm0p8_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.0596 | -0.6688 | 0.0047 | 0.0094 | 0.0058 | 0.0224 | 0.0447 | -0.0756 | 0.2376 | 0.1343 | 77.0000 | 12 | 0.0086 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1600 | -0.7476 | -0.0019 | -0.0038 | 0.0146 | 0.0003 | 0.0006 | -0.0363 | 0.2253 | 0.1190 | 73.0000 | 13 | 0.0085 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1708 | -0.7541 | 0.0070 | 0.0139 | 0.0014 | 0.0114 | 0.0228 | -0.0601 | 0.2392 | 0.1955 | 63.0000 | 21 | 0.0067 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0p8_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1790 | -0.7025 | 0.0104 | 0.0209 | 0.0098 | 0.0058 | 0.0116 | -0.0524 | 0.2339 | 0.0392 | 74.0000 | 20 | 0.0066 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0p8_yvg0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1790 | -0.7025 | 0.0104 | 0.0209 | 0.0098 | 0.0058 | 0.0116 | -0.0524 | 0.2339 | 0.0392 | 74.0000 | 20 | 0.0066 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0p8_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1790 | -0.7025 | 0.0104 | 0.0209 | 0.0098 | 0.0058 | 0.0116 | -0.0524 | 0.2339 | 0.0392 | 74.0000 | 20 | 0.0066 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1992 | -0.7693 | 0.0104 | 0.0207 | 0.0031 | 0.0151 | 0.0302 | -0.0643 | 0.2469 | 0.0324 | 78.0000 | 15 | 0.0074 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2164 | -0.7505 | 0.0039 | 0.0079 | 0.0030 | 0.0112 | 0.0224 | -0.0639 | 0.2446 | 0.2260 | 75.0000 | 10 | 0.0083 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0p8_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2258 | -0.7284 | 0.0143 | 0.0287 | -0.0058 | 0.0219 | 0.0438 | -0.0900 | 0.2325 | 0.1010 | 64.0000 | 28 | 0.0080 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0p8_yvg0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2258 | -0.7284 | 0.0143 | 0.0287 | -0.0058 | 0.0219 | 0.0438 | -0.0900 | 0.2325 | 0.1010 | 64.0000 | 28 | 0.0080 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0p8_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2258 | -0.7284 | 0.0143 | 0.0287 | -0.0058 | 0.0219 | 0.0438 | -0.0900 | 0.2325 | 0.1010 | 64.0000 | 28 | 0.0080 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2269 | -0.7464 | 0.0060 | 0.0120 | 0.0072 | 0.0156 | 0.0312 | -0.0717 | 0.2509 | 0.1785 | 76.0000 | 16 | 0.0068 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0p8_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2518 | -0.7977 | -0.0029 | -0.0059 | 0.0211 | 0.0106 | 0.0212 | -0.0617 | 0.2484 | 0.1064 | 80.0000 | 12 | 0.0067 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0p8_yvg0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2518 | -0.7977 | -0.0029 | -0.0059 | 0.0211 | 0.0106 | 0.0212 | -0.0617 | 0.2484 | 0.1064 | 80.0000 | 12 | 0.0067 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0p8_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2518 | -0.7977 | -0.0029 | -0.0059 | 0.0211 | 0.0106 | 0.0212 | -0.0617 | 0.2484 | 0.1064 | 80.0000 | 12 | 0.0067 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2613 | -0.7815 | 0.0109 | 0.0219 | -0.0071 | 0.0209 | 0.0419 | -0.0903 | 0.2612 | 0.0888 | 60.0000 | 27 | 0.0085 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2839 | -0.8072 | 0.0099 | 0.0199 | -0.0054 | 0.0108 | 0.0215 | -0.0659 | 0.2526 | 0.1722 | 74.0000 | 15 | 0.0067 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0p8_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2998 | -0.7775 | 0.0116 | 0.0233 | 0.0012 | 0.0152 | 0.0305 | -0.0783 | 0.2596 | 0.1205 | 57.0000 | 23 | 0.0084 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0p8_yvg0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2998 | -0.7775 | 0.0116 | 0.0233 | 0.0012 | 0.0152 | 0.0305 | -0.0783 | 0.2596 | 0.1205 | 57.0000 | 23 | 0.0084 | `high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
