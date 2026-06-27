# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `128`
- mode_count: `64`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `150`

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
- `high_lateral_velocity`: `59`

### seed_002
- `high_lateral_velocity`: `64`
- `low_forward_velocity`: `64`
- `high_sent_target_velocity`: `42`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg0p5_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.0054 | -0.7863 | 0.0039 | 0.0117 | 0.0214 | 0.0066 | 0.0199 | -0.0691 | 0.2131 | 0.3855 | 72.0000 | 35 | 0.0109 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg0p8_vxg0p5_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.0758 | -0.8437 | -0.0032 | -0.0096 | 0.0276 | 0.0149 | 0.0448 | -0.1189 | 0.2313 | 0.4035 | 69.3333 | 29 | 0.0086 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg0p5_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1604 | -0.8872 | -0.0031 | -0.0092 | 0.0273 | 0.0091 | 0.0272 | -0.1014 | 0.2352 | 0.2366 | 71.3333 | 27 | 0.0082 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1780 | -1.0288 | -0.0016 | -0.0049 | 0.0280 | 0.0116 | 0.0347 | -0.0923 | 0.2403 | 0.3806 | 62.6667 | 34 | 0.0076 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg0p8_vxg0p5_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1859 | -0.9639 | 0.0021 | 0.0063 | 0.0218 | 0.0122 | 0.0367 | -0.1043 | 0.2420 | 0.2563 | 64.6667 | 34 | 0.0087 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg0p8_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1886 | -0.9982 | 0.0022 | 0.0066 | 0.0309 | 0.0170 | 0.0511 | -0.1115 | 0.2477 | 0.3885 | 65.3333 | 31 | 0.0076 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1908 | -0.9806 | -0.0041 | -0.0122 | 0.0218 | 0.0113 | 0.0340 | -0.1050 | 0.2416 | 0.3761 | 63.3333 | 35 | 0.0103 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1985 | -1.0434 | -0.0040 | -0.0120 | 0.0315 | 0.0152 | 0.0457 | -0.1164 | 0.2469 | 0.3293 | 67.3333 | 30 | 0.0083 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg0p5_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2131 | -0.8681 | -0.0025 | -0.0075 | 0.0212 | 0.0174 | 0.0522 | -0.1150 | 0.2512 | 0.2943 | 66.0000 | 23 | 0.0077 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg0p8_vxg0p5_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2155 | -1.0498 | 0.0049 | 0.0148 | 0.0202 | 0.0148 | 0.0444 | -0.1149 | 0.2486 | 0.2917 | 64.6667 | 33 | 0.0085 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg0p8_vxg0p5_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2209 | -1.1874 | -0.0027 | -0.0081 | 0.0372 | 0.0129 | 0.0388 | -0.1091 | 0.2463 | 0.2744 | 58.6667 | 37 | 0.0077 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2412 | -0.9181 | -0.0023 | -0.0070 | 0.0252 | 0.0113 | 0.0340 | -0.1135 | 0.2479 | 0.2776 | 66.6667 | 25 | 0.0097 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg0p8_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2528 | -1.0727 | -0.0036 | -0.0108 | 0.0293 | 0.0211 | 0.0634 | -0.1262 | 0.2604 | 0.3494 | 73.3333 | 20 | 0.0094 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg0p8_vxg0p5_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2536 | -0.9331 | -0.0029 | -0.0087 | 0.0274 | 0.0123 | 0.0370 | -0.1186 | 0.2506 | 0.2494 | 66.6667 | 28 | 0.0078 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg0p8_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2848 | -0.9183 | 0.0013 | 0.0038 | 0.0305 | 0.0127 | 0.0382 | -0.0943 | 0.2549 | 0.3507 | 66.6667 | 36 | 0.0085 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2912 | -1.0797 | 0.0053 | 0.0159 | 0.0145 | 0.0155 | 0.0466 | -0.1103 | 0.2589 | 0.2819 | 64.6667 | 32 | 0.0078 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg0p5_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2948 | -1.0908 | -0.0037 | -0.0110 | 0.0331 | 0.0099 | 0.0297 | -0.1098 | 0.2530 | 0.2285 | 65.3333 | 30 | 0.0083 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg0p8_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.3012 | -0.9424 | -0.0006 | -0.0017 | 0.0228 | 0.0098 | 0.0295 | -0.1029 | 0.2537 | 0.2332 | 67.3333 | 32 | 0.0084 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg0p8_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.3043 | -0.9491 | -0.0022 | -0.0066 | 0.0256 | 0.0042 | 0.0127 | -0.0817 | 0.2478 | 0.2525 | 76.0000 | 22 | 0.0098 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg0p8_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.3063 | -1.0977 | -0.0041 | -0.0123 | 0.0309 | 0.0084 | 0.0251 | -0.1074 | 0.2527 | 0.2229 | 70.0000 | 27 | 0.0094 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg0p8_vxg0p5_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.3672 | -0.9812 | -0.0024 | -0.0071 | 0.0264 | 0.0056 | 0.0168 | -0.0877 | 0.2572 | 0.2214 | 72.0000 | 22 | 0.0096 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4185 | -1.0023 | -0.0009 | -0.0026 | 0.0228 | 0.0096 | 0.0287 | -0.1082 | 0.2681 | 0.2492 | 66.0000 | 33 | 0.0084 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg0p8_vxg0p5_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4249 | -1.1330 | 0.0057 | 0.0170 | 0.0127 | 0.0073 | 0.0220 | -0.0846 | 0.2664 | 0.3482 | 66.0000 | 36 | 0.0103 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg0p5_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4678 | -1.0466 | -0.0049 | -0.0148 | 0.0296 | 0.0139 | 0.0418 | -0.1193 | 0.2791 | 0.3408 | 62.0000 | 27 | 0.0113 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.5658 | -1.2555 | 0.0061 | 0.0184 | 0.0189 | 0.0107 | 0.0322 | -0.1080 | 0.2878 | 0.2716 | 56.6667 | 39 | 0.0115 | `high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
