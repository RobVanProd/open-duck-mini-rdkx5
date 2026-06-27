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
- `high_lateral_velocity`: `60`
- `low_forward_velocity`: `60`
- `high_sent_target_velocity`: `53`
- `missing_seed_trace_or_window`: `4`

### seed_002
- `high_lateral_velocity`: `62`
- `low_forward_velocity`: `61`
- `high_sent_target_velocity`: `56`
- `low_base_height`: `2`
- `missing_seed_trace_or_window`: `2`
- `high_body_pitch`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.0286 | -0.8494 | 0.0129 | 0.0388 | 0.0054 | 0.0114 | 0.0341 | -0.0453 | 0.1766 | 0.4000 | 73.3333 | 27 | 0.0075 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.4382 | -1.4373 | 0.0047 | 0.0141 | 0.0382 | 0.0269 | 0.0806 | -0.0831 | 0.2396 | 0.2186 | 54.6667 | 32 | 0.0106 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.5277 | -1.4392 | 0.0099 | 0.0296 | 0.0402 | 0.0241 | 0.0722 | -0.0904 | 0.2247 | 0.3862 | 64.0000 | 39 | 0.0089 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.6459 | -1.3637 | 0.0089 | 0.0267 | 0.0017 | 0.0255 | 0.0765 | -0.0875 | 0.2419 | 0.3822 | 56.6667 | 29 | 0.0114 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.6763 | -1.3899 | 0.0038 | 0.0115 | 0.0203 | 0.0247 | 0.0741 | -0.0850 | 0.2204 | 0.3744 | 55.3333 | 39 | 0.0106 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.7867 | -1.4229 | 0.0048 | 0.0145 | 0.0293 | 0.0209 | 0.0627 | -0.0793 | 0.2359 | 0.3847 | 64.0000 | 33 | 0.0120 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.8743 | -1.3269 | 0.0236 | 0.0708 | -0.0097 | 0.0136 | 0.0408 | -0.0515 | 0.1927 | 0.4143 | 72.6667 | 22 | 0.0077 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.9345 | -1.8495 | 0.0215 | 0.0645 | -0.0692 | 0.0189 | 0.0566 | -0.0444 | 0.1653 | 0.1477 | 75.3333 | 32 | 0.0092 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.9361 | -1.6621 | 0.0020 | 0.0060 | -0.0007 | 0.0245 | 0.0736 | -0.0957 | 0.2103 | 0.3569 | 57.3333 | 37 | 0.0100 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.9419 | -1.9238 | 0.0175 | 0.0525 | -0.0522 | 0.0151 | 0.0452 | -0.0517 | 0.1777 | 0.1313 | 78.6667 | 27 | 0.0083 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.9871 | -1.9430 | 0.0261 | 0.0782 | -0.0783 | 0.0239 | 0.0717 | -0.0489 | 0.1978 | 0.1273 | 63.3333 | 46 | 0.0078 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.9960 | -1.9932 | 0.0191 | 0.0574 | -0.0595 | 0.0268 | 0.0803 | -0.0475 | 0.2021 | 0.1179 | 62.0000 | 45 | 0.0080 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -2.0551 | -2.0049 | 0.0133 | 0.0398 | -0.0232 | 0.0132 | 0.0395 | -0.0532 | 0.2142 | 0.1767 | 77.3333 | 23 | 0.0082 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -2.0554 | -2.0037 | 0.0122 | 0.0366 | -0.0296 | 0.0296 | 0.0888 | -0.0910 | 0.2032 | 0.1605 | 61.3333 | 35 | 0.0101 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -2.0693 | -2.0002 | 0.0173 | 0.0520 | -0.0665 | 0.0186 | 0.0558 | -0.0301 | 0.1848 | 0.1177 | 70.6667 | 39 | 0.0082 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -2.0726 | -2.0600 | 0.0195 | 0.0586 | -0.0701 | 0.0272 | 0.0817 | -0.0733 | 0.2122 | 0.2614 | 60.0000 | 42 | 0.0091 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -2.0855 | -2.0412 | 0.0259 | 0.0776 | -0.0605 | 0.0244 | 0.0733 | -0.0569 | 0.2107 | 0.1836 | 67.3333 | 39 | 0.0097 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -2.0908 | -2.0350 | 0.0207 | 0.0622 | -0.0372 | 0.0264 | 0.0791 | -0.0640 | 0.2135 | 0.1118 | 61.3333 | 48 | 0.0091 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -2.1176 | -2.0283 | 0.0218 | 0.0654 | -0.0624 | 0.0162 | 0.0485 | -0.0499 | 0.2069 | 0.2262 | 79.3333 | 22 | 0.0089 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -2.1176 | -2.1148 | 0.0181 | 0.0543 | -0.0608 | 0.0196 | 0.0588 | -0.0438 | 0.2085 | 0.1878 | 68.0000 | 42 | 0.0086 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -2.1241 | -2.0096 | 0.0054 | 0.0163 | 0.0154 | 0.0339 | 0.1018 | -0.1157 | 0.2262 | 0.0754 | 47.3333 | 42 | 0.0088 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -2.1305 | -2.0400 | 0.0243 | 0.0729 | -0.0173 | 0.0221 | 0.0663 | -0.0538 | 0.2137 | 0.2266 | 69.3333 | 40 | 0.0079 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -2.1452 | -2.1026 | 0.0205 | 0.0616 | -0.0644 | 0.0285 | 0.0856 | -0.0846 | 0.2228 | 0.2917 | 63.3333 | 40 | 0.0079 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -2.1658 | -2.1080 | 0.0145 | 0.0436 | -0.0631 | 0.0233 | 0.0699 | -0.0760 | 0.2050 | 0.2064 | 62.6667 | 42 | 0.0094 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -2.1772 | -2.1528 | 0.0270 | 0.0809 | -0.0776 | 0.0105 | 0.0314 | -0.0436 | 0.2064 | 0.2169 | 77.3333 | 30 | 0.0085 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
