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
- `low_forward_velocity`: `64`
- `high_lateral_velocity`: `32`
- `single_contact_pattern_dominates`: `16`

### seed_002
- `low_forward_velocity`: `64`
- `high_lateral_velocity`: `54`
- `high_sent_target_velocity`: `4`
- `single_contact_pattern_dominates`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p5_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.2864 | -0.2864 | 0.0037 | 0.0112 | 0.0005 | 0.0037 | 0.0112 | -0.0165 | 0.1079 | 0.1098 | 92.0000 | 12 | 0.0054 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p5_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.2864 | -0.2864 | 0.0037 | 0.0112 | 0.0005 | 0.0037 | 0.0112 | -0.0165 | 0.1079 | 0.1098 | 92.0000 | 12 | 0.0054 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p5_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.2969 | -0.2868 | 0.0033 | 0.0099 | 0.0031 | 0.0056 | 0.0167 | -0.0269 | 0.1208 | 0.1140 | 84.0000 | 24 | 0.0050 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p5_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.2969 | -0.2868 | 0.0033 | 0.0099 | 0.0031 | 0.0056 | 0.0167 | -0.0269 | 0.1208 | 0.1140 | 84.0000 | 24 | 0.0050 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3082 | -0.3041 | 0.0035 | 0.0106 | -0.0015 | 0.0022 | 0.0067 | -0.0167 | 0.1176 | 0.1044 | 86.0000 | 12 | 0.0050 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3082 | -0.3041 | 0.0035 | 0.0106 | -0.0015 | 0.0022 | 0.0067 | -0.0167 | 0.1176 | 0.1044 | 86.0000 | 12 | 0.0050 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p5_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3254 | -0.3199 | 0.0031 | 0.0093 | 0.0020 | 0.0039 | 0.0118 | -0.0328 | 0.1237 | 0.0883 | 87.3333 | 15 | 0.0049 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p5_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3254 | -0.3199 | 0.0031 | 0.0093 | 0.0020 | 0.0039 | 0.0118 | -0.0328 | 0.1237 | 0.0883 | 87.3333 | 15 | 0.0049 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3263 | -0.2995 | 0.0030 | 0.0090 | 0.0006 | 0.0053 | 0.0158 | -0.0166 | 0.0810 | 0.1191 | 94.6667 | 6 | 0.0050 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3263 | -0.2995 | 0.0030 | 0.0090 | 0.0006 | 0.0053 | 0.0158 | -0.0166 | 0.0810 | 0.1191 | 94.6667 | 6 | 0.0050 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3268 | -0.3188 | -0.0005 | -0.0015 | -0.0010 | 0.0044 | 0.0131 | -0.0281 | 0.1237 | 0.0947 | 88.0000 | 13 | 0.0048 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3268 | -0.3188 | -0.0005 | -0.0015 | -0.0010 | 0.0044 | 0.0131 | -0.0281 | 0.1237 | 0.0947 | 88.0000 | 13 | 0.0048 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3314 | -0.3244 | 0.0039 | 0.0118 | -0.0002 | 0.0037 | 0.0110 | -0.0219 | 0.1238 | 0.0568 | 91.3333 | 6 | 0.0050 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3314 | -0.3244 | 0.0039 | 0.0118 | -0.0002 | 0.0037 | 0.0110 | -0.0219 | 0.1238 | 0.0568 | 91.3333 | 6 | 0.0050 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3400 | -0.3274 | -0.0005 | -0.0016 | -0.0012 | 0.0039 | 0.0117 | -0.0268 | 0.1237 | 0.0974 | 91.3333 | 8 | 0.0047 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3400 | -0.3274 | -0.0005 | -0.0016 | -0.0012 | 0.0039 | 0.0117 | -0.0268 | 0.1237 | 0.0974 | 91.3333 | 8 | 0.0047 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3421 | -0.3169 | 0.0001 | 0.0003 | -0.0042 | 0.0039 | 0.0117 | -0.0150 | 0.0824 | 0.1113 | 95.3333 | 4 | 0.0047 | `low_forward_velocity, single_contact_pattern_dominates` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3421 | -0.3169 | 0.0001 | 0.0003 | -0.0042 | 0.0039 | 0.0117 | -0.0150 | 0.0824 | 0.1113 | 95.3333 | 4 | 0.0047 | `low_forward_velocity, single_contact_pattern_dominates` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.3543 | -0.3381 | 0.0035 | 0.0105 | -0.0020 | 0.0029 | 0.0087 | -0.0223 | 0.1276 | 0.1052 | 80.6667 | 27 | 0.0052 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.3543 | -0.3381 | 0.0035 | 0.0105 | -0.0020 | 0.0029 | 0.0087 | -0.0223 | 0.1276 | 0.1052 | 80.6667 | 27 | 0.0052 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.4601 | -0.4162 | 0.0023 | 0.0070 | 0.0037 | 0.0051 | 0.0154 | -0.0457 | 0.1433 | 0.0535 | 72.6667 | 46 | 0.0054 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.4601 | -0.4162 | 0.0023 | 0.0070 | 0.0037 | 0.0051 | 0.0154 | -0.0457 | 0.1433 | 0.0535 | 72.6667 | 46 | 0.0054 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p25_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.4808 | -0.4016 | -0.0003 | -0.0009 | 0.0213 | 0.0059 | 0.0176 | -0.0376 | 0.1467 | 0.0904 | 74.0000 | 31 | 0.0048 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p25_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.4808 | -0.4016 | -0.0003 | -0.0009 | 0.0213 | 0.0059 | 0.0176 | -0.0376 | 0.1467 | 0.0904 | 74.0000 | 31 | 0.0048 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p15_pms0p5_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.4882 | -0.3898 | 0.0018 | 0.0055 | 0.0026 | 0.0032 | 0.0095 | -0.0168 | 0.0934 | 0.1041 | 91.3333 | 10 | 0.0047 | `low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
