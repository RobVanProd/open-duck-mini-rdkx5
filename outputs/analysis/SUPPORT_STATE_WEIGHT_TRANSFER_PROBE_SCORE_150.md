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
- min_forward_displacement_m: `0.06`
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

### seed_002
- `high_lateral_velocity`: `4`
- `low_forward_displacement`: `4`
- `low_forward_velocity`: `4`
- `high_sent_target_velocity`: `3`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg0p5_mfs0p25_ffp0p01_pt0_pd1_lgm1_bygm1_plg0p06_clb1 | 0 | seed_002 | -1.1569 | -1.1257 | 0.0102 | 0.0306 | 0.0103 | 0.0309 | 0.1635 | 84.6667 | 25 | 0.0070 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_mfs0p25_ffp0p01_pt0_pd1_lgm1_bygm1_plg0p06_clb1 | 0 | seed_002 | -1.3858 | -1.2023 | 0.0115 | 0.0344 | 0.0101 | 0.0304 | 0.1582 | 81.3333 | 35 | 0.0066 | `high_lateral_velocity, high_sent_target_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p04_sk0p08_sa0_shr0p06_srs0p5_spg0p5_mfs0p25_ffp0p01_pt0_pd1_lgm1_bygm1_plg0p06_clb1 | 0 | seed_000 | -1.4226 | -1.3153 | 0.0102 | 0.0305 | 0.0132 | 0.0397 | 0.1626 | 80.0000 | 30 | 0.0071 | `high_lateral_velocity, high_sent_target_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p04_sk0p08_sa0_shr0p06_srs0p5_spg1_mfs0p25_ffp0p01_pt0_pd1_lgm1_bygm1_plg0p06_clb1 | 0 | seed_000 | -2.8508 | -2.0255 | 0.0073 | 0.0218 | 0.0134 | 0.0403 | 0.1635 | 78.0000 | 28 | 0.0065 | `high_lateral_velocity, high_sent_target_velocity, low_forward_displacement, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
