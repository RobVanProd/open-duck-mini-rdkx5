# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `96`
- mode_count: `48`
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
- `low_forward_velocity`: `47`
- `high_lateral_velocity`: `46`
- `low_forward_displacement`: `37`
- `high_sent_target_velocity`: `10`
- `single_support_not_balanced`: `3`
- `double_support_dominates`: `2`
- `low_base_height`: `2`
- `missing_seed_trace_or_window`: `1`
- `too_little_single_support`: `1`

### seed_002
- `low_forward_velocity`: `47`
- `high_lateral_velocity`: `46`
- `low_forward_displacement`: `36`
- `high_sent_target_velocity`: `10`
- `double_support_dominates`: `4`
- `low_base_height`: `3`
- `high_body_pitch`: `1`
- `missing_seed_trace_or_window`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| teacher_p0p56_rs0p02_sk0p08_sa0p02_shr0p09_srs0p5_spg1_mfs0p25_ffp0p01_pt0_pd2_lgm1_bygm0p5_plg0p04_clb1 | 0 | seed_002 | -1.0249 | -0.9444 | 0.0137 | 0.0411 | 0.0124 | 0.0372 | 0.1650 | 85.3333 | 19 | 0.0076 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p03_sk0p12_sam0p02_shr0p06_srs0p5_spg0p5_mfs0p25_ffp0p01_pt0p03_pd1_lgm2_byg0_plg0p04_clb1 | 0 | seed_000 | -1.0544 | -0.9562 | 0.0138 | 0.0414 | 0.0169 | 0.0507 | 0.1829 | 76.0000 | 24 | 0.0104 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p01_sk0p08_sa0p02_shr0p06_srs1_spg0p5_mfs0_ffp0p005_pt0p03_pd1_lg0_bygm1_plg0p1_clb1 | 0 | seed_000 | -1.1613 | -0.9918 | 0.0167 | 0.0501 | 0.0196 | 0.0588 | 0.2018 | 74.0000 | 29 | 0.0122 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0_sk0p12_sam0p02_shr0p09_srs1_spg1_mfs0p25_ffp0p005_pt0p03_pd1_lgm0p5_bygm1p5_plg0p1_clb1 | 0 | seed_002 | -1.2104 | -1.0421 | 0.0227 | 0.0682 | 0.0202 | 0.0605 | 0.2245 | 67.3333 | 35 | 0.0113 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| teacher_p0p64_rs0_sk0p12_sa0p02_shr0p09_srs0p5_spg0p5_mfs0_ffp0p02_pt0p03_pd2_lgm0p5_byg0_plg0p1_clb0p5 | 0 | seed_002 | -1.2566 | -1.2479 | 0.0116 | 0.0349 | 0.0149 | 0.0448 | 0.2158 | 72.6667 | 35 | 0.0139 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p01_sk0p12_sa0_shr0p06_srs0p5_spg0p5_mfs0p25_ffp0p02_pt0p03_pd1_lgm2_bygm2_plg0p06_clb1 | 0 | seed_002 | -1.2869 | -1.0868 | 0.0192 | 0.0575 | 0.0166 | 0.0497 | 0.2336 | 66.6667 | 41 | 0.0107 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0_sk0p12_sa0p02_shr0p09_srs0p5_spg0p5_mfs0_ffp0p01_pt0p03_pd1_lgm0p5_byg0_plg0p04_clb1 | 0 | seed_000 | -1.2933 | -1.1657 | 0.0140 | 0.0421 | 0.0176 | 0.0527 | 0.2114 | 70.6667 | 33 | 0.0135 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0_sk0p08_sa0p02_shr0p06_srs1_spg1_mfs0_ffp0p02_pt0p03_pd2_lg0_byg0_plg0p1_clb1 | 0 | seed_000 | -1.3173 | -1.2020 | 0.0131 | 0.0394 | 0.0160 | 0.0481 | 0.2041 | 77.3333 | 24 | 0.0105 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p03_sk0p12_sa0_shr0p06_srs0p5_spg0p5_mfs0_ffp0p02_pt0_pd2_lgm1p5_bygm1p5_plg0p08_clb1 | 0 | seed_002 | -1.3417 | -1.3386 | 0.0186 | 0.0557 | 0.0238 | 0.0715 | 0.2511 | 62.0000 | 45 | 0.0121 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p12_sam0p02_shr0p06_srs0p5_spg1_mfs0p25_ffp0p01_pt0_pd2_lgm2_byg0p5_plg0p1_clb0p5 | 0 | seed_002 | -1.3430 | -1.3211 | 0.0088 | 0.0264 | 0.0091 | 0.0274 | 0.1766 | 76.0000 | 30 | 0.0082 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0_sk0p12_sa0_shr0p09_srs1_spg1_mfs0_ffp0p01_pt0p03_pd2_lg0_bygm2_plg0p1_clb0p5 | 0 | seed_000 | -1.3613 | -1.2923 | 0.0261 | 0.0784 | 0.0109 | 0.0326 | 0.1766 | 84.6667 | 20 | 0.0071 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p01_sk0p12_sam0p02_shr0p09_srs1_spg1_mfs0_ffp0p01_pt0p03_pd2_lgm0p5_byg0p5_plg0p08_clb1 | 0 | seed_000 | -1.4005 | -1.2889 | 0.0127 | 0.0382 | 0.0151 | 0.0453 | 0.2074 | 77.3333 | 24 | 0.0116 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p06_sk0p12_sa0_shr0p06_srs1_spg1_mfs0p25_ffp0p01_pt0p03_pd2_lgm1_bygm1_plg0p08_clb1 | 0 | seed_002 | -1.4014 | -1.2728 | 0.0177 | 0.0531 | 0.0196 | 0.0589 | 0.2746 | 64.0000 | 31 | 0.0167 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p01_sk0p08_sa0p02_shr0p06_srs0p5_spg1_mfs0p25_ffp0p005_pt0p03_pd1_lgm1_bygm1_plg0p08_clb1 | 0 | seed_000 | -1.4062 | -1.3522 | 0.0062 | 0.0187 | 0.0080 | 0.0239 | 0.1611 | 81.3333 | 26 | 0.0102 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p12_sa0p02_shr0p09_srs1_spg0p5_mfs0p25_ffp0p01_pt0p03_pd2_lgm2_byg0p5_plg0p1_clb0p5 | 0 | seed_002 | -1.4506 | -1.3780 | 0.0218 | 0.0655 | 0.0254 | 0.0762 | 0.2244 | 63.3333 | 34 | 0.0149 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p04_sk0p12_sa0_shr0p06_srs0p5_spg1_mfs0_ffp0p005_pt0_pd2_lgm1p5_byg0p5_plg0p04_clb1 | 0 | seed_000 | -1.4540 | -1.4052 | 0.0106 | 0.0319 | 0.0126 | 0.0377 | 0.2080 | 77.3333 | 30 | 0.0110 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p03_sk0p08_sam0p02_shr0p06_srs0p5_spg0p5_mfs0p25_ffp0p005_pt0_pd1_lgm2_bygm1p5_plg0p04_clb0p5 | 0 | seed_000 | -1.4770 | -1.4144 | 0.0006 | 0.0019 | 0.0028 | 0.0085 | 0.1201 | 91.3333 | 16 | 0.0047 | `double_support_dominates, high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p03_sk0p08_sa0_shr0p09_srs1_spg1_mfs0p25_ffp0p005_pt0p03_pd1_lgm0p5_bygm1_plg0p06_clb1 | 0 | seed_002 | -1.4834 | -1.2479 | 0.0193 | 0.0580 | 0.0079 | 0.0237 | 0.1794 | 77.3333 | 32 | 0.0109 | `high_lateral_velocity, high_sent_target_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p03_sk0p12_sam0p02_shr0p09_srs0p5_spg0p5_mfs0_ffp0p005_pt0_pd2_lgm1_byg0p5_plg0p1_clb1 | 0 | seed_002 | -1.5115 | -1.4505 | 0.0076 | 0.0228 | 0.0073 | 0.0218 | 0.1815 | 81.3333 | 27 | 0.0097 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p03_sk0p08_sa0_shr0p06_srs1_spg1_mfs0_ffp0p005_pt0_pd2_lgm1p5_bygm1p5_plg0p08_clb1 | 0 | seed_000 | -1.5255 | -1.4553 | 0.0041 | 0.0124 | 0.0089 | 0.0267 | 0.1800 | 82.0000 | 20 | 0.0094 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0_sk0p12_sa0p02_shr0p09_srs1_spg0p5_mfs0_ffp0p01_pt0_pd1_lgm1_bygm0p5_plg0p08_clb0p5 | 0 | seed_000 | -1.5959 | -1.5829 | 0.0243 | 0.0728 | 0.0232 | 0.0695 | 0.2398 | 65.3333 | 38 | 0.0119 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| teacher_p0p64_rs0_sk0p12_sa0_shr0p06_srs1_spg1_mfs0_ffp0p02_pt0p03_pd2_lgm0p5_byg0p5_plg0p08_clb0p5 | 0 | seed_000 | -1.6005 | -1.3740 | 0.0067 | 0.0202 | 0.0148 | 0.0445 | 0.2013 | 75.3333 | 37 | 0.0115 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p12_sam0p02_shr0p09_srs0p5_spg1_mfs0p25_ffp0p02_pt0p03_pd1_lgm0p5_bygm1_plg0p1_clb1 | 0 | seed_000 | -1.6220 | -1.5569 | 0.0034 | 0.0101 | 0.0059 | 0.0178 | 0.1676 | 86.0000 | 17 | 0.0075 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_p0p56_rs0p06_sk0p12_sa0p02_shr0p06_srs0p5_spg0p5_mfs0p25_ffp0p02_pt0_pd1_lg0_byg0_plg0p06_clb1 | 0 | seed_002 | -1.6265 | -1.6260 | 0.0249 | 0.0746 | 0.0284 | 0.0851 | 0.3126 | 62.6667 | 37 | 0.0189 | `high_body_pitch, high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0_sk0p08_sam0p02_shr0p09_srs0p5_spg1_mfs0p25_ffp0p005_pt0p03_pd2_lgm1_byg0_plg0p04_clb0p5 | 0 | seed_000 | -1.6359 | -1.4641 | 0.0016 | 0.0048 | 0.0033 | 0.0099 | 0.1157 | 86.6667 | 22 | 0.0087 | `low_forward_displacement, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
