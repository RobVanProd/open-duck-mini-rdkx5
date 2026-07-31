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
- `single_contact_pattern_dominates`: `1`

### seed_002
- `low_forward_velocity`: `15`
- `high_lateral_velocity`: `14`
- `high_sent_target_velocity`: `4`
- `missing_seed_trace_or_window`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.4295 | -0.3422 | 0.0050 | 0.0149 | 0.0031 | 0.0072 | 0.0217 | -0.0329 | 0.1121 | 0.1636 | 81.3333 | 28 | 0.0073 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.5295 | -0.4819 | -0.0009 | -0.0026 | 0.0043 | 0.0110 | 0.0330 | -0.0500 | 0.1467 | 0.1410 | 82.0000 | 21 | 0.0075 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.7962 | -0.6944 | -0.0032 | -0.0096 | 0.0256 | 0.0120 | 0.0361 | -0.0912 | 0.1922 | 0.1714 | 68.0000 | 41 | 0.0073 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.8200 | -0.7400 | -0.0013 | -0.0039 | 0.0222 | 0.0109 | 0.0328 | -0.0704 | 0.1748 | 0.1281 | 71.3333 | 32 | 0.0073 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.8201 | -0.6704 | 0.0017 | 0.0050 | 0.0037 | 0.0157 | 0.0471 | -0.0659 | 0.2002 | 0.1684 | 72.6667 | 35 | 0.0057 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.8328 | -0.7309 | -0.0002 | -0.0007 | 0.0300 | 0.0097 | 0.0292 | -0.0728 | 0.1696 | 0.1717 | 68.0000 | 44 | 0.0071 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.8614 | -0.8156 | 0.0001 | 0.0004 | 0.0153 | 0.0174 | 0.0521 | -0.0968 | 0.2072 | 0.0989 | 68.6667 | 33 | 0.0057 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.8639 | -0.7120 | -0.0008 | -0.0025 | 0.0103 | 0.0089 | 0.0268 | -0.0639 | 0.1980 | 0.1121 | 70.6667 | 37 | 0.0066 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.9109 | -0.6744 | 0.0001 | 0.0004 | 0.0022 | 0.0119 | 0.0356 | -0.0882 | 0.2072 | 0.0967 | 68.6667 | 40 | 0.0071 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.9463 | -0.7119 | 0.0035 | 0.0106 | 0.0068 | 0.0115 | 0.0346 | -0.0750 | 0.2113 | 0.1168 | 68.0000 | 37 | 0.0054 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.0165 | -0.8431 | -0.0026 | -0.0078 | 0.0285 | 0.0162 | 0.0485 | -0.0801 | 0.2252 | 0.1122 | 64.0000 | 46 | 0.0058 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.0438 | -0.8479 | -0.0016 | -0.0049 | 0.0250 | 0.0101 | 0.0302 | -0.0837 | 0.2060 | 0.0882 | 70.6667 | 42 | 0.0056 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.0695 | -0.9947 | -0.0058 | -0.0175 | 0.0351 | 0.0153 | 0.0458 | -0.0916 | 0.2122 | 0.0720 | 69.3333 | 40 | 0.0057 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1559 | -1.0313 | -0.0043 | -0.0130 | 0.0278 | 0.0173 | 0.0520 | -0.1170 | 0.2264 | 0.1152 | 53.3333 | 55 | 0.0057 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -1.2117 | -1.0330 | 0.0002 | 0.0006 | 0.0143 | 0.0160 | 0.0481 | -0.1121 | 0.2495 | 0.1196 | 62.6667 | 45 | 0.0066 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -999.0000 | -499.8702 | -0.0027 | -0.0081 | 0.0207 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
