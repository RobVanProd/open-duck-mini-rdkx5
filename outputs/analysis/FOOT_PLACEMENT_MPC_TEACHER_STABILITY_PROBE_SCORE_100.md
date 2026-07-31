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
- `low_forward_velocity`: `64`
- `single_contact_pattern_dominates`: `20`
- `high_lateral_velocity`: `14`

### seed_002
- `low_forward_velocity`: `64`
- `high_lateral_velocity`: `38`
- `high_sent_target_velocity`: `2`
- `single_contact_pattern_dominates`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.2791 | -0.2758 | 0.0045 | 0.0091 | 0.0043 | 0.0053 | 0.0106 | -0.0234 | 0.0962 | 0.0467 | 92.0000 | 7 | 0.0046 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.2791 | -0.2758 | 0.0045 | 0.0091 | 0.0043 | 0.0053 | 0.0106 | -0.0234 | 0.0962 | 0.0467 | 92.0000 | 7 | 0.0046 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.2796 | -0.2634 | 0.0045 | 0.0090 | 0.0041 | 0.0081 | 0.0162 | -0.0227 | 0.1175 | 0.0384 | 92.0000 | 7 | 0.0046 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.2796 | -0.2634 | 0.0045 | 0.0090 | 0.0041 | 0.0081 | 0.0162 | -0.0227 | 0.1175 | 0.0384 | 92.0000 | 7 | 0.0046 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p15_pms0p5_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.2906 | -0.2699 | 0.0079 | 0.0157 | -0.0056 | 0.0063 | 0.0126 | -0.0145 | 0.1234 | 0.0562 | 87.0000 | 12 | 0.0046 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p25_pms0p5_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.2906 | -0.2699 | 0.0079 | 0.0157 | -0.0056 | 0.0063 | 0.0126 | -0.0145 | 0.1234 | 0.0562 | 87.0000 | 12 | 0.0046 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p5_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3014 | -0.2863 | 0.0043 | 0.0086 | 0.0066 | 0.0076 | 0.0153 | -0.0136 | 0.1013 | 0.0287 | 96.0000 | 6 | 0.0046 | `low_forward_velocity, single_contact_pattern_dominates` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p5_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3014 | -0.2863 | 0.0043 | 0.0086 | 0.0066 | 0.0076 | 0.0153 | -0.0136 | 0.1013 | 0.0287 | 96.0000 | 6 | 0.0046 | `low_forward_velocity, single_contact_pattern_dominates` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p15_pms0p25_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.3069 | -0.2908 | 0.0055 | 0.0109 | 0.0234 | 0.0015 | 0.0029 | -0.0211 | 0.1149 | 0.0464 | 84.0000 | 12 | 0.0046 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p25_pms0p25_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.3069 | -0.2908 | 0.0055 | 0.0109 | 0.0234 | 0.0015 | 0.0029 | -0.0211 | 0.1149 | 0.0464 | 84.0000 | 12 | 0.0046 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3092 | -0.3007 | 0.0056 | 0.0113 | -0.0028 | 0.0031 | 0.0062 | -0.0089 | 0.0887 | 0.1085 | 93.0000 | 4 | 0.0061 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3092 | -0.3007 | 0.0056 | 0.0113 | -0.0028 | 0.0031 | 0.0062 | -0.0089 | 0.0887 | 0.1085 | 93.0000 | 4 | 0.0061 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p5_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3115 | -0.2943 | 0.0054 | 0.0108 | 0.0097 | 0.0048 | 0.0095 | -0.0278 | 0.1045 | 0.0440 | 90.0000 | 8 | 0.0047 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p5_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3115 | -0.2943 | 0.0054 | 0.0108 | 0.0097 | 0.0048 | 0.0095 | -0.0278 | 0.1045 | 0.0440 | 90.0000 | 8 | 0.0047 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3211 | -0.3210 | -0.0001 | -0.0003 | -0.0049 | 0.0083 | 0.0166 | -0.0204 | 0.1294 | 0.0385 | 83.0000 | 20 | 0.0049 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3211 | -0.3210 | -0.0001 | -0.0003 | -0.0049 | 0.0083 | 0.0166 | -0.0204 | 0.1294 | 0.0385 | 83.0000 | 20 | 0.0049 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3220 | -0.2988 | -0.0003 | -0.0005 | -0.0041 | 0.0049 | 0.0099 | -0.0115 | 0.1142 | 0.0466 | 87.0000 | 8 | 0.0048 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3220 | -0.2988 | -0.0003 | -0.0005 | -0.0041 | 0.0049 | 0.0099 | -0.0115 | 0.1142 | 0.0466 | 87.0000 | 8 | 0.0048 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3246 | -0.2858 | 0.0062 | 0.0123 | 0.0063 | 0.0081 | 0.0162 | -0.0178 | 0.1182 | 0.0785 | 92.0000 | 5 | 0.0049 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3246 | -0.2858 | 0.0062 | 0.0123 | 0.0063 | 0.0081 | 0.0162 | -0.0178 | 0.1182 | 0.0785 | 92.0000 | 5 | 0.0049 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p5_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3307 | -0.2963 | 0.0033 | 0.0065 | 0.0097 | 0.0064 | 0.0129 | -0.0157 | 0.1087 | 0.1144 | 88.0000 | 12 | 0.0060 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p5_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3307 | -0.2963 | 0.0033 | 0.0065 | 0.0097 | 0.0064 | 0.0129 | -0.0157 | 0.1087 | 0.1144 | 88.0000 | 12 | 0.0060 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p15_pms0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.3340 | -0.3146 | -0.0018 | -0.0035 | 0.0235 | 0.0037 | 0.0074 | -0.0264 | 0.1211 | 0.0401 | 75.0000 | 34 | 0.0046 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p25_pms0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.3340 | -0.3146 | -0.0018 | -0.0035 | 0.0235 | 0.0037 | 0.0074 | -0.0264 | 0.1211 | 0.0401 | 75.0000 | 34 | 0.0046 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p25_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.3372 | -0.3162 | 0.0003 | 0.0006 | 0.0020 | 0.0028 | 0.0055 | -0.0135 | 0.1161 | 0.0353 | 79.0000 | 21 | 0.0046 | `low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
