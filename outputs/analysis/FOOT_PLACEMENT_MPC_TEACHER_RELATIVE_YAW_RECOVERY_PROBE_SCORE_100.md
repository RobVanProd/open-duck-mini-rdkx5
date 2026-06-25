# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `32`
- mode_count: `16`
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
- `low_forward_velocity`: `16`
- `single_contact_pattern_dominates`: `7`
- `high_lateral_velocity`: `2`

### seed_002
- `high_lateral_velocity`: `16`
- `low_forward_velocity`: `16`
- `high_sent_target_velocity`: `6`
- `short_done_margin`: `2`
- `high_body_pitch`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.3257 | -0.3234 | -0.0001 | -0.0003 | 0.0174 | 0.0052 | 0.0104 | -0.0347 | 0.1266 | 0.0959 | 90.0000 | 8 | 0.0070 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.3485 | -0.3466 | 0.0084 | 0.0167 | -0.0031 | 0.0046 | 0.0093 | -0.0329 | 0.1288 | 0.0851 | 91.0000 | 8 | 0.0069 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.0538 | -0.7058 | 0.0069 | 0.0138 | -0.0040 | 0.0213 | 0.0427 | -0.0812 | 0.2357 | 0.2232 | 64.0000 | 18 | 0.0081 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1013 | -0.7193 | 0.0070 | 0.0139 | 0.0014 | 0.0188 | 0.0376 | -0.0639 | 0.2388 | 0.1695 | 67.0000 | 15 | 0.0072 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2164 | -0.7505 | 0.0039 | 0.0079 | 0.0030 | 0.0112 | 0.0224 | -0.0639 | 0.2446 | 0.2260 | 75.0000 | 10 | 0.0083 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4139 | -0.8303 | 0.0081 | 0.0163 | -0.0060 | 0.0045 | 0.0090 | -0.0601 | 0.2618 | 0.2901 | 64.0000 | 20 | 0.0073 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.5290 | -0.9565 | 0.0040 | 0.0080 | -0.0016 | 0.0107 | 0.0214 | -0.0742 | 0.2832 | 0.1127 | 68.0000 | 18 | 0.0068 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.5557 | -0.9476 | 0.0104 | 0.0207 | 0.0031 | 0.0064 | 0.0129 | -0.0646 | 0.2817 | 0.0423 | 66.0000 | 21 | 0.0066 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.6364 | -1.0633 | -0.0023 | -0.0045 | 0.0304 | 0.0112 | 0.0225 | -0.0745 | 0.2972 | 0.0705 | 76.0000 | 14 | 0.0068 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.7334 | -1.0175 | 0.0109 | 0.0219 | -0.0071 | 0.0106 | 0.0213 | -0.0603 | 0.2768 | 0.1246 | 59.0000 | 23 | 0.0101 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.7809 | -1.0090 | 0.0092 | 0.0184 | -0.0061 | -0.0036 | -0.0071 | -0.0646 | 0.2991 | 0.1349 | 67.0000 | 21 | 0.0070 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.8658 | -1.1245 | -0.0079 | -0.0158 | 0.0156 | 0.0107 | 0.0214 | -0.0868 | 0.3253 | 0.0618 | 65.0000 | 13 | 0.0076 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -2.0793 | -1.1900 | 0.0044 | 0.0087 | -0.0092 | 0.0098 | 0.0196 | -0.1036 | 0.3395 | 0.0783 | 50.0000 | 25 | 0.0082 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -2.1661 | -1.2506 | -0.0019 | -0.0038 | 0.0146 | -0.0125 | -0.0250 | -0.0571 | 0.3013 | 0.2945 | 57.0000 | 19 | 0.0117 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity, short_done_margin` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -2.3731 | -1.3211 | 0.0123 | 0.0246 | -0.0082 | 0.0095 | 0.0190 | -0.0886 | 0.3299 | 0.0413 | 50.0000 | 20 | 0.0089 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -4.6259 | -2.4484 | 0.0054 | 0.0109 | 0.0071 | -0.0725 | -0.1451 | -0.0324 | 0.3634 | 0.1652 | 42.0000 | 28 | 0.0223 | `high_body_pitch, high_lateral_velocity, high_sent_target_velocity, low_forward_velocity, short_done_margin` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
