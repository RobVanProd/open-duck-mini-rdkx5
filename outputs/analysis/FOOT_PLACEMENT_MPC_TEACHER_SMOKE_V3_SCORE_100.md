# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `16`
- mode_count: `8`
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
- `low_forward_velocity`: `8`
- `single_contact_pattern_dominates`: `2`
- `high_lateral_velocity`: `1`

### seed_002
- `low_forward_velocity`: `8`
- `high_sent_target_velocity`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_ism1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sapm0p02_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3138 | -0.2428 | 0.0007 | 0.0014 | 0.0165 | 0.0329 | 0.1005 | 84.0000 | 20 | 0.0050 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sapm0p02_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.3167 | -0.2548 | 0.0004 | 0.0007 | 0.0164 | 0.0327 | 0.0852 | 78.0000 | 30 | 0.0048 | `high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sap0p02_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.3197 | -0.2581 | 0.0000 | 0.0001 | 0.0137 | 0.0275 | 0.1089 | 88.0000 | 9 | 0.0060 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sapm0p02_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.3258 | -0.2463 | -0.0007 | -0.0015 | 0.0170 | 0.0341 | 0.1027 | 78.0000 | 26 | 0.0059 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sap0p02_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3348 | -0.2277 | 0.0006 | 0.0012 | 0.0222 | 0.0443 | 0.0999 | 77.0000 | 22 | 0.0048 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sap0p02_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.3388 | -0.2645 | -0.0024 | -0.0047 | 0.0144 | 0.0289 | 0.0861 | 85.0000 | 18 | 0.0043 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sapm0p02_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3449 | -0.2527 | -0.0006 | -0.0012 | 0.0177 | 0.0355 | 0.0699 | 87.0000 | 16 | 0.0052 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sap0p02_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3492 | -0.2836 | -0.0031 | -0.0062 | 0.0113 | 0.0227 | 0.0475 | 94.0000 | 10 | 0.0039 | `low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
