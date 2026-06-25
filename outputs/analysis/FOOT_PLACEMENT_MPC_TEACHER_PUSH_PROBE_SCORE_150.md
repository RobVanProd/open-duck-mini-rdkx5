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
- `high_sent_target_velocity`: `6`

### seed_002
- `low_forward_velocity`: `16`
- `high_lateral_velocity`: `14`
- `high_sent_target_velocity`: `4`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.7320 | -0.5134 | -0.0030 | -0.0089 | 0.0187 | 0.0561 | 0.1379 | 78.6667 | 25 | 0.0067 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.7636 | -0.5976 | -0.0030 | -0.0090 | 0.0221 | 0.0662 | 0.1566 | 72.6667 | 26 | 0.0055 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.8057 | -0.6358 | -0.0057 | -0.0170 | 0.0197 | 0.0590 | 0.1604 | 74.0000 | 37 | 0.0068 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.9010 | -0.8856 | -0.0030 | -0.0089 | 0.0263 | 0.0788 | 0.2085 | 66.6667 | 38 | 0.0069 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.9877 | -0.9021 | -0.0013 | -0.0039 | 0.0313 | 0.0940 | 0.2062 | 60.6667 | 37 | 0.0065 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -1.0237 | -0.6086 | -0.0092 | -0.0276 | 0.0141 | 0.0422 | 0.1080 | 83.3333 | 25 | 0.0055 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -1.0257 | -0.7533 | -0.0094 | -0.0283 | 0.0200 | 0.0599 | 0.1626 | 72.0000 | 26 | 0.0076 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.0698 | -0.6595 | -0.0083 | -0.0250 | 0.0079 | 0.0236 | 0.0749 | 88.6667 | 14 | 0.0056 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -1.0711 | -0.7332 | -0.0122 | -0.0365 | 0.0292 | 0.0876 | 0.1623 | 67.3333 | 35 | 0.0060 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.1152 | -0.6780 | -0.0111 | -0.0332 | 0.0103 | 0.0308 | 0.1217 | 74.6667 | 37 | 0.0086 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1885 | -1.0078 | -0.0057 | -0.0171 | 0.0229 | 0.0687 | 0.1738 | 68.6667 | 42 | 0.0062 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -1.2151 | -0.8975 | -0.0145 | -0.0435 | 0.0164 | 0.0491 | 0.1709 | 73.3333 | 32 | 0.0071 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -1.3258 | -0.8819 | -0.0137 | -0.0411 | 0.0234 | 0.0701 | 0.1610 | 74.6667 | 30 | 0.0058 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -1.4142 | -1.0588 | -0.0153 | -0.0458 | 0.0325 | 0.0976 | 0.2045 | 64.6667 | 38 | 0.0063 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.5364 | -0.9497 | -0.0098 | -0.0293 | 0.0168 | 0.0503 | 0.1442 | 75.3333 | 32 | 0.0065 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.6473 | -1.0551 | -0.0111 | -0.0332 | 0.0180 | 0.0540 | 0.1581 | 74.0000 | 30 | 0.0079 | `high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
