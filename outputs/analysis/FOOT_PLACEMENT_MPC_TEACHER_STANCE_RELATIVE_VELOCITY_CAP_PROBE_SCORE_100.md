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
- `high_sent_target_velocity`: `30`
- `short_done_margin`: `6`
- `high_body_pitch`: `3`

### seed_002
- `low_forward_velocity`: `59`
- `high_lateral_velocity`: `54`
- `high_sent_target_velocity`: `18`
- `single_contact_pattern_dominates`: `2`
- `missing_seed_trace_or_window`: `1`
- `short_done_margin`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.5943 | -0.4753 | 0.0040 | 0.0079 | -0.0002 | 0.0249 | 0.0498 | -0.0311 | 0.1526 | 0.1061 | 86.0000 | 10 | 0.0127 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.6237 | -0.4936 | 0.0144 | 0.0287 | 0.0052 | -0.0029 | -0.0059 | -0.0016 | 0.0548 | 0.0351 | 96.0000 | 7 | 0.0030 | `low_forward_velocity, single_contact_pattern_dominates` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.6711 | -0.4965 | 0.0015 | 0.0031 | 0.0158 | 0.0071 | 0.0141 | -0.0293 | 0.1282 | 0.2415 | 85.0000 | 18 | 0.0090 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.6898 | -0.6303 | 0.0058 | 0.0116 | -0.0052 | 0.0242 | 0.0484 | -0.0434 | 0.1935 | 0.1476 | 57.0000 | 27 | 0.0121 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.7150 | -0.6689 | 0.0110 | 0.0220 | 0.0048 | 0.0383 | 0.0766 | -0.0814 | 0.2124 | 0.3882 | 45.0000 | 30 | 0.0095 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.7492 | -0.7242 | 0.0066 | 0.0133 | -0.0123 | 0.0215 | 0.0431 | -0.0370 | 0.1979 | 0.2721 | 62.0000 | 27 | 0.0088 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.7985 | -0.6963 | 0.0228 | 0.0456 | -0.0245 | 0.0055 | 0.0111 | -0.0189 | 0.1605 | 0.2687 | 72.0000 | 24 | 0.0074 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.9129 | -0.8341 | 0.0184 | 0.0367 | -0.0033 | 0.0286 | 0.0573 | -0.0511 | 0.2066 | 0.3206 | 49.0000 | 22 | 0.0109 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.9151 | -0.8744 | 0.0031 | 0.0061 | -0.0072 | 0.0292 | 0.0584 | -0.0608 | 0.2272 | 0.2448 | 50.0000 | 26 | 0.0101 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.9195 | -0.6994 | 0.0010 | 0.0020 | 0.0015 | 0.0169 | 0.0339 | -0.0299 | 0.1485 | 0.1760 | 72.0000 | 21 | 0.0087 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.9514 | -0.8576 | 0.0145 | 0.0290 | -0.0038 | 0.0162 | 0.0324 | -0.0522 | 0.2171 | 0.4029 | 54.0000 | 30 | 0.0105 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.9553 | -0.8320 | 0.0020 | 0.0039 | 0.0108 | 0.0265 | 0.0531 | -0.0695 | 0.2029 | 0.2895 | 63.0000 | 14 | 0.0078 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.9861 | -0.8312 | 0.0161 | 0.0322 | -0.0108 | 0.0356 | 0.0711 | -0.0590 | 0.2046 | 0.2350 | 54.0000 | 29 | 0.0097 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.9869 | -0.8435 | 0.0121 | 0.0242 | 0.0033 | 0.0269 | 0.0537 | -0.0441 | 0.1978 | 0.2152 | 50.0000 | 32 | 0.0094 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.0007 | -0.6706 | 0.0106 | 0.0212 | 0.0273 | 0.0043 | 0.0085 | -0.0147 | 0.1274 | 0.1252 | 91.0000 | 6 | 0.0070 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.0313 | -0.8276 | 0.0140 | 0.0281 | 0.0061 | 0.0087 | 0.0175 | -0.0265 | 0.1678 | 0.2159 | 82.0000 | 15 | 0.0064 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.0422 | -0.6317 | 0.0218 | 0.0436 | -0.0027 | 0.0110 | 0.0219 | -0.0238 | 0.0736 | 0.1255 | 86.0000 | 10 | 0.0074 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.0514 | -0.9967 | 0.0118 | 0.0237 | 0.0275 | 0.0273 | 0.0546 | -0.0610 | 0.2421 | 0.3639 | 55.0000 | 24 | 0.0104 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.0717 | -1.0355 | 0.0363 | 0.0726 | -0.0117 | 0.0461 | 0.0922 | -0.0946 | 0.2507 | 0.2116 | 53.0000 | 18 | 0.0109 | `high_lateral_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1069 | -0.8414 | 0.0188 | 0.0376 | -0.0033 | 0.0256 | 0.0511 | -0.0562 | 0.2471 | 0.2158 | 42.0000 | 35 | 0.0079 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.1162 | -0.7107 | 0.0181 | 0.0362 | 0.0218 | 0.0017 | 0.0033 | -0.0075 | 0.1128 | 0.0320 | 93.0000 | 3 | 0.0039 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.1245 | -0.9841 | 0.0144 | 0.0287 | -0.0071 | 0.0343 | 0.0687 | -0.0570 | 0.2241 | 0.2374 | 39.0000 | 25 | 0.0091 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1902 | -0.9925 | 0.0089 | 0.0179 | -0.0090 | 0.0336 | 0.0673 | -0.0716 | 0.2041 | 0.2069 | 55.0000 | 24 | 0.0088 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.1972 | -0.9776 | 0.0285 | 0.0570 | -0.0414 | 0.0066 | 0.0132 | -0.0093 | 0.1822 | 0.2028 | 78.0000 | 17 | 0.0076 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.2054 | -0.7574 | 0.0129 | 0.0259 | 0.0069 | 0.0067 | 0.0134 | -0.0147 | 0.1262 | 0.0756 | 86.0000 | 14 | 0.0086 | `high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
