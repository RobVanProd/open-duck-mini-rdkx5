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
- `high_lateral_velocity`: `6`
- `single_contact_pattern_dominates`: `3`
- `short_done_margin`: `1`

### seed_002
- `low_forward_velocity`: `16`
- `high_lateral_velocity`: `14`
- `high_sent_target_velocity`: `7`
- `short_done_margin`: `2`
- `high_body_pitch`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.2301 | -0.2138 | 0.0100 | 0.0200 | -0.0105 | 0.0136 | 0.0272 | -0.0335 | 0.1180 | 0.0639 | 88.0000 | 13 | 0.0064 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.2781 | -0.2701 | 0.0107 | 0.0213 | 0.0035 | 0.0064 | 0.0129 | -0.0251 | 0.1021 | 0.0815 | 88.0000 | 12 | 0.0070 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.4144 | -0.3898 | 0.0040 | 0.0079 | 0.0148 | 0.0027 | 0.0054 | -0.0279 | 0.1348 | 0.0841 | 77.0000 | 28 | 0.0070 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.5835 | -0.3896 | 0.0138 | 0.0276 | -0.0015 | -0.0063 | -0.0126 | -0.0116 | 0.1366 | 0.1556 | 79.0000 | 14 | 0.0081 | `high_lateral_velocity, low_forward_velocity, short_done_margin` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.6242 | -0.4698 | 0.0027 | 0.0055 | 0.0098 | 0.0004 | 0.0008 | -0.0252 | 0.1585 | 0.0727 | 83.0000 | 18 | 0.0067 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.7899 | -0.5809 | -0.0040 | -0.0080 | 0.0117 | 0.0086 | 0.0171 | -0.0549 | 0.1873 | 0.0955 | 68.0000 | 35 | 0.0048 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.8445 | -0.5685 | 0.0031 | 0.0061 | 0.0057 | 0.0120 | 0.0239 | -0.0396 | 0.1990 | 0.1620 | 71.0000 | 27 | 0.0047 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.8825 | -0.6125 | 0.0050 | 0.0101 | 0.0206 | 0.0101 | 0.0202 | -0.0546 | 0.2017 | 0.1815 | 68.0000 | 29 | 0.0051 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.8882 | -0.5983 | 0.0013 | 0.0026 | 0.0001 | 0.0165 | 0.0330 | -0.0706 | 0.2089 | 0.0610 | 63.0000 | 34 | 0.0071 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.8974 | -0.6102 | 0.0020 | 0.0040 | -0.0075 | 0.0113 | 0.0226 | -0.0587 | 0.2049 | 0.1696 | 62.0000 | 33 | 0.0053 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.9236 | -0.6197 | 0.0005 | 0.0009 | 0.0016 | 0.0136 | 0.0273 | -0.0498 | 0.2108 | 0.1496 | 68.0000 | 23 | 0.0053 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -1.1998 | -0.9801 | -0.0202 | -0.0405 | 0.0310 | 0.0140 | 0.0280 | -0.0479 | 0.1902 | 0.0636 | 65.0000 | 24 | 0.0061 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2080 | -0.7446 | 0.0056 | 0.0111 | 0.0234 | 0.0051 | 0.0102 | -0.0572 | 0.2368 | 0.1427 | 65.0000 | 28 | 0.0051 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -1.2515 | -0.7430 | 0.0095 | 0.0190 | -0.0114 | 0.0116 | 0.0231 | -0.0685 | 0.2494 | 0.2777 | 52.0000 | 43 | 0.0056 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4575 | -0.9241 | -0.0038 | -0.0077 | 0.0134 | 0.0122 | 0.0244 | -0.0718 | 0.2747 | 0.0868 | 54.0000 | 23 | 0.0073 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -2.6110 | -1.4398 | 0.0057 | 0.0114 | -0.0058 | -0.0695 | -0.1390 | 0.0315 | 0.1998 | 0.1642 | 61.0000 | 34 | 0.0183 | `high_body_pitch, high_lateral_velocity, low_forward_velocity, short_done_margin` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
