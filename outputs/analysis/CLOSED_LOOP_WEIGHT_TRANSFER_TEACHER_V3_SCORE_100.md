# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `80`
- mode_count: `40`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `100`

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
- `high_lateral_velocity`: `36`
- `action_saturation`: `6`
- `double_support_dominates`: `6`
- `too_little_single_support`: `4`
- `single_support_not_balanced`: `3`
- `high_sent_target_velocity`: `1`

### seed_002
- `low_forward_velocity`: `40`
- `high_lateral_velocity`: `38`
- `action_saturation`: `6`
- `double_support_dominates`: `5`
- `too_little_single_support`: `2`
- `high_sent_target_velocity`: `1`
- `too_few_contact_transitions`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| teacher_p0p48_rs0p04_sk0p08_sam0p02_shr0p06_srs1_spg1p5_pt0p06_pd2_lgm1_byg0_plg0p06_clb0p5 | 0 | seed_000 | -0.3636 | -0.3285 | 0.0104 | 0.0155 | 0.1341 | 88.0000 | 12 | 0.0055 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs1_spg0p5_pt0p06_pd1_lgm1_byg0_plg0p08_clb0 | 0 | seed_000 | -0.4153 | -0.4115 | -0.0019 | 0.0035 | 0.1299 | 92.0000 | 7 | 0.0062 | `double_support_dominates, high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p04_sk0p12_sa0_shr0p06_srs1_spg0p5_pt0p06_pd2_lgm0p5_byg1_plg0p06_clb0 | 0 | seed_000 | -0.4225 | -0.3811 | -0.0027 | 0.0070 | 0.1254 | 92.0000 | 7 | 0.0056 | `double_support_dominates, high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0_sk0p08_sam0p02_shrm0p03_srs0p5_spg0p5_pt0_pd1_lgm0p5_bygm1_plg0p08_clb0 | 0 | seed_002 | -0.4433 | -0.4308 | 0.0002 | 0.0019 | 0.0907 | 94.0000 | 2 | 0.0036 | `double_support_dominates, low_forward_velocity, too_few_contact_transitions, too_little_single_support` |
| teacher_p0p48_rs0_sk0p08_sa0p02_shr0_srs1_spg1_pt0p03_pd2_lg1_byg1_plg0p06_clb0 | 0 | seed_000 | -0.4774 | -0.4507 | -0.0047 | 0.0062 | 0.1072 | 95.0000 | 9 | 0.0043 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| teacher_p0p48_rs0_sk0p08_sa0p02_shr0p03_srs0_spg0p5_ptm0p03_pd1_lg0p5_byg0p5_plg0p06_clb0 | 0 | seed_000 | -0.5134 | -0.4324 | -0.0042 | 0.0102 | 0.1354 | 89.0000 | 7 | 0.0058 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0_sk0p12_sa0p02_shr0_srs0p5_spg1_pt0p06_pd2_lg0p5_bygm1_plg0p08_clb0 | 0 | seed_000 | -0.5948 | -0.5719 | -0.0029 | 0.0036 | 0.1477 | 92.0000 | 14 | 0.0065 | `double_support_dominates, high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0_sk0p12_sa0_shr0p06_srs0_spg1_pt0p06_pd2_lgm1_byg1_plg0p06_clb0p5 | 0 | seed_000 | -0.6107 | -0.6091 | 0.0108 | 0.0113 | 0.1686 | 86.0000 | 17 | 0.0089 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p08_sam0p02_shrm0p03_srs0_spg0p5_pt0p03_pd2_lgm1_bygm1_plg0p08_clb1 | 0 | seed_002 | -0.6347 | -0.5927 | 0.0040 | 0.0097 | 0.1702 | 85.0000 | 23 | 0.0082 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p12_sam0p02_shrm0p06_srs1_spg1_ptm0p03_pd1_lg0p5_byg1_plg0p06_clb0 | 0 | seed_002 | -0.6351 | -0.4940 | 0.0053 | 0.0011 | 0.1607 | 80.0000 | 29 | 0.0055 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p12_sa0_shr0p06_srs1_spg1p5_pt0p03_pd1_lgm0p5_byg0p5_plg0p08_clb1 | 0 | seed_002 | -0.7975 | -0.7854 | 0.0246 | 0.0339 | 0.2178 | 60.0000 | 24 | 0.0103 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0_sk0p12_sa0_shrm0p03_srs1_spg1p5_pt0p06_pd1_lg0_byg1_plg0p08_clb0p5 | 0 | seed_000 | -0.8187 | -0.7932 | 0.0161 | 0.0243 | 0.2033 | 70.0000 | 19 | 0.0090 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p12_sam0p02_shrm0p03_srs0p5_spg0p5_pt0_pd2_lg0p5_bygm1_plg0p08_clb0 | 0 | seed_002 | -0.9304 | -0.6974 | 0.0005 | 0.0019 | 0.1984 | 75.0000 | 25 | 0.0057 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0_sk0p08_sam0p02_shrm0p03_srs1_spg0p5_ptm0p03_pd1_lgm1_byg0p5_plg0p06_clb1 | 0 | seed_000 | -0.9360 | -0.8540 | 0.0032 | 0.0081 | 0.1856 | 84.0000 | 21 | 0.0058 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0_sk0p12_sa0_shrm0p03_srs0p5_spg0p5_pt0p03_pd2_lg0p5_bygm0p5_plg0p06_clb0p5 | 0 | seed_002 | -0.9486 | -0.8541 | 0.0132 | 0.0127 | 0.2128 | 68.0000 | 29 | 0.0078 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p12_sa0_shr0p03_srs1_spg1p5_pt0_pd1_lg1_byg0_plg0p06_clb0 | 0 | seed_002 | -1.0113 | -0.8729 | 0.0032 | 0.0023 | 0.2090 | 75.0000 | 26 | 0.0053 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p12_sa0_shrm0p03_srs0p5_spg1p5_ptm0p03_pd2_lgm0p5_byg1_plg0p08_clb1 | 0 | seed_000 | -1.0427 | -0.8843 | 0.0177 | 0.0177 | 0.1906 | 73.0000 | 27 | 0.0099 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p16_sam0p02_shrm0p03_srs0p5_spg0p5_pt0p06_pd1_lg0_byg1_plg0p08_clb0p5 | 0 | seed_000 | -1.0772 | -0.9405 | 0.0177 | 0.0174 | 0.2000 | 83.0000 | 20 | 0.0083 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p12_sa0p02_shr0p06_srs0p5_spg0p5_ptm0p03_pd1_lgm1_byg0p5_plg0p12_clb1 | 0 | seed_000 | -1.0866 | -1.0272 | 0.0252 | 0.0280 | 0.2054 | 71.0000 | 25 | 0.0150 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p16_sa0_shr0p06_srs1_spg0p5_pt0_pd2_lgm0p5_byg0_plg0p08_clb0 | 0 | seed_002 | -1.1254 | -1.0130 | 0.0273 | 0.0323 | 0.2570 | 52.0000 | 22 | 0.0107 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0_sk0p16_sa0p02_shrm0p06_srs0_spg0p5_ptm0p03_pd2_lg1_byg0_plg0p08_clb0 | 0 | seed_000 | -1.1418 | -1.0200 | 0.0143 | 0.0200 | 0.2147 | 77.0000 | 18 | 0.0085 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p12_sa0_shrm0p06_srs0p5_spg1p5_ptm0p03_pd2_lg1_bygm0p5_plg0p12_clb1 | 0 | seed_002 | -1.2349 | -1.2131 | 0.0032 | 0.0022 | 0.2368 | 68.0000 | 28 | 0.0083 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p12_sam0p02_shrm0p06_srs0p5_spg0p5_pt0p03_pd2_lg0p5_byg0_plg0p06_clb0p5 | 0 | seed_000 | -1.2611 | -1.1340 | 0.0121 | 0.0048 | 0.2113 | 71.0000 | 29 | 0.0065 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0_sk0p12_sam0p02_shrm0p06_srs0_spg1_pt0_pd1_lgm1_byg0_plg0p06_clb1 | 0 | seed_000 | -1.3183 | -1.3147 | 0.0115 | 0.0161 | 0.2620 | 70.0000 | 24 | 0.0103 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p04_sk0p08_sa0p02_shr0p06_srs0_spg1_pt0p03_pd1_lg1_bygm1_plg0p12_clb0p5 | 0 | seed_002 | -1.3843 | -1.1215 | 0.0102 | 0.0173 | 0.2725 | 62.0000 | 29 | 0.0100 | `high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
