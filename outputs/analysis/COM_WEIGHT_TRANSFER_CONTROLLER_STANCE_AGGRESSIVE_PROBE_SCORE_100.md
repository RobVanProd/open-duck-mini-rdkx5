# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `48`
- mode_count: `24`
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
- `low_forward_displacement`: `24`
- `low_forward_velocity`: `24`
- `double_support_dominates`: `13`
- `too_little_single_support`: `11`
- `single_support_not_balanced`: `5`
- `single_contact_pattern_dominates`: `2`

### seed_002
- `low_forward_displacement`: `24`
- `low_forward_velocity`: `24`
- `double_support_dominates`: `9`
- `too_little_single_support`: `2`
- `single_support_not_balanced`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx2_ffp0p03_sk0p1_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_002 | -0.3787 | -0.3503 | 0.0127 | 0.0254 | 0.0105 | 0.0209 | 0.0960 | 79.0000 | 19 | 0.0075 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_kpy2_kdy0p2_kpvx2_ffp0p04_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.4004 | -0.3897 | 0.0104 | 0.0209 | 0.0096 | 0.0192 | 0.0865 | 80.0000 | 16 | 0.0073 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p04_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.4190 | -0.4145 | 0.0092 | 0.0184 | 0.0088 | 0.0177 | 0.0557 | 90.0000 | 16 | 0.0067 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p03_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_000 | -0.4194 | -0.4157 | 0.0088 | 0.0176 | 0.0091 | 0.0182 | 0.0537 | 86.0000 | 16 | 0.0063 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx2_ffp0p04_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_002 | -0.4608 | -0.4410 | 0.0088 | 0.0175 | 0.0072 | 0.0143 | 0.0816 | 83.0000 | 17 | 0.0060 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p02_byg0p03_lvg0p12_kpy2_kdy0p2_kpvx2_ffp0p03_sk0p1_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_000 | -0.4611 | -0.4579 | 0.0072 | 0.0143 | 0.0074 | 0.0148 | 0.0572 | 86.0000 | 15 | 0.0059 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx2_ffp0p04_sk0p08_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_002 | -0.4611 | -0.4543 | 0.0077 | 0.0154 | 0.0088 | 0.0175 | 0.0518 | 92.0000 | 16 | 0.0067 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p04_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_002 | -0.4654 | -0.4424 | 0.0088 | 0.0176 | 0.0086 | 0.0172 | 0.0568 | 92.0000 | 13 | 0.0062 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_kpy2_kdy0p2_kpvx2_ffp0p04_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_002 | -0.4668 | -0.4440 | 0.0088 | 0.0175 | 0.0069 | 0.0139 | 0.0816 | 83.0000 | 16 | 0.0060 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx2_ffp0p02_sk0p08_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_002 | -0.4704 | -0.4651 | 0.0072 | 0.0144 | 0.0076 | 0.0152 | 0.0509 | 91.0000 | 15 | 0.0055 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p02_byg0p03_lvg0p12_kpy2_kdy0p2_kpvx1_ffp0p03_sk0p08_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_002 | -0.5219 | -0.5041 | 0.0069 | 0.0139 | 0.0047 | 0.0094 | 0.0525 | 88.0000 | 17 | 0.0047 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p03_sk0p1_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_002 | -0.5252 | -0.4656 | 0.0094 | 0.0187 | 0.0046 | 0.0092 | 0.0690 | 82.0000 | 18 | 0.0056 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx2_ffp0p04_sk0p1_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_000 | -0.5606 | -0.5467 | 0.0056 | 0.0112 | 0.0075 | 0.0150 | 0.0581 | 92.0000 | 8 | 0.0053 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx2_ffp0p04_sk0p1_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_000 | -0.5609 | -0.5285 | 0.0096 | 0.0191 | 0.0090 | 0.0179 | 0.0540 | 93.0000 | 12 | 0.0067 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p12_kpy1_kdy0p2_kpvx2_ffp0p02_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_000 | -0.5925 | -0.5249 | 0.0059 | 0.0118 | 0.0081 | 0.0162 | 0.0540 | 91.0000 | 11 | 0.0055 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p02_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_000 | -0.5925 | -0.5249 | 0.0059 | 0.0118 | 0.0081 | 0.0162 | 0.0540 | 91.0000 | 11 | 0.0055 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx2_ffp0p04_sk0p08_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6111 | -0.5709 | 0.0076 | 0.0151 | 0.0076 | 0.0151 | 0.0568 | 93.0000 | 12 | 0.0059 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p12_kpy1_kdy0p2_kpvx2_ffp0p03_sk0p08_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_002 | -0.6198 | -0.5696 | 0.0080 | 0.0160 | 0.0008 | 0.0016 | 0.1030 | 90.0000 | 8 | 0.0084 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p04_sk0p08_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_002 | -0.6198 | -0.5696 | 0.0080 | 0.0160 | 0.0008 | 0.0016 | 0.1030 | 90.0000 | 8 | 0.0084 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p02_sk0p08_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_002 | -0.6198 | -0.5696 | 0.0080 | 0.0160 | 0.0008 | 0.0016 | 0.1030 | 90.0000 | 8 | 0.0084 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p02_sk0p1_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_000 | -0.7090 | -0.6459 | 0.0092 | 0.0185 | 0.0023 | 0.0046 | 0.1037 | 90.0000 | 8 | 0.0077 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx2_ffp0p04_sk0p1_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_000 | -0.7090 | -0.6497 | 0.0092 | 0.0185 | 0.0020 | 0.0040 | 0.1037 | 88.0000 | 12 | 0.0077 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy1_kdy0p2_kpvx1_ffp0p03_sk0p08_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_000 | -0.8162 | -0.7036 | -0.0040 | -0.0080 | 0.0020 | 0.0039 | 0.0987 | 90.0000 | 4 | 0.0077 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p04_sk0p08_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_000 | -0.8162 | -0.7131 | -0.0040 | -0.0080 | 0.0020 | 0.0040 | 0.0987 | 91.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
