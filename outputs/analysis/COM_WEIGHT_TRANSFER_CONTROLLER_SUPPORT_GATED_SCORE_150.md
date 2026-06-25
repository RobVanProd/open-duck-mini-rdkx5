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
- min_forward_displacement_m: `0.006`
- max_vy_abs_p95: `0.12`
- max_contact_dominance_pct: `95.0`
- max_double_support_pct: `75.0`
- max_no_support_pct: `100.0`
- min_single_support_pct: `20.0`
- min_each_single_support_pct: `5.0`
- max_pitch_abs_p95: `0.35`
- min_base_height: `0.145`
- max_sent_velocity_p95: `3.75`
- max_tracking_p95: `0.12`
- min_done_margin: `50`
- min_contact_transitions: `2`
- min_foot_site_z_p95: `-1.0`

## Seed Failure Counts

### seed_000
- `double_support_dominates`: `48`
- `low_forward_displacement`: `48`
- `low_forward_velocity`: `48`
- `too_little_single_support`: `44`
- `single_support_not_balanced`: `41`

### seed_002
- `double_support_dominates`: `48`
- `low_forward_displacement`: `48`
- `low_forward_velocity`: `48`
- `too_little_single_support`: `45`
- `single_support_not_balanced`: `40`
- `single_contact_pattern_dominates`: `7`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p2_lo0p02_byg0p02_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.5848 | -0.5096 | -0.0053 | -0.0159 | 0.0002 | 0.0006 | 0.0695 | 78.6667 | 41 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p2_lo0p02_byg0p02_lvg0p12_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0p01_sk0p08_sa0_shr0p06_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.5848 | -0.5096 | -0.0053 | -0.0159 | 0.0002 | 0.0006 | 0.0695 | 78.6667 | 41 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p2_lo0p02_byg0p02_lvg0p12_som0p02_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0_sk0p12_sa0_shr0p04_srs0p3_gs1_pt0_pd1 | 0 | seed_000 | -0.5848 | -0.5096 | -0.0053 | -0.0159 | 0.0002 | 0.0006 | 0.0695 | 78.6667 | 41 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p02_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0p01_sk0p12_sa0_shr0p06_srs0p3_gs1_pt0_pd1 | 0 | seed_000 | -0.5848 | -0.5561 | -0.0053 | -0.0159 | 0.0002 | 0.0007 | 0.0695 | 81.3333 | 36 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p02_byg0p035_lvg0p12_so0_kpy3_kdy0p5_kpx1_kpvx1_ffp0p005_sap0p01_sk0p12_sa0_shr0p06_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.6490 | -0.5852 | -0.0044 | -0.0132 | 0.0008 | 0.0024 | 0.0695 | 82.0000 | 37 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p02_byg0p035_lvg0p12_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0_sk0p08_sa0_shr0p04_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.6490 | -0.6174 | -0.0044 | -0.0132 | 0.0005 | 0.0014 | 0.0695 | 83.3333 | 31 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p02_byg0p035_lvg0p08_so0_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0_sk0p12_sa0_shr0p04_srs0p3_gs1_pt0_pd1 | 0 | seed_000 | -0.6490 | -0.6229 | -0.0044 | -0.0132 | 0.0005 | 0.0016 | 0.0695 | 83.3333 | 34 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p02_byg0p035_lvg0p12_so0_kpy2_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0p01_sk0p12_sa0_shr0p06_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.9406 | -0.8755 | -0.0041 | -0.0124 | 0.0003 | 0.0010 | 0.0708 | 88.6667 | 21 | 0.0029 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p02_byg0p035_lvg0p08_so0_kpy2_kdy0p5_kpx0_kpvx1_ffp0p015_sap0_sk0p08_sa0_shr0p04_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.9406 | -0.9075 | -0.0041 | -0.0124 | 0.0004 | 0.0012 | 0.0708 | 90.0000 | 16 | 0.0029 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p02_byg0p035_lvg0p08_som0p02_kpy2_kdy0p5_kpx0_kpvx1_ffp0p015_sap0_sk0p08_sa0_shr0p04_srs0p3_gs1_pt0_pd1 | 0 | seed_000 | -0.9406 | -0.9101 | -0.0041 | -0.0124 | 0.0003 | 0.0008 | 0.0708 | 90.0000 | 15 | 0.0029 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p02_byg0p02_lvg0p08_so0_kpy2_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.9406 | -0.9372 | -0.0041 | -0.0124 | 0.0002 | 0.0007 | 0.0708 | 91.3333 | 14 | 0.0029 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p02_byg0p02_lvg0p08_som0p02_kpy2_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0p01_sk0p12_sa0_shr0p06_srs0p3_gs1_pt0_pd1 | 0 | seed_000 | -0.9406 | -0.9372 | -0.0041 | -0.0124 | 0.0002 | 0.0007 | 0.0708 | 91.3333 | 14 | 0.0029 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p02_byg0p035_lvg0p12_so0_kpy2_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0_sk0p08_sa0_shr0p04_srs0p3_gs1_pt0_pd1 | 0 | seed_002 | -0.9986 | -0.9696 | -0.0041 | -0.0124 | 0.0003 | 0.0009 | 0.0708 | 92.6667 | 10 | 0.0029 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p03_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0_sk0p12_sa0_shr0p04_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -1.0015 | -0.9138 | -0.0031 | -0.0094 | 0.0007 | 0.0020 | 0.0702 | 89.3333 | 19 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p03_byg0p02_lvg0p08_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0p01_sk0p08_sa0_shr0p06_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -1.0136 | -0.9956 | -0.0035 | -0.0105 | 0.0005 | 0.0016 | 0.0702 | 92.0000 | 12 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p02_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0p01_sk0p08_sa0_shr0p04_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -1.0269 | -0.9263 | -0.0035 | -0.0105 | 0.0007 | 0.0020 | 0.0702 | 89.3333 | 19 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p03_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0_sk0p08_sa0_shr0p04_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -1.0269 | -0.9263 | -0.0035 | -0.0105 | 0.0007 | 0.0020 | 0.0702 | 89.3333 | 19 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p03_byg0p02_lvg0p12_som0p02_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0p01_sk0p08_sa0_shr0p04_srs0p3_gs1_pt0_pd1 | 0 | seed_000 | -1.0269 | -0.9263 | -0.0035 | -0.0105 | 0.0007 | 0.0020 | 0.0702 | 89.3333 | 19 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p03_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0p01_sk0p08_sa0_shr0p06_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -1.0269 | -0.9267 | -0.0035 | -0.0105 | 0.0007 | 0.0020 | 0.0702 | 89.3333 | 19 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -1.0269 | -0.9269 | -0.0035 | -0.0105 | 0.0006 | 0.0019 | 0.0702 | 89.3333 | 19 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p03_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -1.0269 | -0.9269 | -0.0035 | -0.0105 | 0.0006 | 0.0019 | 0.0702 | 89.3333 | 19 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p02_byg0p035_lvg0p12_som0p02_kpy2_kdy0p5_kpx1_kpvx1_ffp0p015_sap0p01_sk0p12_sa0_shr0p04_srs0p5_gs1_pt0_pd1 | 0 | seed_002 | -1.0329 | -1.0264 | -0.0041 | -0.0124 | 0.0005 | 0.0014 | 0.0708 | 93.3333 | 8 | 0.0029 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p02_byg0p02_lvg0p08_som0p02_kpy2_kdy0p5_kpx0_kpvx1_ffp0p005_sap0p01_sk0p08_sa0_shr0p06_srs0p3_gs1_pt0_pd1 | 0 | seed_002 | -1.0329 | -1.0264 | -0.0041 | -0.0124 | 0.0005 | 0.0014 | 0.0708 | 93.3333 | 8 | 0.0029 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p02_byg0p02_lvg0p08_som0p02_kpy2_kdy0p5_kpx0_kpvx1_ffp0p005_sap0p01_sk0p12_sa0_shr0p04_srs0p3_gs1_pt0_pd1 | 0 | seed_002 | -1.0329 | -1.0264 | -0.0041 | -0.0124 | 0.0005 | 0.0014 | 0.0708 | 93.3333 | 8 | 0.0029 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p02_byg0p035_lvg0p12_so0_kpy2_kdy0p5_kpx1_kpvx1_ffp0p005_sap0_sk0p08_sa0_shr0p06_srs0p3_gs1_pt0_pd1 | 0 | seed_002 | -1.0329 | -1.0264 | -0.0041 | -0.0124 | 0.0005 | 0.0014 | 0.0708 | 93.3333 | 8 | 0.0029 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
