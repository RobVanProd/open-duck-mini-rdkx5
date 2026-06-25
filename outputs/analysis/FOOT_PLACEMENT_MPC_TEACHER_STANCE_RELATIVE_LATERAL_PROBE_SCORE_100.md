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
- `high_lateral_velocity`: `64`
- `low_forward_velocity`: `64`
- `high_sent_target_velocity`: `52`
- `short_done_margin`: `4`
- `high_body_pitch`: `1`

### seed_002
- `high_lateral_velocity`: `63`
- `low_forward_velocity`: `62`
- `high_sent_target_velocity`: `51`
- `short_done_margin`: `2`
- `high_body_pitch`: `1`
- `low_base_height`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.6931 | -0.6125 | 0.0074 | 0.0149 | 0.0089 | 0.0023 | 0.0047 | -0.0182 | 0.1491 | 0.1867 | 86.0000 | 9 | 0.0066 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.9071 | -0.8936 | 0.0090 | 0.0180 | 0.0043 | 0.0166 | 0.0333 | -0.0484 | 0.2087 | 0.1140 | 60.0000 | 27 | 0.0101 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.0818 | -0.8482 | 0.0033 | 0.0067 | 0.0131 | 0.0210 | 0.0421 | -0.0407 | 0.1705 | 0.2410 | 72.0000 | 21 | 0.0087 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.0838 | -0.8118 | 0.0196 | 0.0392 | -0.0103 | 0.0377 | 0.0755 | -0.0748 | 0.1899 | 0.2230 | 60.0000 | 20 | 0.0113 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.1700 | -0.8686 | 0.0082 | 0.0164 | -0.0067 | 0.0146 | 0.0293 | -0.0331 | 0.1674 | 0.1638 | 86.0000 | 9 | 0.0069 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2559 | -1.0882 | 0.0126 | 0.0251 | 0.0099 | 0.0097 | 0.0193 | -0.0330 | 0.1990 | 0.3224 | 62.0000 | 28 | 0.0111 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity, short_done_margin` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.3140 | -1.1730 | 0.0158 | 0.0317 | 0.0240 | 0.0308 | 0.0617 | -0.0444 | 0.1887 | 0.1302 | 64.0000 | 19 | 0.0106 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.3221 | -0.9821 | 0.0172 | 0.0343 | 0.0279 | 0.0170 | 0.0339 | -0.0354 | 0.1793 | 0.2790 | 80.0000 | 14 | 0.0082 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.3225 | -1.2703 | 0.0194 | 0.0389 | 0.0129 | 0.0179 | 0.0357 | -0.0546 | 0.2524 | 0.2935 | 50.0000 | 25 | 0.0116 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.3862 | -1.3055 | 0.0137 | 0.0273 | 0.0421 | 0.0233 | 0.0466 | -0.0578 | 0.2384 | 0.2378 | 65.0000 | 26 | 0.0076 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.4576 | -1.0759 | 0.0067 | 0.0133 | 0.0386 | 0.0078 | 0.0156 | -0.0311 | 0.1755 | 0.2069 | 69.0000 | 17 | 0.0083 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.4971 | -1.0222 | 0.0202 | 0.0403 | -0.0034 | 0.0021 | 0.0042 | -0.0173 | 0.1508 | 0.1649 | 84.0000 | 9 | 0.0060 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.5069 | -0.9742 | 0.0116 | 0.0233 | -0.0141 | 0.0366 | 0.0732 | -0.0684 | 0.1763 | 0.2420 | 70.0000 | 22 | 0.0098 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.5503 | -0.9255 | -0.0113 | -0.0226 | 0.0332 | 0.0021 | 0.0043 | -0.0076 | 0.1144 | 0.0889 | 91.0000 | 5 | 0.0038 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.6422 | -1.6234 | 0.0294 | 0.0589 | -0.0357 | 0.0203 | 0.0407 | -0.0326 | 0.1586 | 0.1349 | 75.0000 | 20 | 0.0103 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.6674 | -1.6244 | 0.0097 | 0.0194 | 0.0093 | 0.0375 | 0.0750 | -0.0409 | 0.2402 | 0.3502 | 60.0000 | 19 | 0.0096 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.6971 | -1.0627 | 0.0173 | 0.0346 | -0.0201 | 0.0049 | 0.0098 | -0.0121 | 0.1391 | 0.1115 | 92.0000 | 8 | 0.0069 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.7075 | -1.6910 | 0.0170 | 0.0339 | -0.0090 | 0.0159 | 0.0319 | -0.0234 | 0.1703 | 0.1467 | 74.0000 | 25 | 0.0074 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.7166 | -1.1878 | 0.0202 | 0.0404 | -0.0072 | 0.0137 | 0.0274 | -0.0357 | 0.1778 | 0.1933 | 79.0000 | 11 | 0.0069 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.7238 | -1.2739 | 0.0178 | 0.0357 | 0.0182 | 0.0279 | 0.0559 | -0.0567 | 0.2144 | 0.1972 | 73.0000 | 22 | 0.0088 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.7718 | -1.5668 | 0.0110 | 0.0221 | -0.0165 | 0.0165 | 0.0330 | -0.0257 | 0.1565 | 0.2006 | 78.0000 | 21 | 0.0095 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.7727 | -1.4064 | 0.0101 | 0.0202 | -0.0154 | 0.0143 | 0.0285 | -0.0228 | 0.2203 | 0.2053 | 80.0000 | 16 | 0.0080 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.7738 | -1.7078 | 0.0185 | 0.0370 | -0.0433 | 0.0350 | 0.0701 | -0.0549 | 0.2263 | 0.1822 | 63.0000 | 31 | 0.0097 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.7924 | -1.7832 | 0.0248 | 0.0497 | -0.0543 | 0.0125 | 0.0250 | -0.0084 | 0.1625 | 0.1249 | 75.0000 | 27 | 0.0079 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.8168 | -1.7561 | 0.0233 | 0.0466 | -0.0434 | 0.0098 | 0.0195 | -0.0066 | 0.1700 | 0.1995 | 86.0000 | 10 | 0.0074 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
