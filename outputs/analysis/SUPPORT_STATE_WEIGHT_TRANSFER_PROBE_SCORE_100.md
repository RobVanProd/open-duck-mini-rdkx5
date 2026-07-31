# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `8`
- mode_count: `4`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `100`

## Criteria

- min_mean_vx: `0.04`
- min_forward_displacement_m: `0.04`
- max_vy_abs_p95: `0.12`
- max_contact_dominance_pct: `95.0`
- max_double_support_pct: `90.0`
- max_no_support_pct: `100.0`
- min_single_support_pct: `8.0`
- min_each_single_support_pct: `2.0`
- max_pitch_abs_p95: `0.35`
- min_base_height: `0.145`
- max_sent_velocity_p95: `2.5`
- max_tracking_p95: `0.12`
- min_done_margin: `50`
- min_contact_transitions: `3`
- min_foot_site_z_p95: `-1.0`

## Seed Failure Counts

### seed_000
- `high_lateral_velocity`: `4`
- `low_forward_displacement`: `4`
- `low_forward_velocity`: `4`
- `high_sent_target_velocity`: `2`
- `double_support_dominates`: `1`
- `too_little_single_support`: `1`

### seed_002
- `high_lateral_velocity`: `4`
- `low_forward_displacement`: `4`
- `low_forward_velocity`: `4`
- `double_support_dominates`: `1`
- `high_sent_target_velocity`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_mfs0p25_ffp0p01_pt0_pd1_lgm1_bygm1_plg0p06_clb1 | 0 | seed_002 | -0.7817 | -0.7274 | 0.0137 | 0.0273 | 0.0115 | 0.0230 | 0.1483 | 89.0000 | 20 | 0.0063 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg0p5_mfs0p25_ffp0p01_pt0_pd1_lgm1_bygm1_plg0p06_clb1 | 0 | seed_000 | -0.8606 | -0.8212 | 0.0123 | 0.0246 | 0.0115 | 0.0229 | 0.1455 | 91.0000 | 13 | 0.0061 | `double_support_dominates, high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p04_sk0p08_sa0_shr0p06_srs0p5_spg0p5_mfs0p25_ffp0p01_pt0_pd1_lgm1_bygm1_plg0p06_clb1 | 0 | seed_000 | -1.0861 | -0.9584 | 0.0095 | 0.0190 | 0.0118 | 0.0235 | 0.1560 | 86.0000 | 19 | 0.0068 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p04_sk0p08_sa0_shr0p06_srs0p5_spg1_mfs0p25_ffp0p01_pt0_pd1_lgm1_bygm1_plg0p06_clb1 | 0 | seed_000 | -2.1626 | -1.4283 | 0.0048 | 0.0096 | 0.0150 | 0.0299 | 0.1509 | 84.0000 | 19 | 0.0061 | `high_lateral_velocity, high_sent_target_velocity, low_forward_displacement, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
