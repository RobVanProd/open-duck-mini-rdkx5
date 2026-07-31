# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `72`
- mode_count: `36`
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
- `high_lateral_velocity`: `36`
- `low_forward_velocity`: `36`
- `low_forward_displacement`: `27`
- `high_sent_target_velocity`: `5`
- `action_saturation`: `2`
- `low_base_height`: `2`
- `single_support_not_balanced`: `2`
- `double_support_dominates`: `1`
- `high_body_pitch`: `1`
- `high_tracking_error`: `1`
- `too_little_single_support`: `1`

### seed_002
- `low_forward_velocity`: `36`
- `high_lateral_velocity`: `35`
- `low_forward_displacement`: `21`
- `high_sent_target_velocity`: `5`
- `action_saturation`: `2`
- `low_base_height`: `2`
- `double_support_dominates`: `1`
- `too_little_single_support`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| teacher_p0p56_rs0p06_sk0p12_sam0p02_shr0p06_srs1_spg1p5_mfs0p5_ffp0p005_pt0_pd2_lgm0p5_bygm1_plg0p08_clb1 | 0 | seed_000 | -1.1953 | -1.1925 | 0.0252 | 0.0757 | 0.0216 | 0.0648 | 0.2530 | 61.3333 | 37 | 0.0114 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p16_sa0_shr0p03_srs1_spg1_mfs0p5_ffp0p02_pt0p03_pd2_lgm0p5_bygm1_plg0p08_clb0 | 0 | seed_002 | -1.1976 | -1.1505 | 0.0239 | 0.0717 | 0.0232 | 0.0695 | 0.2558 | 62.6667 | 34 | 0.0102 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p12_sa0p02_shr0p06_srs0p5_spg0p5_mfs0_ffp0p01_pt0p03_pd2_lgm0p5_bygm1_plg0p06_clb1 | 0 | seed_002 | -1.2161 | -1.1804 | 0.0157 | 0.0470 | 0.0157 | 0.0470 | 0.2170 | 72.0000 | 35 | 0.0126 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p12_sa0p02_shr0p03_srs1_spg1_mfs0p5_ffp0p005_ptm0p03_pd1_lg0_byg1_plg0p12_clb1 | 0 | seed_002 | -1.2571 | -1.2545 | 0.0225 | 0.0676 | 0.0243 | 0.0728 | 0.2644 | 58.6667 | 39 | 0.0114 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p12_sam0p02_shr0p06_srs0p5_spg1_mfs0p75_ffp0p01_ptm0p03_pd2_lgm1_bygm0p5_plg0p08_clb1 | 0 | seed_000 | -1.3029 | -1.2501 | 0.0084 | 0.0252 | 0.0131 | 0.0394 | 0.1929 | 77.3333 | 28 | 0.0089 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p06_sk0p16_sa0p02_shr0p03_srs0p5_spg1_mfs0p5_ffp0_pt0_pd1_lgm1_bygm1_plg0p08_clb0 | 0 | seed_002 | -1.4058 | -1.1992 | 0.0299 | 0.0896 | 0.0316 | 0.0949 | 0.2913 | 59.3333 | 32 | 0.0137 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p06_sk0p12_sa0p02_shr0p09_srs1_spg1p5_mfs0p5_ffp0p02_pt0p03_pd2_lgm1_byg0_plg0p12_clb0 | 0 | seed_002 | -1.5289 | -1.4150 | 0.0122 | 0.0367 | 0.0078 | 0.0235 | 0.1886 | 76.0000 | 31 | 0.0104 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p16_sa0_shr0p03_srs1_spg1p5_mfs0p5_ffp0_pt0p03_pd1_lg0_bygm0p5_plg0p12_clb0 | 0 | seed_000 | -1.5395 | -1.3813 | 0.0229 | 0.0686 | 0.0274 | 0.0821 | 0.2637 | 66.6667 | 29 | 0.0115 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p06_sk0p12_sam0p02_shr0p06_srs0p5_spg1_mfs0p75_ffp0p005_pt0p03_pd1_lgm1_bygm0p5_plg0p12_clb0 | 0 | seed_002 | -1.5728 | -1.5700 | 0.0008 | 0.0024 | 0.0015 | 0.0046 | 0.1397 | 80.6667 | 37 | 0.0070 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p04_sk0p12_sam0p02_shr0p09_srs1_spg1p5_mfs0p25_ffp0p01_pt0_pd1_lgm0p5_bygm1_plg0p06_clb0p5 | 0 | seed_002 | -1.6499 | -1.6382 | 0.0161 | 0.0483 | 0.0085 | 0.0256 | 0.2099 | 71.3333 | 40 | 0.0093 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p48_rs0p04_sk0p12_sa0p02_shr0p03_srs0p5_spg0p5_mfs0p25_ffp0p005_pt0_pd2_lg0_bygm0p5_plg0p06_clb0p5 | 0 | seed_000 | -1.7282 | -1.5724 | 0.0181 | 0.0544 | 0.0219 | 0.0656 | 0.2817 | 61.3333 | 37 | 0.0115 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p12_sa0p02_shr0p03_srs1_spg0p5_mfs0p5_ffp0p01_ptm0p03_pd1_lg0_bygm0p5_plg0p06_clb0 | 0 | seed_000 | -1.7664 | -1.5313 | 0.0056 | 0.0168 | 0.0124 | 0.0371 | 0.1988 | 82.0000 | 21 | 0.0096 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p12_sa0_shr0p03_srs1_spg1_mfs0_ffp0p005_pt0_pd1_lgm0p5_bygm1_plg0p06_clb0 | 0 | seed_000 | -1.8286 | -1.6720 | 0.0014 | 0.0043 | 0.0026 | 0.0079 | 0.1337 | 92.6667 | 7 | 0.0062 | `double_support_dominates, high_lateral_velocity, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| teacher_p0p48_rs0p06_sk0p08_sam0p02_shr0p09_srs0p5_spg1_mfs0_ffp0p01_pt0_pd1_lgm1_byg1_plg0p06_clb0p5 | 0 | seed_000 | -1.8700 | -1.4406 | 0.0075 | 0.0224 | 0.0113 | 0.0340 | 0.1540 | 84.0000 | 27 | 0.0066 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p12_sam0p02_shr0p03_srs1_spg0p5_mfs0_ffp0p02_pt0p03_pd2_lg0_bygm1_plg0p06_clb0p5 | 0 | seed_000 | -1.9384 | -1.6718 | 0.0113 | 0.0338 | 0.0196 | 0.0587 | 0.2744 | 67.3333 | 34 | 0.0105 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p06_sk0p08_sam0p02_shr0p09_srs0p5_spg1_mfs0_ffp0p005_ptm0p03_pd1_lgm1_byg1_plg0p08_clb0p5 | 0 | seed_000 | -1.9644 | -1.7343 | 0.0002 | 0.0007 | 0.0002 | 0.0007 | 0.1121 | 82.6667 | 30 | 0.0060 | `low_forward_displacement, low_forward_velocity` |
| teacher_p0p48_rs0p04_sk0p16_sam0p02_shr0p03_srs1_spg1p5_mfs0p75_ffp0p01_pt0p03_pd1_lg0_byg0_plg0p08_clb0p5 | 0 | seed_000 | -1.9688 | -1.9088 | 0.0252 | 0.0756 | 0.0263 | 0.0789 | 0.3215 | 50.6667 | 39 | 0.0101 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p06_sk0p08_sam0p02_shr0p03_srs0p5_spg1_mfs0p75_ffp0p02_pt0_pd2_lgm1_byg1_plg0p06_clb1 | 0 | seed_000 | -1.9740 | -1.6850 | 0.0071 | 0.0214 | 0.0082 | 0.0247 | 0.1756 | 80.6667 | 37 | 0.0079 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p48_rs0p06_sk0p08_sam0p02_shr0p06_srs0p5_spg0p5_mfs0p5_ffp0p005_pt0_pd1_lgm0p5_bygm0p5_plg0p08_clb0p5 | 0 | seed_000 | -2.0191 | -1.6199 | 0.0024 | 0.0073 | 0.0102 | 0.0305 | 0.1702 | 80.0000 | 37 | 0.0064 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p04_sk0p12_sa0_shr0p09_srs1_spg1_mfs0p75_ffp0_pt0p03_pd2_lg0_byg0p5_plg0p06_clb0 | 0 | seed_000 | -2.0771 | -1.8114 | 0.0041 | 0.0123 | 0.0084 | 0.0251 | 0.1953 | 85.3333 | 19 | 0.0075 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p06_sk0p08_sa0p02_shr0p03_srs1_spg1p5_mfs0_ffp0p01_pt0_pd1_lg0_byg0_plg0p06_clb0p5 | 0 | seed_000 | -2.1277 | -1.9108 | 0.0028 | 0.0084 | 0.0092 | 0.0275 | 0.2208 | 78.0000 | 36 | 0.0092 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p04_sk0p16_sa0p02_shr0p03_srs1_spg1_mfs0p75_ffp0_ptm0p03_pd2_lg0_byg1_plg0p08_clb1 | 0 | seed_002 | -2.1296 | -2.1121 | 0.0165 | 0.0496 | 0.0219 | 0.0658 | 0.3173 | 71.3333 | 31 | 0.0123 | `action_saturation, high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p08_sam0p02_shr0p09_srs1_spg1_mfs0_ffp0p02_pt0_pd2_lg1_byg0p5_plg0p12_clb0 | 0 | seed_000 | -2.1914 | -1.9000 | -0.0032 | -0.0096 | 0.0014 | 0.0043 | 0.1433 | 82.0000 | 30 | 0.0062 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p04_sk0p16_sa0_shr0p09_srs1_spg1_mfs0p5_ffp0p02_ptm0p03_pd2_lg0p5_bygm1_plg0p06_clb0 | 0 | seed_000 | -2.2044 | -2.1987 | 0.0165 | 0.0494 | 0.0276 | 0.0828 | 0.3852 | 51.3333 | 40 | 0.0152 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p06_sk0p12_sam0p02_shr0p06_srs1_spg1p5_mfs0p25_ffp0p02_pt0_pd1_lg0p5_bygm0p5_plg0p12_clb1 | 0 | seed_002 | -2.2503 | -2.2318 | 0.0193 | 0.0579 | 0.0325 | 0.0974 | 0.3961 | 55.3333 | 41 | 0.0144 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
