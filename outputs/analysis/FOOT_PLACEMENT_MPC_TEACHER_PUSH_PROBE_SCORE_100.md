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
- `high_lateral_velocity`: `12`
- `high_sent_target_velocity`: `4`
- `single_contact_pattern_dominates`: `1`

### seed_002
- `low_forward_velocity`: `16`
- `high_lateral_velocity`: `8`
- `high_sent_target_velocity`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.3638 | -0.3583 | -0.0016 | -0.0032 | 0.0232 | 0.0463 | 0.1515 | 78.0000 | 16 | 0.0046 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.4071 | -0.3761 | -0.0031 | -0.0062 | 0.0223 | 0.0446 | 0.1524 | 75.0000 | 24 | 0.0057 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.4355 | -0.3887 | -0.0027 | -0.0055 | 0.0233 | 0.0467 | 0.1607 | 75.0000 | 22 | 0.0053 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.5047 | -0.4196 | -0.0018 | -0.0036 | 0.0216 | 0.0432 | 0.1581 | 67.0000 | 24 | 0.0056 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.6029 | -0.3666 | -0.0025 | -0.0051 | 0.0211 | 0.0422 | 0.1178 | 76.0000 | 21 | 0.0067 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.6331 | -0.3612 | -0.0010 | -0.0020 | 0.0256 | 0.0513 | 0.0969 | 84.0000 | 22 | 0.0057 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.9074 | -0.4897 | -0.0116 | -0.0232 | 0.0275 | 0.0551 | 0.1029 | 82.0000 | 12 | 0.0074 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -1.0164 | -0.6047 | -0.0061 | -0.0123 | 0.0141 | 0.0282 | 0.0915 | 85.0000 | 20 | 0.0047 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -1.0262 | -0.6983 | -0.0071 | -0.0142 | 0.0256 | 0.0512 | 0.1551 | 71.0000 | 23 | 0.0053 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.0514 | -0.6409 | -0.0072 | -0.0144 | 0.0100 | 0.0199 | 0.0692 | 89.0000 | 12 | 0.0050 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.0662 | -0.5812 | -0.0111 | -0.0223 | 0.0249 | 0.0498 | 0.0755 | 89.0000 | 14 | 0.0063 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -1.0751 | -0.6891 | -0.0146 | -0.0293 | 0.0302 | 0.0604 | 0.1519 | 73.0000 | 24 | 0.0061 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.0948 | -0.6255 | -0.0125 | -0.0249 | 0.0182 | 0.0364 | 0.1110 | 74.0000 | 24 | 0.0076 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.1029 | -0.6149 | -0.0079 | -0.0157 | 0.0215 | 0.0429 | 0.0927 | 83.0000 | 17 | 0.0058 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -1.2473 | -0.7974 | -0.0099 | -0.0198 | 0.0254 | 0.0507 | 0.1520 | 80.0000 | 20 | 0.0049 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -1.4225 | -0.9167 | -0.0130 | -0.0261 | 0.0310 | 0.0620 | 0.1662 | 70.0000 | 26 | 0.0057 | `high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
