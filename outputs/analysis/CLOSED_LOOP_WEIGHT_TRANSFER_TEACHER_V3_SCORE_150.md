# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `80`
- mode_count: `40`
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
- `low_forward_velocity`: `40`
- `high_lateral_velocity`: `38`
- `action_saturation`: `6`
- `double_support_dominates`: `4`
- `high_sent_target_velocity`: `4`
- `single_support_not_balanced`: `3`
- `low_base_height`: `2`
- `too_little_single_support`: `2`
- `single_contact_pattern_dominates`: `1`

### seed_002
- `low_forward_velocity`: `40`
- `high_lateral_velocity`: `38`
- `action_saturation`: `6`
- `double_support_dominates`: `5`
- `too_little_single_support`: `4`
- `high_sent_target_velocity`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| teacher_p0p48_rs0p04_sk0p08_sam0p02_shr0p06_srs1_spg1p5_pt0p06_pd2_lgm1_byg0_plg0p06_clb0p5 | 0 | seed_002 | -0.4012 | -0.3959 | 0.0072 | 0.0102 | 0.1416 | 86.0000 | 21 | 0.0062 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs1_spg0p5_pt0p06_pd1_lgm1_byg0_plg0p08_clb0 | 0 | seed_000 | -0.4949 | -0.4607 | 0.0013 | 0.0045 | 0.0933 | 94.6667 | 7 | 0.0054 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| teacher_p0p56_rs0_sk0p08_sam0p02_shrm0p03_srs0p5_spg0p5_pt0_pd1_lgm0p5_bygm1_plg0p08_clb0 | 0 | seed_000 | -0.5309 | -0.4685 | -0.0005 | 0.0008 | 0.1089 | 93.3333 | 4 | 0.0038 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| teacher_p0p64_rs0p04_sk0p12_sa0_shr0p06_srs1_spg0p5_pt0p06_pd2_lgm0p5_byg1_plg0p06_clb0 | 0 | seed_000 | -0.6431 | -0.5066 | 0.0030 | 0.0023 | 0.1238 | 92.0000 | 9 | 0.0056 | `double_support_dominates, high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0_sk0p08_sa0p02_shr0_srs1_spg1_pt0p03_pd2_lg1_byg1_plg0p06_clb0 | 0 | seed_000 | -0.6821 | -0.5539 | 0.0004 | 0.0045 | 0.1266 | 93.3333 | 10 | 0.0047 | `double_support_dominates, high_lateral_velocity, low_forward_velocity, too_little_single_support` |
| teacher_p0p48_rs0_sk0p08_sa0p02_shr0p03_srs0_spg0p5_ptm0p03_pd1_lg0p5_byg0p5_plg0p06_clb0 | 0 | seed_000 | -0.7468 | -0.5463 | 0.0006 | 0.0068 | 0.1208 | 92.6667 | 7 | 0.0048 | `double_support_dominates, high_lateral_velocity, low_forward_velocity, too_little_single_support` |
| teacher_p0p56_rs0p04_sk0p08_sam0p02_shrm0p03_srs0_spg0p5_pt0p03_pd2_lgm1_bygm1_plg0p08_clb1 | 0 | seed_002 | -0.7490 | -0.6640 | 0.0054 | 0.0066 | 0.1810 | 79.3333 | 39 | 0.0085 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0_sk0p12_sa0_shr0p06_srs0_spg1_pt0p06_pd2_lgm1_byg1_plg0p06_clb0p5 | 0 | seed_000 | -0.8003 | -0.7440 | 0.0030 | 0.0064 | 0.1731 | 79.3333 | 28 | 0.0089 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0_sk0p12_sa0_shrm0p03_srs1_spg1p5_pt0p06_pd1_lg0_byg1_plg0p08_clb0p5 | 0 | seed_000 | -0.8800 | -0.8517 | 0.0149 | 0.0172 | 0.2023 | 67.3333 | 31 | 0.0090 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0_sk0p08_sam0p02_shrm0p03_srs1_spg0p5_ptm0p03_pd1_lgm1_byg0p5_plg0p06_clb1 | 0 | seed_000 | -0.9285 | -0.8849 | 0.0041 | 0.0056 | 0.1914 | 79.3333 | 30 | 0.0060 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p12_sam0p02_shrm0p06_srs1_spg1_ptm0p03_pd1_lg0p5_byg1_plg0p06_clb0 | 0 | seed_002 | -0.9966 | -0.9243 | 0.0057 | 0.0057 | 0.2110 | 75.3333 | 46 | 0.0060 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0_sk0p12_sa0p02_shr0_srs0p5_spg1_pt0p06_pd2_lg0p5_bygm1_plg0p08_clb0 | 0 | seed_000 | -1.0214 | -0.8549 | 0.0035 | 0.0120 | 0.1796 | 83.3333 | 21 | 0.0084 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0_sk0p16_sa0p02_shrm0p06_srs0_spg0p5_ptm0p03_pd2_lg1_byg0_plg0p08_clb0 | 0 | seed_000 | -1.1421 | -1.1003 | 0.0146 | 0.0143 | 0.2284 | 73.3333 | 28 | 0.0092 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0_sk0p12_sa0_shrm0p03_srs0p5_spg0p5_pt0p03_pd2_lg0p5_bygm0p5_plg0p06_clb0p5 | 0 | seed_000 | -1.1709 | -1.1079 | 0.0145 | 0.0173 | 0.2301 | 63.3333 | 45 | 0.0092 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p12_sa0_shrm0p03_srs0p5_spg1p5_ptm0p03_pd2_lgm0p5_byg1_plg0p08_clb1 | 0 | seed_000 | -1.2327 | -1.0692 | 0.0145 | 0.0146 | 0.2097 | 68.0000 | 41 | 0.0101 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p12_sa0_shr0p06_srs1_spg1p5_pt0p03_pd1_lgm0p5_byg0p5_plg0p08_clb1 | 0 | seed_000 | -1.2392 | -1.0290 | 0.0258 | 0.0312 | 0.2175 | 60.6667 | 36 | 0.0104 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p16_sam0p02_shrm0p03_srs0p5_spg0p5_pt0p06_pd1_lg0_byg1_plg0p08_clb0p5 | 0 | seed_000 | -1.2731 | -1.1752 | 0.0185 | 0.0138 | 0.2302 | 78.6667 | 33 | 0.0085 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p16_sa0_shr0p06_srs1_spg0p5_pt0_pd2_lgm0p5_byg0_plg0p08_clb0 | 0 | seed_002 | -1.3254 | -1.2159 | 0.0297 | 0.0377 | 0.2881 | 47.3333 | 31 | 0.0113 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p16_sa0_shr0_srs0_spg0p5_ptm0p03_pd2_lgm1_byg1_plg0p12_clb0p5 | 0 | seed_000 | -1.4932 | -1.3201 | 0.0156 | 0.0200 | 0.2459 | 72.6667 | 25 | 0.0110 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p12_sa0_shr0p03_srs1_spg1p5_pt0_pd1_lg1_byg0_plg0p06_clb0 | 0 | seed_000 | -1.5168 | -1.3908 | 0.0052 | 0.0090 | 0.2483 | 68.0000 | 39 | 0.0059 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p04_sk0p08_sa0p02_shr0p06_srs0_spg1_pt0p03_pd1_lg1_bygm1_plg0p12_clb0p5 | 0 | seed_002 | -1.5317 | -1.4809 | 0.0065 | 0.0133 | 0.2864 | 62.6667 | 45 | 0.0090 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p12_sam0p02_shrm0p03_srs0p5_spg0p5_pt0_pd2_lg0p5_bygm1_plg0p08_clb0 | 0 | seed_000 | -1.5708 | -1.3674 | 0.0037 | 0.0070 | 0.2334 | 68.6667 | 41 | 0.0075 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p16_sa0_shr0_srs1_spg1_pt0p03_pd2_lg0_byg1_plg0p12_clb0 | 0 | seed_000 | -1.5777 | -1.5248 | 0.0297 | 0.0324 | 0.3005 | 53.3333 | 31 | 0.0106 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0_sk0p12_sam0p02_shrm0p06_srs0_spg1_pt0_pd1_lgm1_byg0_plg0p06_clb1 | 0 | seed_002 | -1.5850 | -1.5459 | 0.0150 | 0.0185 | 0.2990 | 72.6667 | 35 | 0.0095 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0_sk0p16_sa0p02_shr0_srs0_spg1_pt0p03_pd2_lg0_bygm1_plg0p12_clb1 | 0 | seed_000 | -1.6731 | -1.6691 | 0.0210 | 0.0289 | 0.2808 | 56.6667 | 24 | 0.0122 | `action_saturation, high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
