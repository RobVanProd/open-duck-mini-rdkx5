# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `8`
- mode_count: `4`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `150`

## Criteria

- min_mean_vx: `0.04`
- min_forward_displacement_m: `0.004`
- max_vy_abs_p95: `0.12`
- max_contact_dominance_pct: `95.0`
- max_double_support_pct: `75.0`
- max_no_support_pct: `100.0`
- min_single_support_pct: `20.0`
- min_each_single_support_pct: `5.0`
- max_pitch_abs_p95: `0.35`
- min_base_height: `0.145`
- max_sent_velocity_p95: `3.75`
- max_tracking_p95: `0.12`
- min_done_margin: `20`
- min_contact_transitions: `2`
- min_foot_site_z_p95: `-1.0`

## Seed Failure Counts

### seed_000
- `double_support_dominates`: `4`
- `low_forward_displacement`: `4`
- `low_forward_velocity`: `4`
- `single_contact_pattern_dominates`: `4`
- `single_support_not_balanced`: `4`
- `too_little_single_support`: `4`

### seed_002
- `double_support_dominates`: `4`
- `low_forward_velocity`: `4`
- `high_lateral_velocity`: `2`
- `too_little_single_support`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sap0p02_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.1340 | -0.7464 | 0.0003 | 0.0010 | 0.0127 | 0.0382 | 0.1149 | 81.3333 | 25 | 0.0060 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| fpm_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sapm0p02_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.1536 | -0.7367 | -0.0003 | -0.0008 | 0.0097 | 0.0290 | 0.1029 | 79.3333 | 28 | 0.0063 | `double_support_dominates, low_forward_velocity` |
| fpm_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sap0p02_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -1.2706 | -0.7701 | 0.0006 | 0.0019 | 0.0161 | 0.0483 | 0.1243 | 78.0000 | 30 | 0.0056 | `double_support_dominates, high_lateral_velocity, low_forward_velocity` |
| fpm_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sapm0p02_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -1.2955 | -0.8842 | -0.0001 | -0.0003 | 0.0148 | 0.0444 | 0.1299 | 82.6667 | 28 | 0.0057 | `double_support_dominates, high_lateral_velocity, low_forward_velocity, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
