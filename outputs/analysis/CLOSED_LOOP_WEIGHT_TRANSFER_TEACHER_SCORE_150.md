# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `48`
- mode_count: `24`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `150`

## Criteria

- min_mean_vx: `0.04`
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
- `high_lateral_velocity`: `24`
- `low_forward_velocity`: `24`
- `double_support_dominates`: `3`
- `action_saturation`: `2`
- `low_base_height`: `2`
- `single_contact_pattern_dominates`: `1`
- `single_support_not_balanced`: `1`
- `too_little_single_support`: `1`

### seed_002
- `high_lateral_velocity`: `24`
- `low_forward_velocity`: `24`
- `action_saturation`: `2`
- `double_support_dominates`: `2`
- `single_contact_pattern_dominates`: `1`
- `too_little_single_support`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| teacher_p0p64_rs0p02_sk0p08_sa0p02_spg0p5_pd1_lg0_clb0p5 | 0 | seed_000 | -0.5842 | -0.5150 | 0.0028 | 0.0047 | 0.1360 | 92.0000 | 13 | 0.0080 | `double_support_dominates, high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p04_sk0p08_sam0p02_spg0p5_pd1_lg0_clb0p5 | 0 | seed_000 | -0.6126 | -0.5394 | 0.0016 | 0.0037 | 0.1425 | 88.0000 | 19 | 0.0059 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p08_sa0p02_spg1p5_pd0_lg0_clb0p5 | 0 | seed_000 | -0.6797 | -0.6248 | 0.0049 | 0.0074 | 0.1595 | 85.3333 | 29 | 0.0071 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p08_sa0_spg1p5_pd2_lg0_clb0 | 0 | seed_000 | -0.7049 | -0.6143 | 0.0007 | 0.0044 | 0.1279 | 95.3333 | 5 | 0.0044 | `double_support_dominates, high_lateral_velocity, low_forward_velocity, single_contact_pattern_dominates, too_little_single_support` |
| teacher_p0p64_rs0p06_sk0p08_sa0p02_spg1p5_pd2_lg0_clb0p5 | 0 | seed_000 | -0.7280 | -0.6881 | 0.0018 | 0.0049 | 0.1665 | 82.0000 | 33 | 0.0071 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p12_sa0_spg1_pd0_lg0_clb0 | 0 | seed_000 | -0.8813 | -0.8331 | 0.0083 | 0.0119 | 0.1916 | 74.6667 | 30 | 0.0080 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p12_sa0p02_spg1p5_pd0_lg1_clb0 | 0 | seed_000 | -1.0506 | -0.9982 | 0.0046 | 0.0084 | 0.2076 | 84.0000 | 23 | 0.0078 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p08_sa0p02_spg0p5_pd2_lg0p5_clb1 | 0 | seed_000 | -1.2092 | -1.0621 | 0.0030 | 0.0096 | 0.2052 | 77.3333 | 40 | 0.0100 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p08_sa0_spg0p5_pd2_lg0p5_clb0p5 | 0 | seed_000 | -1.2278 | -0.9434 | 0.0022 | 0.0081 | 0.1715 | 78.6667 | 37 | 0.0061 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p08_sa0p02_spg1p5_pd2_lg0p5_clb1 | 0 | seed_000 | -1.2585 | -1.0764 | 0.0028 | 0.0102 | 0.2032 | 78.0000 | 36 | 0.0097 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p16_sa0p02_spg0p5_pd1_lg0_clb0 | 0 | seed_000 | -1.4239 | -1.3804 | 0.0150 | 0.0194 | 0.2690 | 72.6667 | 29 | 0.0119 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p04_sk0p08_sa0p02_spg1p5_pd2_lg0p5_clb1 | 0 | seed_002 | -1.4801 | -1.4463 | 0.0054 | 0.0067 | 0.2726 | 60.6667 | 48 | 0.0086 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p12_sa0_spg1p5_pd2_lg0p5_clb0p5 | 0 | seed_000 | -1.5913 | -1.5667 | 0.0116 | 0.0198 | 0.2951 | 60.6667 | 51 | 0.0094 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p16_sam0p02_spg0p5_pd1_lg0_clb1 | 0 | seed_002 | -1.6850 | -1.6641 | 0.0123 | 0.0143 | 0.2461 | 80.0000 | 25 | 0.0096 | `action_saturation, high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p12_sa0_spg1_pd1_lg0p5_clb0p5 | 0 | seed_000 | -1.8441 | -1.7779 | 0.0097 | 0.0127 | 0.3083 | 63.3333 | 42 | 0.0095 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p06_sk0p16_sam0p02_spg1p5_pd1_lg0_clb0 | 0 | seed_002 | -1.8975 | -1.8909 | 0.0203 | 0.0197 | 0.3393 | 60.0000 | 34 | 0.0086 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p04_sk0p16_sa0_spg1p5_pd1_lg1_clb0 | 0 | seed_000 | -1.9637 | -1.9313 | 0.0112 | 0.0145 | 0.3337 | 66.6667 | 30 | 0.0087 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p06_sk0p12_sa0_spg0p5_pd1_lg0p5_clb0 | 0 | seed_000 | -1.9757 | -1.9584 | 0.0077 | 0.0101 | 0.3340 | 69.3333 | 34 | 0.0085 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p06_sk0p16_sam0p02_spg1_pd1_lg0_clb0 | 0 | seed_002 | -2.0403 | -2.0137 | 0.0221 | 0.0243 | 0.3623 | 52.6667 | 39 | 0.0094 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p06_sk0p12_sa0p02_spg1_pd0_lg1_clb1 | 0 | seed_002 | -2.0930 | -2.0364 | 0.0136 | 0.0146 | 0.3581 | 63.3333 | 37 | 0.0117 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p06_sk0p12_sam0p02_spg1_pd2_lg1_clb0 | 0 | seed_000 | -2.1662 | -2.0599 | 0.0077 | 0.0101 | 0.3356 | 64.0000 | 37 | 0.0084 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p06_sk0p16_sa0p02_spg1p5_pd0_lg0p5_clb0 | 0 | seed_000 | -2.3533 | -2.2871 | 0.0128 | 0.0215 | 0.3819 | 62.0000 | 30 | 0.0152 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p04_sk0p16_sam0p02_spg0p5_pd2_lg0p5_clb1 | 0 | seed_002 | -2.4312 | -2.4150 | 0.0193 | 0.0226 | 0.3695 | 54.6667 | 40 | 0.0108 | `action_saturation, high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p06_sk0p16_sa0_spg0p5_pd0_lg0p5_clb0p5 | 0 | seed_000 | -2.4421 | -2.4278 | 0.0173 | 0.0270 | 0.4121 | 53.3333 | 50 | 0.0126 | `high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
