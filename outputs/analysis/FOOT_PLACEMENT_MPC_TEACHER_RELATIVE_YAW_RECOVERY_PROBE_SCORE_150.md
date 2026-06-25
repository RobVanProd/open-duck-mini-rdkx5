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
- `high_lateral_velocity`: `14`
- `low_forward_velocity`: `14`
- `high_sent_target_velocity`: `6`
- `missing_seed_trace_or_window`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2187 | -0.8478 | -0.0011 | -0.0032 | 0.0154 | 0.0156 | 0.0469 | -0.0956 | 0.2491 | 0.3717 | 64.0000 | 29 | 0.0078 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.2741 | -0.9363 | 0.0037 | 0.0110 | 0.0300 | 0.0118 | 0.0354 | -0.0952 | 0.2525 | 0.3506 | 64.0000 | 30 | 0.0111 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.3487 | -1.1323 | 0.0009 | 0.0028 | 0.0247 | 0.0102 | 0.0306 | -0.1086 | 0.2601 | 0.3179 | 65.3333 | 21 | 0.0090 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.3744 | -1.1096 | -0.0010 | -0.0030 | 0.0151 | 0.0095 | 0.0284 | -0.0919 | 0.2624 | 0.4024 | 65.3333 | 30 | 0.0085 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4228 | -1.0117 | -0.0015 | -0.0044 | 0.0243 | 0.0149 | 0.0446 | -0.1158 | 0.2746 | 0.2793 | 72.0000 | 27 | 0.0086 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4347 | -0.9677 | 0.0030 | 0.0090 | 0.0248 | 0.0137 | 0.0412 | -0.1099 | 0.2748 | 0.2604 | 65.3333 | 34 | 0.0085 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4852 | -1.0594 | -0.0016 | -0.0049 | 0.0244 | 0.0124 | 0.0373 | -0.1061 | 0.2796 | 0.2838 | 72.0000 | 29 | 0.0084 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.6659 | -1.2980 | 0.0042 | 0.0127 | 0.0147 | 0.0072 | 0.0217 | -0.0978 | 0.2885 | 0.1188 | 67.3333 | 32 | 0.0085 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.7608 | -1.2843 | 0.0066 | 0.0198 | 0.0106 | 0.0058 | 0.0174 | -0.1140 | 0.3066 | 0.1003 | 62.6667 | 34 | 0.0098 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.8191 | -1.2222 | 0.0030 | 0.0089 | 0.0189 | 0.0111 | 0.0333 | -0.1174 | 0.3199 | 0.1115 | 64.6667 | 27 | 0.0091 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.8591 | -1.4027 | -0.0017 | -0.0051 | 0.0372 | 0.0084 | 0.0251 | -0.1222 | 0.3218 | 0.0583 | 68.6667 | 25 | 0.0090 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.9220 | -1.5309 | 0.0068 | 0.0205 | 0.0130 | 0.0121 | 0.0363 | -0.1387 | 0.3327 | 0.1110 | 57.3333 | 32 | 0.0092 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -2.0685 | -1.3138 | -0.0009 | -0.0028 | 0.0166 | 0.0096 | 0.0287 | -0.1136 | 0.2872 | 0.1126 | 56.6667 | 37 | 0.0101 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -3.0022 | -1.8074 | 0.0053 | 0.0159 | 0.0214 | 0.0146 | 0.0437 | -0.1501 | 0.3342 | 0.0816 | 50.6667 | 37 | 0.0103 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -999.0000 | -499.9347 | -0.0039 | -0.0118 | 0.0368 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -999.0000 | -499.9362 | 0.0025 | 0.0074 | 0.0316 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
