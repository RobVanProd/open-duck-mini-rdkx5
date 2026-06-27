# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `2`
- mode_count: `1`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `100`

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
- min_done_margin: `50`
- min_contact_transitions: `2`
- min_foot_site_z_p95: `-1.0`

## Seed Failure Counts

### seed_000
- `missing_seed_trace_or_window`: `1`

### seed_002
- `double_support_dominates`: `1`
- `high_body_pitch`: `1`
- `low_forward_velocity`: `1`
- `single_contact_pattern_dominates`: `1`
- `single_support_not_balanced`: `1`
- `too_little_single_support`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| aggregate_phase_table_seam_corrected | 0 | seed_000 | -999.0000 | -500.0202 | NA | NA | 0.0282 | 0.0563 | 0.1110 | 97.0000 | 3 | NA | `double_support_dominates, high_body_pitch, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
