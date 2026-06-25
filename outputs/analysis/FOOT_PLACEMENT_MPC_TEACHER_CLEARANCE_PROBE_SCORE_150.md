# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `32`
- mode_count: `16`
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
- `high_lateral_velocity`: `16`
- `low_forward_velocity`: `16`

### seed_002
- `high_lateral_velocity`: `13`
- `low_forward_velocity`: `13`
- `high_sent_target_velocity`: `9`
- `missing_seed_trace_or_window`: `3`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4348 | -1.1825 | 0.0042 | 0.0127 | 0.0147 | 0.0121 | 0.0364 | -0.1058 | 0.2730 | 0.1174 | 69.3333 | 29 | 0.0091 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -1.5012 | -1.0711 | 0.0011 | 0.0032 | 0.0092 | 0.0127 | 0.0380 | -0.1060 | 0.2763 | 0.0833 | 58.0000 | 29 | 0.0102 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.5528 | -1.1803 | 0.0066 | 0.0198 | 0.0106 | 0.0094 | 0.0281 | -0.1112 | 0.2846 | 0.1072 | 69.3333 | 22 | 0.0096 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -1.8502 | -1.3681 | 0.0077 | 0.0232 | 0.0051 | 0.0089 | 0.0268 | -0.1157 | 0.3213 | 0.0833 | 63.3333 | 26 | 0.0093 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.8591 | -1.4027 | -0.0017 | -0.0051 | 0.0372 | 0.0084 | 0.0251 | -0.1222 | 0.3218 | 0.0583 | 68.6667 | 25 | 0.0090 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -1.8769 | -1.2755 | 0.0050 | 0.0151 | -0.0087 | 0.0143 | 0.0428 | -0.1420 | 0.3306 | 0.0888 | 58.0000 | 35 | 0.0095 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.9507 | -1.2549 | -0.0009 | -0.0028 | 0.0166 | 0.0166 | 0.0499 | -0.1302 | 0.2905 | 0.1659 | 56.0000 | 39 | 0.0093 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -2.0389 | -1.3740 | -0.0006 | -0.0018 | 0.0174 | 0.0100 | 0.0299 | -0.1301 | 0.3152 | 0.0674 | 59.3333 | 38 | 0.0080 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -2.0917 | -1.3037 | 0.0005 | 0.0016 | 0.0078 | 0.0189 | 0.0566 | -0.1542 | 0.3218 | 0.0789 | 48.0000 | 34 | 0.0102 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -2.4136 | -1.5349 | -0.0005 | -0.0015 | 0.0202 | 0.0088 | 0.0263 | -0.1270 | 0.3299 | 0.0725 | 60.6667 | 34 | 0.0085 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -2.4628 | -1.5377 | 0.0053 | 0.0159 | 0.0214 | 0.0118 | 0.0353 | -0.1455 | 0.3342 | 0.0816 | 52.0000 | 35 | 0.0103 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -2.6711 | -1.6272 | 0.0000 | 0.0001 | 0.0114 | 0.0091 | 0.0272 | -0.0978 | 0.2866 | 0.1278 | 60.6667 | 33 | 0.0109 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -2.8197 | -1.7182 | 0.0014 | 0.0042 | 0.0086 | 0.0166 | 0.0499 | -0.1447 | 0.3137 | 0.0652 | 49.3333 | 39 | 0.0100 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -999.0000 | -499.8861 | 0.0067 | 0.0202 | 0.0109 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -999.0000 | -499.8913 | 0.0070 | 0.0210 | 0.0150 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -999.0000 | -499.9362 | 0.0025 | 0.0074 | 0.0316 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
