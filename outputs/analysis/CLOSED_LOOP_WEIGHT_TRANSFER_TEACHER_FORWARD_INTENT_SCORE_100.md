# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `72`
- mode_count: `36`
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
- `low_forward_velocity`: `36`
- `high_lateral_velocity`: `35`
- `low_forward_displacement`: `22`
- `high_sent_target_velocity`: `3`
- `single_support_not_balanced`: `3`
- `action_saturation`: `2`
- `double_support_dominates`: `2`
- `high_body_pitch`: `1`
- `low_base_height`: `1`
- `single_contact_pattern_dominates`: `1`
- `too_little_single_support`: `1`

### seed_002
- `low_forward_velocity`: `36`
- `high_lateral_velocity`: `34`
- `low_forward_displacement`: `17`
- `high_sent_target_velocity`: `3`
- `action_saturation`: `2`
- `low_base_height`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| teacher_p0p64_rs0p02_sk0p12_sa0p02_shr0p06_srs0p5_spg0p5_mfs0_ffp0p01_pt0p03_pd2_lgm0p5_bygm1_plg0p06_clb1 | 0 | seed_000 | -0.6608 | -0.6596 | 0.0259 | 0.0518 | 0.0210 | 0.0420 | 0.1859 | 80.0000 | 20 | 0.0126 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p06_sk0p12_sa0p02_shr0p09_srs1_spg1p5_mfs0p5_ffp0p02_pt0p03_pd2_lgm1_byg0_plg0p12_clb0 | 0 | seed_000 | -0.7579 | -0.6964 | 0.0255 | 0.0510 | 0.0170 | 0.0341 | 0.1637 | 76.0000 | 21 | 0.0111 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p12_sam0p02_shr0p06_srs0p5_spg1_mfs0p75_ffp0p01_ptm0p03_pd2_lgm1_bygm0p5_plg0p08_clb1 | 0 | seed_002 | -0.8690 | -0.8071 | 0.0145 | 0.0290 | 0.0148 | 0.0296 | 0.1791 | 82.0000 | 21 | 0.0071 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p06_sk0p12_sam0p02_shr0p06_srs0p5_spg1_mfs0p75_ffp0p005_pt0p03_pd1_lgm1_bygm0p5_plg0p12_clb0 | 0 | seed_000 | -0.9328 | -0.9252 | 0.0076 | 0.0152 | 0.0041 | 0.0083 | 0.1154 | 81.0000 | 25 | 0.0065 | `low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p04_sk0p12_sam0p02_shr0p09_srs1_spg1p5_mfs0p25_ffp0p01_pt0_pd1_lgm0p5_bygm1_plg0p06_clb0p5 | 0 | seed_000 | -0.9591 | -0.8176 | 0.0214 | 0.0428 | 0.0185 | 0.0370 | 0.1779 | 76.0000 | 23 | 0.0090 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p48_rs0p06_sk0p08_sam0p02_shr0p06_srs0p5_spg0p5_mfs0p5_ffp0p005_pt0_pd1_lgm0p5_bygm0p5_plg0p08_clb0p5 | 0 | seed_000 | -0.9948 | -0.9502 | 0.0027 | 0.0054 | 0.0104 | 0.0207 | 0.1568 | 78.0000 | 26 | 0.0063 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p16_sa0_shr0p03_srs1_spg1_mfs0p5_ffp0p02_pt0p03_pd2_lgm0p5_bygm1_plg0p08_clb0 | 0 | seed_002 | -1.0298 | -1.0225 | 0.0269 | 0.0538 | 0.0192 | 0.0383 | 0.2261 | 69.0000 | 21 | 0.0102 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p04_sk0p12_sa0_shr0p09_srs1_spg1_mfs0p75_ffp0_pt0p03_pd2_lg0_byg0p5_plg0p06_clb0 | 0 | seed_000 | -1.0368 | -0.8974 | 0.0062 | 0.0124 | 0.0150 | 0.0300 | 0.1665 | 88.0000 | 10 | 0.0073 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p08_sam0p02_shr0p09_srs1_spg1_mfs0_ffp0p02_pt0_pd2_lg1_byg0p5_plg0p12_clb0 | 0 | seed_000 | -1.0533 | -0.8386 | 0.0014 | 0.0027 | 0.0101 | 0.0202 | 0.1117 | 89.0000 | 18 | 0.0057 | `low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p06_sk0p08_sam0p02_shr0p09_srs0p5_spg1_mfs0_ffp0p005_ptm0p03_pd1_lgm1_byg1_plg0p08_clb0p5 | 0 | seed_000 | -1.1061 | -1.0154 | 0.0087 | 0.0174 | 0.0082 | 0.0164 | 0.1459 | 76.0000 | 28 | 0.0061 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p06_sk0p12_sam0p02_shr0p06_srs1_spg1p5_mfs0p5_ffp0p005_pt0_pd2_lgm0p5_bygm1_plg0p08_clb1 | 0 | seed_002 | -1.1078 | -1.0593 | 0.0287 | 0.0573 | 0.0290 | 0.0580 | 0.2511 | 63.0000 | 23 | 0.0133 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p12_sa0_shr0p03_srs1_spg1_mfs0_ffp0p005_pt0_pd1_lgm0p5_bygm1_plg0p06_clb0 | 0 | seed_000 | -1.1700 | -1.0665 | 0.0064 | 0.0128 | 0.0078 | 0.0156 | 0.1481 | 89.0000 | 7 | 0.0066 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p12_sa0p02_shr0p03_srs1_spg1_mfs0p5_ffp0p005_ptm0p03_pd1_lg0_byg1_plg0p12_clb1 | 0 | seed_002 | -1.1938 | -1.0760 | 0.0238 | 0.0476 | 0.0194 | 0.0388 | 0.2480 | 62.0000 | 24 | 0.0099 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p06_sk0p16_sa0p02_shr0p03_srs0p5_spg1_mfs0p5_ffp0_pt0_pd1_lgm1_bygm1_plg0p08_clb0 | 0 | seed_002 | -1.1990 | -1.0428 | 0.0299 | 0.0598 | 0.0278 | 0.0556 | 0.2611 | 61.0000 | 20 | 0.0144 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p16_sa0_shr0p03_srs1_spg1p5_mfs0p5_ffp0_pt0p03_pd1_lg0_bygm0p5_plg0p12_clb0 | 0 | seed_000 | -1.2173 | -1.1385 | 0.0239 | 0.0477 | 0.0264 | 0.0528 | 0.2422 | 67.0000 | 20 | 0.0120 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p06_sk0p08_sam0p02_shr0p09_srs0p5_spg1_mfs0_ffp0p01_pt0_pd1_lgm1_byg1_plg0p06_clb0p5 | 0 | seed_000 | -1.2307 | -0.9595 | 0.0113 | 0.0226 | 0.0117 | 0.0235 | 0.1379 | 85.0000 | 15 | 0.0060 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p06_sk0p08_sa0p02_shr0p03_srs1_spg1p5_mfs0_ffp0p01_pt0_pd1_lg0_byg0_plg0p06_clb0p5 | 0 | seed_002 | -1.2985 | -1.2835 | 0.0022 | 0.0045 | 0.0015 | 0.0030 | 0.1515 | 87.0000 | 22 | 0.0058 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p12_sa0p02_shr0p03_srs1_spg0p5_mfs0p5_ffp0p01_ptm0p03_pd1_lg0_bygm0p5_plg0p06_clb0 | 0 | seed_000 | -1.3201 | -1.1607 | 0.0020 | 0.0040 | 0.0155 | 0.0310 | 0.2002 | 84.0000 | 13 | 0.0096 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p06_sk0p08_sam0p02_shr0p03_srs0p5_spg1_mfs0p75_ffp0p02_pt0_pd2_lgm1_byg1_plg0p06_clb1 | 0 | seed_000 | -1.4255 | -1.1777 | 0.0122 | 0.0243 | 0.0087 | 0.0175 | 0.1498 | 88.0000 | 22 | 0.0076 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p48_rs0p04_sk0p12_sa0p02_shr0p03_srs0p5_spg0p5_mfs0p25_ffp0p005_pt0_pd2_lg0_bygm0p5_plg0p06_clb0p5 | 0 | seed_000 | -1.4466 | -1.4083 | 0.0153 | 0.0306 | 0.0278 | 0.0556 | 0.2825 | 64.0000 | 21 | 0.0121 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p12_sam0p02_shr0p03_srs1_spg0p5_mfs0_ffp0p02_pt0p03_pd2_lg0_bygm1_plg0p06_clb0p5 | 0 | seed_000 | -1.5096 | -1.3012 | 0.0109 | 0.0217 | 0.0211 | 0.0423 | 0.2404 | 72.0000 | 20 | 0.0108 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p04_sk0p16_sam0p02_shr0p03_srs1_spg1p5_mfs0p75_ffp0p01_pt0p03_pd1_lg0_byg0_plg0p08_clb0p5 | 0 | seed_000 | -1.6693 | -1.6577 | 0.0235 | 0.0471 | 0.0287 | 0.0575 | 0.3181 | 53.0000 | 24 | 0.0099 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p12_sa0_shr0p06_srs0p5_spg0p5_mfs0p25_ffp0_pt0p03_pd2_lg1_byg1_plg0p08_clb1 | 0 | seed_002 | -1.7325 | -1.4903 | 0.0168 | 0.0336 | 0.0296 | 0.0593 | 0.3299 | 58.0000 | 29 | 0.0145 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p06_sk0p08_sa0p02_shr0p03_srs1_spg1p5_mfs0p5_ffp0p005_ptm0p03_pd2_lg1_bygm0p5_plg0p06_clb0 | 0 | seed_000 | -1.7476 | -1.6084 | -0.0013 | -0.0027 | 0.0105 | 0.0210 | 0.2280 | 70.0000 | 27 | 0.0086 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p12_sa0_shr0p06_srs0p5_spg1_mfs0p5_ffp0p01_pt0_pd1_lg1_bygm0p5_plg0p06_clb0p5 | 0 | seed_000 | -1.8281 | -1.5702 | 0.0262 | 0.0524 | 0.0238 | 0.0476 | 0.2708 | 69.0000 | 27 | 0.0082 | `high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
