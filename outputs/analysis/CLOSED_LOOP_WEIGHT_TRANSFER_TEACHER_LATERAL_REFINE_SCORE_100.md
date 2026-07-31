# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `96`
- mode_count: `48`
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
- `low_forward_velocity`: `47`
- `high_lateral_velocity`: `45`
- `low_forward_displacement`: `29`
- `high_sent_target_velocity`: `9`
- `double_support_dominates`: `5`
- `single_support_not_balanced`: `3`
- `low_base_height`: `2`
- `too_little_single_support`: `2`
- `missing_seed_trace_or_window`: `1`

### seed_002
- `low_forward_velocity`: `46`
- `high_lateral_velocity`: `39`
- `low_forward_displacement`: `28`
- `high_sent_target_velocity`: `8`
- `double_support_dominates`: `7`
- `low_base_height`: `3`
- `too_little_single_support`: `3`
- `high_body_pitch`: `1`
- `missing_seed_trace_or_window`: `1`
- `single_support_not_balanced`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| teacher_p0p56_rs0_sk0p08_sam0p02_shr0p09_srs0p5_spg1_mfs0p25_ffp0p005_pt0p03_pd2_lgm1_byg0_plg0p04_clb0p5 | 0 | seed_000 | -0.5756 | -0.4131 | 0.0131 | 0.0261 | 0.0186 | 0.0371 | 0.1093 | 92.0000 | 12 | 0.0085 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p08_sa0p02_shr0p09_srs0p5_spg1_mfs0p25_ffp0p01_pt0_pd2_lgm1_bygm0p5_plg0p04_clb1 | 0 | seed_000 | -0.6425 | -0.6145 | 0.0133 | 0.0267 | 0.0156 | 0.0312 | 0.1487 | 90.0000 | 12 | 0.0071 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p03_sk0p12_sam0p02_shr0p09_srs0p5_spg0p5_mfs0_ffp0p005_pt0_pd2_lgm1_byg0p5_plg0p1_clb1 | 0 | seed_000 | -0.7083 | -0.6476 | 0.0195 | 0.0391 | 0.0188 | 0.0376 | 0.1686 | 83.0000 | 17 | 0.0088 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p03_sk0p12_sam0p02_shr0p06_srs0p5_spg0p5_mfs0p25_ffp0p01_pt0p03_pd1_lgm2_byg0_plg0p04_clb1 | 0 | seed_000 | -0.7529 | -0.6736 | 0.0160 | 0.0320 | 0.0181 | 0.0361 | 0.1649 | 82.0000 | 14 | 0.0085 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p12_sam0p02_shr0p09_srs0p5_spg1_mfs0p25_ffp0p02_pt0p03_pd1_lgm0p5_bygm1_plg0p1_clb1 | 0 | seed_002 | -0.7608 | -0.7491 | 0.0138 | 0.0277 | 0.0145 | 0.0289 | 0.1637 | 87.0000 | 11 | 0.0073 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0_sk0p08_sa0_shr0p09_srs0p5_spg1_mfs0p25_ffp0p01_pt0_pd1_lg0_bygm1_plg0p08_clb1 | 0 | seed_002 | -0.7626 | -0.7624 | 0.0117 | 0.0235 | 0.0142 | 0.0284 | 0.1598 | 91.0000 | 11 | 0.0070 | `double_support_dominates, high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0_sk0p12_sa0p02_shr0p09_srs0p5_spg0p5_mfs0_ffp0p02_pt0p03_pd2_lgm0p5_byg0_plg0p1_clb0p5 | 0 | seed_002 | -0.7649 | -0.7472 | 0.0232 | 0.0465 | 0.0221 | 0.0441 | 0.2004 | 80.0000 | 19 | 0.0146 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p01_sk0p08_sa0p02_shr0p06_srs0p5_spg1_mfs0p25_ffp0p005_pt0p03_pd1_lgm1_bygm1_plg0p08_clb1 | 0 | seed_000 | -0.7826 | -0.7283 | 0.0140 | 0.0279 | 0.0180 | 0.0360 | 0.1746 | 78.0000 | 17 | 0.0110 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p04_sk0p12_sa0_shr0p06_srs0p5_spg1_mfs0_ffp0p005_pt0_pd2_lgm1p5_byg0p5_plg0p04_clb1 | 0 | seed_000 | -0.8056 | -0.7673 | 0.0201 | 0.0402 | 0.0176 | 0.0351 | 0.1787 | 84.0000 | 16 | 0.0113 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0_sk0p12_sam0p02_shr0p09_srs1_spg1_mfs0p25_ffp0p005_pt0p03_pd1_lgm0p5_bygm1p5_plg0p1_clb1 | 0 | seed_002 | -0.8100 | -0.7231 | 0.0266 | 0.0532 | 0.0226 | 0.0452 | 0.1994 | 72.0000 | 19 | 0.0113 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p03_sk0p08_sam0p02_shr0p09_srs0p5_spg0p5_mfs0_ffp0p01_pt0p03_pd1_lg0_byg0_plg0p04_clb0p5 | 0 | seed_000 | -0.8158 | -0.6973 | 0.0066 | 0.0132 | 0.0127 | 0.0254 | 0.1198 | 93.0000 | 6 | 0.0059 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| teacher_p0p64_rs0p03_sk0p08_sa0_shr0p09_srs1_spg1_mfs0p25_ffp0p005_pt0p03_pd1_lgm0p5_bygm1_plg0p06_clb1 | 0 | seed_000 | -0.8359 | -0.6959 | 0.0252 | 0.0504 | 0.0227 | 0.0455 | 0.1751 | 80.0000 | 23 | 0.0114 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p12_sam0p02_shr0p06_srs0p5_spg1_mfs0p25_ffp0p01_pt0_pd2_lgm2_byg0p5_plg0p1_clb0p5 | 0 | seed_000 | -0.8372 | -0.8155 | 0.0131 | 0.0263 | 0.0139 | 0.0277 | 0.1641 | 82.0000 | 19 | 0.0069 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0_sk0p12_sa0p02_shr0p09_srs0p5_spg0p5_mfs0_ffp0p01_pt0p03_pd1_lgm0p5_byg0_plg0p04_clb1 | 0 | seed_000 | -0.8471 | -0.7873 | 0.0259 | 0.0518 | 0.0242 | 0.0483 | 0.1981 | 77.0000 | 19 | 0.0137 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p03_sk0p08_sa0_shr0p06_srs1_spg1_mfs0_ffp0p005_pt0_pd2_lgm1p5_bygm1p5_plg0p08_clb1 | 0 | seed_000 | -0.8559 | -0.7690 | 0.0115 | 0.0229 | 0.0188 | 0.0375 | 0.1802 | 82.0000 | 13 | 0.0095 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p06_sk0p12_sa0_shr0p06_srs1_spg1_mfs0p25_ffp0p01_pt0p03_pd2_lgm1_bygm1_plg0p08_clb1 | 0 | seed_000 | -0.8561 | -0.8125 | 0.0279 | 0.0557 | 0.0274 | 0.0548 | 0.2069 | 72.0000 | 20 | 0.0181 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p01_sk0p12_sa0_shr0p06_srs0p5_spg0p5_mfs0p25_ffp0p02_pt0p03_pd1_lgm2_bygm2_plg0p06_clb1 | 0 | seed_002 | -0.8650 | -0.7282 | 0.0201 | 0.0402 | 0.0178 | 0.0357 | 0.1974 | 72.0000 | 26 | 0.0113 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p01_sk0p12_sam0p02_shr0p09_srs1_spg1_mfs0_ffp0p01_pt0p03_pd2_lgm0p5_byg0p5_plg0p08_clb1 | 0 | seed_000 | -0.8807 | -0.7283 | 0.0226 | 0.0452 | 0.0194 | 0.0387 | 0.1706 | 86.0000 | 13 | 0.0109 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p06_sk0p08_sa0_shr0p09_srs0p5_spg0p5_mfs0_ffp0p01_pt0p03_pd1_lgm0p5_bygm2_plg0p06_clb0p5 | 0 | seed_000 | -0.8814 | -0.7257 | 0.0070 | 0.0140 | 0.0112 | 0.0224 | 0.1133 | 85.0000 | 21 | 0.0067 | `low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0_sk0p12_sa0_shr0p06_srs1_spg1_mfs0_ffp0p02_pt0p03_pd2_lgm0p5_byg0p5_plg0p08_clb0p5 | 0 | seed_000 | -0.9170 | -0.8079 | 0.0158 | 0.0315 | 0.0196 | 0.0392 | 0.1873 | 82.0000 | 22 | 0.0109 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p03_sk0p08_sam0p02_shr0p06_srs0p5_spg0p5_mfs0p25_ffp0p005_pt0_pd1_lgm2_bygm1p5_plg0p04_clb0p5 | 0 | seed_000 | -0.9215 | -0.8950 | 0.0069 | 0.0138 | 0.0076 | 0.0152 | 0.1144 | 94.0000 | 8 | 0.0045 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| teacher_p0p56_rs0_sk0p12_sa0_shr0p09_srs1_spg1_mfs0_ffp0p01_pt0p03_pd2_lg0_bygm2_plg0p1_clb0p5 | 0 | seed_000 | -0.9415 | -0.7490 | 0.0275 | 0.0550 | 0.0191 | 0.0382 | 0.1665 | 88.0000 | 14 | 0.0070 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p01_sk0p12_sam0p02_shr0p06_srs0p5_spg1_mfs0_ffp0p02_pt0p03_pd1_lgm1p5_bygm2_plg0p04_clb1 | 0 | seed_002 | -0.9557 | -0.8493 | 0.0175 | 0.0349 | 0.0129 | 0.0257 | 0.1782 | 81.0000 | 20 | 0.0092 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p03_sk0p08_sa0_shr0p09_srs1_spg1_mfs0p25_ffp0p02_pt0p03_pd1_lgm2_byg0p5_plg0p08_clb1 | 0 | seed_000 | -0.9722 | -0.7729 | 0.0132 | 0.0264 | 0.0172 | 0.0344 | 0.1535 | 89.0000 | 14 | 0.0100 | `high_lateral_velocity, high_sent_target_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p01_sk0p08_sa0p02_shr0p06_srs1_spg0p5_mfs0_ffp0p005_pt0p03_pd1_lg0_bygm1_plg0p1_clb1 | 0 | seed_000 | -0.9750 | -0.8170 | 0.0190 | 0.0379 | 0.0252 | 0.0504 | 0.1907 | 74.0000 | 19 | 0.0129 | `high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
