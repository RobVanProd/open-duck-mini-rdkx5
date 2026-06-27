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
- `high_lateral_velocity`: `64`
- `low_forward_velocity`: `64`

### seed_002
- `high_lateral_velocity`: `64`
- `low_forward_velocity`: `64`
- `high_sent_target_velocity`: `54`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg0p2_pyg0p35_pms0p4_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1234 | -0.9169 | -0.0012 | -0.0037 | 0.0201 | 0.0054 | 0.0161 | -0.0941 | 0.2265 | 0.1793 | 72.6667 | 21 | 0.0076 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1873 | -0.8941 | -0.0026 | -0.0079 | 0.0263 | 0.0102 | 0.0305 | -0.1077 | 0.2399 | 0.2292 | 64.0000 | 41 | 0.0082 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1949 | -0.9106 | 0.0010 | 0.0031 | 0.0156 | 0.0080 | 0.0241 | -0.0917 | 0.2384 | 0.2325 | 64.6667 | 36 | 0.0096 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2245 | -0.9153 | -0.0027 | -0.0082 | 0.0282 | 0.0171 | 0.0513 | -0.1281 | 0.2523 | 0.2210 | 60.0000 | 38 | 0.0069 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2292 | -1.0418 | -0.0049 | -0.0148 | 0.0296 | 0.0186 | 0.0557 | -0.1397 | 0.2545 | 0.2156 | 59.3333 | 34 | 0.0076 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.3220 | -1.0056 | 0.0063 | 0.0189 | 0.0163 | 0.0121 | 0.0363 | -0.1056 | 0.2481 | 0.2127 | 60.0000 | 38 | 0.0078 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.3223 | -0.9963 | -0.0031 | -0.0092 | 0.0230 | 0.0074 | 0.0223 | -0.0914 | 0.2310 | 0.1572 | 72.0000 | 30 | 0.0083 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.3858 | -0.9904 | -0.0025 | -0.0075 | 0.0254 | 0.0151 | 0.0452 | -0.1276 | 0.2644 | 0.2168 | 58.6667 | 35 | 0.0082 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg0p2_pyg0p35_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4331 | -0.9034 | 0.0061 | 0.0182 | 0.0092 | 0.0035 | 0.0105 | -0.0862 | 0.2399 | 0.1471 | 61.3333 | 40 | 0.0091 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4488 | -1.2214 | 0.0020 | 0.0059 | 0.0352 | 0.0166 | 0.0499 | -0.1361 | 0.2666 | 0.0745 | 60.6667 | 42 | 0.0076 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4800 | -1.0911 | -0.0019 | -0.0058 | 0.0258 | 0.0119 | 0.0358 | -0.1271 | 0.2784 | 0.0674 | 63.3333 | 36 | 0.0069 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.5119 | -1.0668 | -0.0047 | -0.0140 | 0.0289 | 0.0139 | 0.0416 | -0.1246 | 0.2846 | 0.2670 | 60.6667 | 34 | 0.0086 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.5148 | -1.1050 | -0.0001 | -0.0002 | 0.0122 | 0.0090 | 0.0270 | -0.0975 | 0.2440 | 0.2129 | 62.6667 | 39 | 0.0071 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.5227 | -1.2412 | -0.0026 | -0.0078 | 0.0392 | 0.0170 | 0.0509 | -0.1431 | 0.2894 | 0.1036 | 64.6667 | 38 | 0.0080 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.5690 | -1.2006 | -0.0007 | -0.0022 | 0.0188 | 0.0162 | 0.0487 | -0.1179 | 0.2383 | 0.2542 | 58.6667 | 40 | 0.0073 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.5813 | -1.0993 | -0.0027 | -0.0081 | 0.0247 | 0.0144 | 0.0432 | -0.1286 | 0.2552 | 0.1186 | 66.6667 | 35 | 0.0082 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg0p2_pyg0p35_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.5884 | -1.0029 | 0.0050 | 0.0150 | 0.0099 | 0.0150 | 0.0451 | -0.0937 | 0.2443 | 0.1434 | 63.3333 | 43 | 0.0095 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.5951 | -1.1961 | -0.0030 | -0.0090 | 0.0254 | 0.0145 | 0.0434 | -0.1237 | 0.2643 | 0.1624 | 60.0000 | 42 | 0.0072 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.6035 | -1.1888 | 0.0026 | 0.0077 | 0.0168 | 0.0130 | 0.0389 | -0.1061 | 0.2473 | 0.1812 | 60.6667 | 38 | 0.0073 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.6317 | -1.1463 | 0.0075 | 0.0226 | 0.0059 | 0.0063 | 0.0190 | -0.0918 | 0.2664 | 0.1711 | 64.6667 | 37 | 0.0089 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.6934 | -1.3810 | -0.0030 | -0.0090 | 0.0383 | 0.0130 | 0.0389 | -0.1318 | 0.3062 | 0.1381 | 60.6667 | 34 | 0.0097 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.6993 | -1.2988 | 0.0038 | 0.0114 | 0.0250 | 0.0136 | 0.0409 | -0.1384 | 0.3078 | 0.0724 | 60.6667 | 38 | 0.0090 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.7280 | -1.3001 | 0.0032 | 0.0095 | 0.0255 | 0.0136 | 0.0407 | -0.1486 | 0.2809 | 0.0799 | 56.6667 | 45 | 0.0075 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.7609 | -1.1944 | -0.0024 | -0.0073 | 0.0252 | 0.0150 | 0.0450 | -0.1197 | 0.2531 | 0.1620 | 66.0000 | 43 | 0.0070 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg0p2_pyg0p35_pms0p6_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.7670 | -1.0639 | 0.0056 | 0.0168 | 0.0069 | 0.0118 | 0.0353 | -0.0850 | 0.2409 | 0.1702 | 78.6667 | 20 | 0.0081 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
