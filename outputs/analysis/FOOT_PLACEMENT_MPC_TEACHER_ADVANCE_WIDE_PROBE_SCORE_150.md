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
- `high_lateral_velocity`: `15`
- `low_forward_velocity`: `15`
- `missing_seed_trace_or_window`: `1`

### seed_002
- `high_lateral_velocity`: `14`
- `low_forward_velocity`: `14`
- `high_sent_target_velocity`: `11`
- `missing_seed_trace_or_window`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.5108 | -0.4711 | 0.0070 | 0.0210 | 0.0018 | 0.0017 | 0.0050 | -0.0405 | 0.1358 | 0.1527 | 84.6667 | 20 | 0.0074 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.5495 | -0.5373 | 0.0022 | 0.0067 | 0.0219 | 0.0108 | 0.0324 | -0.0727 | 0.1608 | 0.1627 | 71.3333 | 42 | 0.0073 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.6815 | -0.5335 | -0.0015 | -0.0045 | 0.0093 | 0.0045 | 0.0134 | -0.0430 | 0.1702 | 0.0945 | 81.3333 | 21 | 0.0067 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.7947 | -0.6149 | 0.0015 | 0.0044 | 0.0161 | 0.0029 | 0.0087 | -0.0591 | 0.1818 | 0.1275 | 75.3333 | 30 | 0.0070 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.9629 | -0.7065 | -0.0014 | -0.0042 | 0.0227 | 0.0036 | 0.0108 | -0.0771 | 0.2036 | 0.1205 | 66.6667 | 44 | 0.0095 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.9804 | -0.6807 | 0.0066 | 0.0197 | -0.0023 | 0.0093 | 0.0280 | -0.0710 | 0.2124 | 0.1290 | 66.0000 | 42 | 0.0053 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.0070 | -0.6932 | -0.0010 | -0.0031 | 0.0129 | 0.0112 | 0.0336 | -0.0912 | 0.2041 | 0.0734 | 66.0000 | 48 | 0.0054 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -1.0347 | -0.8935 | 0.0021 | 0.0063 | -0.0006 | 0.0139 | 0.0416 | -0.1003 | 0.2249 | 0.2115 | 55.3333 | 53 | 0.0062 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -1.0685 | -0.7627 | 0.0048 | 0.0144 | 0.0055 | 0.0104 | 0.0311 | -0.0828 | 0.2252 | 0.1257 | 67.3333 | 36 | 0.0059 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.0938 | -0.7699 | 0.0017 | 0.0050 | 0.0194 | 0.0111 | 0.0333 | -0.0958 | 0.2292 | 0.1049 | 66.6667 | 39 | 0.0055 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -1.3010 | -0.9884 | 0.0031 | 0.0093 | -0.0043 | 0.0123 | 0.0368 | -0.1047 | 0.2535 | 0.2148 | 55.3333 | 58 | 0.0065 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4343 | -0.9186 | -0.0016 | -0.0048 | 0.0176 | 0.0084 | 0.0252 | -0.1061 | 0.2673 | 0.1821 | 56.0000 | 37 | 0.0064 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.4391 | -0.9581 | -0.0003 | -0.0008 | 0.0129 | 0.0086 | 0.0259 | -0.1107 | 0.2447 | 0.1195 | 56.6667 | 50 | 0.0060 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -999.0000 | -499.6874 | 0.0095 | 0.0286 | -0.0080 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -999.0000 | -499.9636 | -0.0002 | -0.0005 | 0.0210 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -999.0000 | -500.0774 | NA | NA | NA | 0.0072 | 0.0215 | -0.0703 | 0.2324 | 0.0966 | 58.6667 | 36 | 0.0069 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
