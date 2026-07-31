# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `64`
- mode_count: `32`
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
- `double_support_dominates`: `32`
- `low_forward_displacement`: `32`
- `low_forward_velocity`: `32`
- `too_little_single_support`: `32`
- `single_support_not_balanced`: `30`
- `high_lateral_velocity`: `1`

### seed_002
- `double_support_dominates`: `32`
- `low_forward_velocity`: `32`
- `too_little_single_support`: `32`
- `low_forward_displacement`: `30`
- `single_support_not_balanced`: `23`
- `high_lateral_velocity`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p02_byg0p05_lvg0p12_so0_kpy4_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0_sk0p12_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_002 | -0.7696 | -0.7666 | 0.0011 | 0.0023 | 0.0017 | 0.0034 | 0.0950 | 88.0000 | 12 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p02_byg0p035_lvg0p08_so0_kpy4_kdy0p5_kpx1_kpvx1_ffp0p015_sap0_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.7738 | -0.7718 | -0.0009 | -0.0018 | 0.0017 | 0.0034 | 0.0950 | 88.0000 | 12 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p02_byg0p035_lvg0p12_so0_kpy4_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0p01_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.7869 | -0.7785 | 0.0002 | 0.0004 | 0.0017 | 0.0033 | 0.0950 | 88.0000 | 12 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p02_byg0p035_lvg0p12_so0_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0p01_sk0p12_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.8520 | -0.7815 | -0.0057 | -0.0114 | 0.0016 | 0.0033 | 0.0950 | 87.0000 | 12 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p02_byg0p05_lvg0p08_so0_kpy4_kdy0p5_kpx1_kpvx1_ffp0p005_sap0p01_sk0p08_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.8608 | -0.8154 | -0.0012 | -0.0024 | 0.0017 | 0.0034 | 0.0950 | 88.0000 | 12 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p02_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0p01_sk0p08_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.8665 | -0.7888 | 0.0002 | 0.0004 | 0.0016 | 0.0033 | 0.0950 | 87.0000 | 12 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p02_byg0p05_lvg0p12_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0p01_sk0p08_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.8800 | -0.7955 | -0.0003 | -0.0007 | 0.0016 | 0.0033 | 0.0950 | 87.0000 | 12 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p02_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.8850 | -0.7980 | 0.0011 | 0.0022 | 0.0016 | 0.0033 | 0.0950 | 87.0000 | 12 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p02_byg0p05_lvg0p12_so0_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p015_sap0_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9071 | -0.8091 | 0.0002 | 0.0004 | 0.0016 | 0.0033 | 0.0950 | 87.0000 | 12 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p02_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p005_sap0_sk0p08_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9081 | -0.8095 | 0.0002 | 0.0003 | 0.0016 | 0.0033 | 0.0950 | 87.0000 | 12 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p02_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0p01_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9389 | -0.8249 | -0.0011 | -0.0022 | 0.0016 | 0.0033 | 0.0950 | 87.0000 | 12 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p03_byg0p05_lvg0p08_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0_sk0p08_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9429 | -0.8935 | -0.0030 | -0.0059 | 0.0011 | 0.0022 | 0.0943 | 90.0000 | 6 | 0.0076 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p03_byg0p05_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0p01_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9645 | -0.8730 | -0.0030 | -0.0060 | 0.0012 | 0.0024 | 0.1193 | 88.0000 | 8 | 0.0082 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p02_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9729 | -0.8420 | -0.0000 | -0.0001 | 0.0016 | 0.0033 | 0.0950 | 87.0000 | 12 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9739 | -0.9013 | -0.0026 | -0.0052 | 0.0017 | 0.0035 | 0.0918 | 90.0000 | 8 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p03_byg0p035_lvg0p12_so0_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0p01_sk0p12_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9773 | -0.9243 | -0.0027 | -0.0054 | 0.0016 | 0.0033 | 0.0918 | 91.0000 | 6 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p05_lvg0p12_so0_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0p01_sk0p08_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9807 | -0.9664 | -0.0029 | -0.0057 | 0.0008 | 0.0016 | 0.0950 | 92.0000 | 2 | 0.0076 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p2_lo0p03_byg0p05_lvg0p12_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0p01_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0325 | -0.9332 | -0.0000 | -0.0000 | 0.0022 | 0.0044 | 0.1342 | 88.0000 | 8 | 0.0084 | `double_support_dominates, high_lateral_velocity, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p03_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0363 | -0.8781 | -0.0027 | -0.0054 | 0.0022 | 0.0045 | 0.0918 | 88.0000 | 12 | 0.0077 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p03_byg0p05_lvg0p08_so0_kpy4_kdy0p5_kpx0_kpvx1_ffp0p015_sap0p01_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0542 | -0.7827 | -0.0059 | -0.0118 | 0.0008 | 0.0017 | 0.1042 | 82.0000 | 14 | 0.0074 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p2_lo0p03_byg0p05_lvg0p08_so0_kpy4_kdy0p5_kpx0_kpvx0p5_ffp0p015_sap0p01_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0542 | -0.8819 | -0.0059 | -0.0118 | 0.0009 | 0.0018 | 0.1016 | 87.0000 | 9 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p03_byg0p05_lvg0p08_som0p02_kpy4_kdy0p5_kpx1_kpvx1_ffp0p015_sap0p01_sk0p08_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0542 | -0.8917 | -0.0059 | -0.0118 | 0.0009 | 0.0018 | 0.0936 | 87.0000 | 13 | 0.0075 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p035_lvg0p08_so0_kpy4_kdy0p5_kpx0_kpvx1_ffp0p005_sap0_sk0p12_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0542 | -0.9541 | -0.0059 | -0.0118 | 0.0015 | 0.0030 | 0.0950 | 90.0000 | 8 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p03_byg0p035_lvg0p08_so0_kpy4_kdy0p5_kpx1_kpvx1_ffp0p005_sap0p01_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0542 | -0.9541 | -0.0059 | -0.0118 | 0.0015 | 0.0030 | 0.0950 | 90.0000 | 8 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p03_byg0p035_lvg0p08_som0p02_kpy4_kdy0p5_kpx0_kpvx0p5_ffp0p015_sap0p01_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0542 | -0.9541 | -0.0059 | -0.0118 | 0.0015 | 0.0030 | 0.0950 | 90.0000 | 8 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
