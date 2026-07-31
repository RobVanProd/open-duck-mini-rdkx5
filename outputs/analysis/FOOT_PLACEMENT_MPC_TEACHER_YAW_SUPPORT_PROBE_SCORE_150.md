# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `144`
- mode_count: `72`
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
- `high_lateral_velocity`: `72`
- `low_forward_velocity`: `72`

### seed_002
- `high_lateral_velocity`: `65`
- `low_forward_velocity`: `65`
- `high_sent_target_velocity`: `46`
- `missing_seed_trace_or_window`: `7`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.3016 | -0.9764 | -0.0024 | -0.0073 | 0.0316 | 0.0070 | 0.0211 | -0.0907 | 0.2502 | 0.3473 | 66.6667 | 27 | 0.0109 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.3487 | -1.1323 | 0.0009 | 0.0028 | 0.0247 | 0.0102 | 0.0306 | -0.1086 | 0.2601 | 0.3179 | 65.3333 | 21 | 0.0090 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4228 | -1.0117 | -0.0015 | -0.0044 | 0.0243 | 0.0149 | 0.0446 | -0.1158 | 0.2746 | 0.2793 | 72.0000 | 27 | 0.0086 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4348 | -1.1825 | 0.0042 | 0.0127 | 0.0147 | 0.0121 | 0.0364 | -0.1058 | 0.2730 | 0.1174 | 69.3333 | 29 | 0.0091 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_ygm0p8_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4484 | -1.0302 | 0.0056 | 0.0169 | 0.0135 | 0.0180 | 0.0540 | -0.1166 | 0.2807 | 0.2416 | 67.3333 | 28 | 0.0091 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_ygm0p8_yvg0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4484 | -1.0302 | 0.0056 | 0.0169 | 0.0135 | 0.0180 | 0.0540 | -0.1166 | 0.2807 | 0.2416 | 67.3333 | 28 | 0.0091 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_ygm0p8_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4484 | -1.0302 | 0.0056 | 0.0169 | 0.0135 | 0.0180 | 0.0540 | -0.1166 | 0.2807 | 0.2416 | 67.3333 | 28 | 0.0091 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4564 | -1.0001 | -0.0020 | -0.0060 | 0.0247 | 0.0156 | 0.0467 | -0.1138 | 0.2766 | 0.2881 | 70.6667 | 28 | 0.0079 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4776 | -1.0837 | -0.0014 | -0.0042 | 0.0201 | 0.0155 | 0.0464 | -0.1230 | 0.2821 | 0.3154 | 66.0000 | 30 | 0.0087 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4852 | -1.0594 | -0.0016 | -0.0049 | 0.0244 | 0.0124 | 0.0373 | -0.1061 | 0.2796 | 0.2838 | 72.0000 | 29 | 0.0084 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.5528 | -1.1803 | 0.0066 | 0.0198 | 0.0106 | 0.0094 | 0.0281 | -0.1112 | 0.2846 | 0.1072 | 69.3333 | 22 | 0.0096 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_ygm0p8_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.5785 | -1.3357 | 0.0033 | 0.0100 | 0.0266 | 0.0202 | 0.0607 | -0.1359 | 0.2985 | 0.1380 | 61.3333 | 29 | 0.0096 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_ygm0p8_yvg0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.5785 | -1.3357 | 0.0033 | 0.0100 | 0.0266 | 0.0202 | 0.0607 | -0.1359 | 0.2985 | 0.1380 | 61.3333 | 29 | 0.0096 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_ygm0p8_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.5785 | -1.3357 | 0.0033 | 0.0100 | 0.0266 | 0.0202 | 0.0607 | -0.1359 | 0.2985 | 0.1380 | 61.3333 | 29 | 0.0096 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0p8_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.5950 | -1.0287 | 0.0010 | 0.0029 | 0.0086 | 0.0106 | 0.0319 | -0.1133 | 0.2773 | 0.1465 | 53.3333 | 39 | 0.0088 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0p8_yvg0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.5950 | -1.0287 | 0.0010 | 0.0029 | 0.0086 | 0.0106 | 0.0319 | -0.1133 | 0.2773 | 0.1465 | 53.3333 | 39 | 0.0088 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0p8_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.5950 | -1.0287 | 0.0010 | 0.0029 | 0.0086 | 0.0106 | 0.0319 | -0.1133 | 0.2773 | 0.1465 | 53.3333 | 39 | 0.0088 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.6153 | -1.2423 | -0.0039 | -0.0118 | 0.0368 | 0.0125 | 0.0374 | -0.1087 | 0.2959 | 0.2618 | 64.0000 | 24 | 0.0096 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0p8_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.7166 | -1.3060 | -0.0019 | -0.0058 | 0.0256 | 0.0065 | 0.0196 | -0.1146 | 0.3019 | 0.1108 | 64.0000 | 32 | 0.0093 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0p8_yvg0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.7166 | -1.3060 | -0.0019 | -0.0058 | 0.0256 | 0.0065 | 0.0196 | -0.1146 | 0.3019 | 0.1108 | 64.0000 | 32 | 0.0093 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0p8_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.7166 | -1.3060 | -0.0019 | -0.0058 | 0.0256 | 0.0065 | 0.0196 | -0.1146 | 0.3019 | 0.1108 | 64.0000 | 32 | 0.0093 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0p8_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.7221 | -1.2985 | -0.0002 | -0.0007 | 0.0245 | 0.0094 | 0.0283 | -0.1212 | 0.3059 | 0.0896 | 69.3333 | 22 | 0.0088 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0p8_yvg0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.7221 | -1.2985 | -0.0002 | -0.0007 | 0.0245 | 0.0094 | 0.0283 | -0.1212 | 0.3059 | 0.0896 | 69.3333 | 22 | 0.0088 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0p8_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.7221 | -1.2985 | -0.0002 | -0.0007 | 0.0245 | 0.0094 | 0.0283 | -0.1212 | 0.3059 | 0.0896 | 69.3333 | 22 | 0.0088 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_ygm0p8_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.7773 | -1.2400 | -0.0015 | -0.0046 | 0.0211 | 0.0152 | 0.0457 | -0.1239 | 0.3192 | 0.0916 | 68.0000 | 28 | 0.0096 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
