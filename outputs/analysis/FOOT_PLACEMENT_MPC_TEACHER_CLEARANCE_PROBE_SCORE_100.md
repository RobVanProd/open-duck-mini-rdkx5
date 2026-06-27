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
- `single_contact_pattern_dominates`: `8`
- `high_lateral_velocity`: `3`

### seed_002
- `high_lateral_velocity`: `16`
- `low_forward_velocity`: `16`
- `high_sent_target_velocity`: `7`
- `short_done_margin`: `3`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.4404 | -0.3387 | 0.0092 | 0.0184 | -0.0061 | 0.0072 | 0.0144 | -0.0408 | 0.1432 | 0.0615 | 88.0000 | 5 | 0.0069 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1992 | -0.7693 | 0.0104 | 0.0207 | 0.0031 | 0.0151 | 0.0302 | -0.0643 | 0.2469 | 0.0324 | 78.0000 | 15 | 0.0074 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2613 | -0.7815 | 0.0109 | 0.0219 | -0.0071 | 0.0209 | 0.0419 | -0.0903 | 0.2612 | 0.0888 | 60.0000 | 27 | 0.0085 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -1.3242 | -0.7920 | 0.0067 | 0.0134 | 0.0076 | 0.0031 | 0.0062 | -0.0508 | 0.2490 | 0.0853 | 74.0000 | 16 | 0.0071 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -1.5212 | -0.9060 | 0.0055 | 0.0109 | 0.0086 | 0.0204 | 0.0407 | -0.0699 | 0.2685 | 0.0653 | 64.0000 | 19 | 0.0068 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.6364 | -1.0633 | -0.0023 | -0.0045 | 0.0304 | 0.0112 | 0.0225 | -0.0745 | 0.2972 | 0.0705 | 76.0000 | 14 | 0.0068 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.7996 | -1.0443 | 0.0079 | 0.0158 | 0.0031 | 0.0077 | 0.0154 | -0.0833 | 0.3136 | 0.0803 | 67.0000 | 20 | 0.0067 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.8198 | -1.0676 | 0.0094 | 0.0188 | 0.0007 | 0.0059 | 0.0117 | -0.0803 | 0.3141 | 0.0770 | 64.0000 | 22 | 0.0065 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -1.8996 | -1.0379 | 0.0173 | 0.0346 | -0.0213 | 0.0114 | 0.0228 | -0.0869 | 0.3303 | 0.1055 | 64.0000 | 19 | 0.0075 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -1.9329 | -1.1106 | 0.0057 | 0.0115 | 0.0054 | 0.0183 | 0.0366 | -0.0921 | 0.3142 | 0.1101 | 58.0000 | 22 | 0.0066 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.9520 | -1.1105 | 0.0123 | 0.0246 | -0.0082 | 0.0054 | 0.0107 | -0.0841 | 0.3299 | 0.0499 | 52.0000 | 18 | 0.0089 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -2.0224 | -1.1327 | 0.0085 | 0.0171 | 0.0008 | -0.0018 | -0.0036 | -0.0787 | 0.3048 | 0.2616 | 52.0000 | 26 | 0.0125 | `high_lateral_velocity, low_forward_velocity, short_done_margin` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -2.3898 | -1.3004 | 0.0121 | 0.0242 | -0.0020 | 0.0043 | 0.0086 | -0.0997 | 0.3465 | 0.1399 | 42.0000 | 26 | 0.0145 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity, short_done_margin` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -2.5630 | -1.4124 | 0.0087 | 0.0174 | 0.0006 | 0.0200 | 0.0401 | -0.0715 | 0.2854 | 0.0456 | 63.0000 | 22 | 0.0073 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -2.7948 | -1.5619 | 0.0101 | 0.0202 | -0.0066 | 0.0162 | 0.0323 | -0.1078 | 0.3100 | 0.0812 | 46.0000 | 28 | 0.0093 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -2.7998 | -1.5354 | 0.0054 | 0.0109 | 0.0071 | -0.0188 | -0.0376 | -0.0598 | 0.3147 | 0.1290 | 47.0000 | 26 | 0.0142 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity, short_done_margin` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
