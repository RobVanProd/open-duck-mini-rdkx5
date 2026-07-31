# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `16`
- mode_count: `8`
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
- `low_forward_velocity`: `8`
- `single_contact_pattern_dominates`: `6`

### seed_002
- `low_forward_velocity`: `8`
- `high_lateral_velocity`: `5`
- `high_sent_target_velocity`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_is1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sap0p02_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.3236 | -0.2645 | 0.0003 | 0.0010 | 0.0127 | 0.0382 | 0.1149 | 81.3333 | 25 | 0.0060 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sapm0p02_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.3287 | -0.2809 | -0.0003 | -0.0008 | 0.0097 | 0.0290 | 0.1029 | 79.3333 | 28 | 0.0063 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sapm0p02_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3385 | -0.3374 | -0.0023 | -0.0069 | 0.0148 | 0.0444 | 0.1387 | 80.0000 | 28 | 0.0053 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sap0p02_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.3423 | -0.3006 | -0.0019 | -0.0058 | 0.0138 | 0.0414 | 0.1279 | 79.3333 | 32 | 0.0050 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sapm0p02_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.3432 | -0.2901 | -0.0029 | -0.0087 | 0.0140 | 0.0420 | 0.1212 | 75.3333 | 42 | 0.0054 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sap0p02_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3570 | -0.2865 | -0.0021 | -0.0064 | 0.0116 | 0.0347 | 0.0916 | 87.3333 | 20 | 0.0047 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sap0p02_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3608 | -0.2852 | 0.0006 | 0.0019 | 0.0161 | 0.0483 | 0.1243 | 78.0000 | 30 | 0.0056 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sapm0p02_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3675 | -0.3169 | -0.0001 | -0.0003 | 0.0148 | 0.0444 | 0.1299 | 82.6667 | 28 | 0.0057 | `high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
