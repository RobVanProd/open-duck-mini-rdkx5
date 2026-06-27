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
- min_forward_displacement_m: `0.004`
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
- `too_little_single_support`: `41`
- `single_support_not_balanced`: `33`
- `high_lateral_velocity`: `7`

### seed_002
- `low_forward_displacement`: `48`
- `low_forward_velocity`: `48`
- `double_support_dominates`: `45`
- `too_little_single_support`: `43`
- `single_support_not_balanced`: `16`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p2_lo0p02_byg0p02_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.4566 | -0.3934 | -0.0019 | -0.0037 | 0.0009 | 0.0017 | 0.0950 | 73.0000 | 31 | 0.0077 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p2_lo0p02_byg0p02_lvg0p12_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0p01_sk0p08_sa0_shr0p06_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.4566 | -0.3934 | -0.0019 | -0.0037 | 0.0009 | 0.0017 | 0.0950 | 73.0000 | 31 | 0.0077 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p2_lo0p02_byg0p02_lvg0p12_som0p02_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0_sk0p12_sa0_shr0p04_srs0p3_gs1_pt0_pd1 | 0 | seed_000 | -0.4566 | -0.3934 | -0.0019 | -0.0037 | 0.0009 | 0.0017 | 0.0950 | 73.0000 | 31 | 0.0077 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p02_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0p01_sk0p12_sa0_shr0p06_srs0p3_gs1_pt0_pd1 | 0 | seed_000 | -0.4566 | -0.4229 | -0.0019 | -0.0037 | 0.0009 | 0.0018 | 0.0950 | 78.0000 | 24 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p02_byg0p035_lvg0p08_so0_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0_sk0p12_sa0_shr0p04_srs0p3_gs1_pt0_pd1 | 0 | seed_002 | -0.4641 | -0.4492 | -0.0009 | -0.0019 | 0.0011 | 0.0022 | 0.0950 | 81.0000 | 22 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p02_byg0p035_lvg0p12_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0_sk0p08_sa0_shr0p04_srs0p5_gs1_pt0_pd1 | 0 | seed_002 | -0.4641 | -0.4492 | -0.0009 | -0.0019 | 0.0011 | 0.0022 | 0.0950 | 81.0000 | 22 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p02_byg0p035_lvg0p12_so0_kpy3_kdy0p5_kpx1_kpvx1_ffp0p005_sap0p01_sk0p12_sa0_shr0p06_srs0p5_gs1_pt0_pd1 | 0 | seed_002 | -0.4641 | -0.4492 | -0.0009 | -0.0019 | 0.0011 | 0.0022 | 0.0950 | 81.0000 | 22 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p02_byg0p035_lvg0p12_so0_kpy2_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0p01_sk0p12_sa0_shr0p06_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.8301 | -0.7100 | -0.0058 | -0.0115 | 0.0009 | 0.0018 | 0.0866 | 84.0000 | 19 | 0.0075 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p02_byg0p035_lvg0p08_som0p02_kpy2_kdy0p5_kpx0_kpvx1_ffp0p015_sap0_sk0p08_sa0_shr0p04_srs0p3_gs1_pt0_pd1 | 0 | seed_000 | -0.8301 | -0.7505 | -0.0058 | -0.0115 | 0.0008 | 0.0017 | 0.0866 | 86.0000 | 13 | 0.0075 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p02_byg0p035_lvg0p08_so0_kpy2_kdy0p5_kpx0_kpvx1_ffp0p015_sap0_sk0p08_sa0_shr0p04_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.8301 | -0.7690 | -0.0058 | -0.0115 | 0.0010 | 0.0019 | 0.0866 | 87.0000 | 13 | 0.0075 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p02_byg0p02_lvg0p08_so0_kpy2_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.8301 | -0.8102 | -0.0058 | -0.0115 | 0.0009 | 0.0017 | 0.0866 | 89.0000 | 10 | 0.0075 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p02_byg0p02_lvg0p08_som0p02_kpy2_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0p01_sk0p12_sa0_shr0p06_srs0p3_gs1_pt0_pd1 | 0 | seed_000 | -0.8301 | -0.8102 | -0.0058 | -0.0115 | 0.0009 | 0.0017 | 0.0866 | 89.0000 | 10 | 0.0075 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p02_byg0p035_lvg0p12_so0_kpy2_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0_sk0p08_sa0_shr0p04_srs0p3_gs1_pt0_pd1 | 0 | seed_002 | -0.8487 | -0.8394 | -0.0058 | -0.0115 | 0.0009 | 0.0019 | 0.0866 | 90.0000 | 8 | 0.0075 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p03_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0_sk0p12_sa0_shr0p04_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.8731 | -0.7870 | -0.0025 | -0.0051 | 0.0012 | 0.0025 | 0.0918 | 87.0000 | 13 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p02_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0p01_sk0p08_sa0_shr0p04_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.9118 | -0.8063 | -0.0033 | -0.0066 | 0.0012 | 0.0025 | 0.0918 | 87.0000 | 13 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.9118 | -0.8063 | -0.0033 | -0.0066 | 0.0012 | 0.0025 | 0.0918 | 87.0000 | 13 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p03_byg0p02_lvg0p12_som0p02_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0p01_sk0p08_sa0_shr0p04_srs0p3_gs1_pt0_pd1 | 0 | seed_000 | -0.9118 | -0.8063 | -0.0033 | -0.0066 | 0.0012 | 0.0025 | 0.0918 | 87.0000 | 13 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p03_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0p01_sk0p08_sa0_shr0p06_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.9118 | -0.8063 | -0.0033 | -0.0066 | 0.0012 | 0.0025 | 0.0918 | 87.0000 | 13 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p03_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.9118 | -0.8063 | -0.0033 | -0.0066 | 0.0012 | 0.0025 | 0.0918 | 87.0000 | 13 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p03_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0_sk0p08_sa0_shr0p04_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.9118 | -0.8063 | -0.0033 | -0.0066 | 0.0012 | 0.0025 | 0.0918 | 87.0000 | 13 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p03_byg0p02_lvg0p12_so0_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0p01_sk0p12_sa0_shr0p06_srs0p3_gs1_pt0_pd1 | 0 | seed_000 | -0.9184 | -0.8097 | -0.0028 | -0.0055 | 0.0012 | 0.0025 | 0.0918 | 87.0000 | 13 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p03_byg0p02_lvg0p08_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0p01_sk0p08_sa0_shr0p06_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.9426 | -0.8931 | -0.0029 | -0.0059 | 0.0011 | 0.0023 | 0.0918 | 90.0000 | 8 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p02_byg0p035_lvg0p12_som0p02_kpy2_kdy0p5_kpx1_kpvx1_ffp0p015_sap0p01_sk0p12_sa0_shr0p04_srs0p5_gs1_pt0_pd1 | 0 | seed_000 | -0.9626 | -0.9337 | -0.0054 | -0.0109 | 0.0011 | 0.0022 | 0.0866 | 91.0000 | 6 | 0.0075 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p02_byg0p02_lvg0p08_som0p02_kpy2_kdy0p5_kpx0_kpvx1_ffp0p005_sap0p01_sk0p08_sa0_shr0p06_srs0p3_gs1_pt0_pd1 | 0 | seed_000 | -0.9626 | -0.9337 | -0.0054 | -0.0109 | 0.0011 | 0.0022 | 0.0866 | 91.0000 | 6 | 0.0075 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p02_byg0p02_lvg0p08_som0p02_kpy2_kdy0p5_kpx0_kpvx1_ffp0p005_sap0p01_sk0p12_sa0_shr0p04_srs0p3_gs1_pt0_pd1 | 0 | seed_000 | -0.9626 | -0.9337 | -0.0054 | -0.0109 | 0.0011 | 0.0022 | 0.0866 | 91.0000 | 6 | 0.0075 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
