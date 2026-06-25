# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `64`
- mode_count: `32`
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
- `double_support_dominates`: `32`
- `low_forward_displacement`: `32`
- `low_forward_velocity`: `32`
- `too_little_single_support`: `32`
- `single_support_not_balanced`: `30`

### seed_002
- `double_support_dominates`: `32`
- `low_forward_displacement`: `32`
- `low_forward_velocity`: `32`
- `too_little_single_support`: `32`
- `single_support_not_balanced`: `29`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p02_byg0p035_lvg0p12_so0_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0p01_sk0p12_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9368 | -0.8748 | -0.0044 | -0.0133 | 0.0007 | 0.0020 | 0.0695 | 88.6667 | 17 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p02_byg0p035_lvg0p08_so0_kpy4_kdy0p5_kpx1_kpvx1_ffp0p015_sap0_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9622 | -0.9371 | -0.0050 | -0.0151 | 0.0009 | 0.0027 | 0.0797 | 90.6667 | 16 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p02_byg0p05_lvg0p12_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0p01_sk0p08_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9636 | -0.8882 | -0.0044 | -0.0133 | 0.0007 | 0.0020 | 0.0695 | 88.6667 | 17 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p02_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9683 | -0.8905 | -0.0042 | -0.0125 | 0.0007 | 0.0020 | 0.0695 | 88.6667 | 17 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p02_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0p01_sk0p08_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9716 | -0.8922 | -0.0043 | -0.0128 | 0.0007 | 0.0020 | 0.0695 | 88.6667 | 17 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p02_byg0p05_lvg0p12_so0_kpy4_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0_sk0p12_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9744 | -0.8944 | -0.0046 | -0.0137 | 0.0010 | 0.0031 | 0.0788 | 88.6667 | 19 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p02_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0p01_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9756 | -0.8942 | -0.0044 | -0.0132 | 0.0007 | 0.0020 | 0.0695 | 88.6667 | 17 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p02_byg0p05_lvg0p08_so0_kpy4_kdy0p5_kpx1_kpvx1_ffp0p005_sap0p01_sk0p08_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9828 | -0.8621 | -0.0050 | -0.0151 | 0.0010 | 0.0030 | 0.0788 | 87.3333 | 22 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p02_byg0p035_lvg0p12_so0_kpy4_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0p01_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9875 | -0.9225 | -0.0052 | -0.0156 | 0.0009 | 0.0028 | 0.0788 | 89.3333 | 19 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -0.9981 | -0.9938 | -0.0030 | -0.0091 | 0.0010 | 0.0029 | 0.0702 | 92.6667 | 10 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p03_byg0p035_lvg0p12_so0_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0p01_sk0p12_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_002 | -1.0074 | -0.9901 | -0.0031 | -0.0092 | 0.0008 | 0.0025 | 0.0702 | 93.3333 | 8 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p02_byg0p05_lvg0p12_so0_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p015_sap0_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0272 | -0.9200 | -0.0043 | -0.0130 | 0.0007 | 0.0020 | 0.0695 | 88.6667 | 17 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p02_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p005_sap0_sk0p08_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0292 | -0.9210 | -0.0044 | -0.0132 | 0.0007 | 0.0020 | 0.0695 | 88.6667 | 17 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p02_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0440 | -0.9284 | -0.0045 | -0.0134 | 0.0007 | 0.0020 | 0.0695 | 88.6667 | 17 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p03_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0714 | -0.9703 | -0.0032 | -0.0097 | 0.0010 | 0.0029 | 0.0702 | 90.6667 | 16 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p03_byg0p05_lvg0p08_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0_sk0p08_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0745 | -1.0508 | -0.0033 | -0.0100 | 0.0006 | 0.0019 | 0.0669 | 93.3333 | 6 | 0.0031 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p2_lo0p03_byg0p05_lvg0p12_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0p01_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0809 | -0.9516 | -0.0031 | -0.0093 | 0.0012 | 0.0035 | 0.0826 | 89.3333 | 11 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p03_byg0p05_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0p01_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0874 | -1.0166 | -0.0033 | -0.0099 | 0.0007 | 0.0020 | 0.0806 | 91.3333 | 10 | 0.0032 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p05_lvg0p12_so0_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0p01_sk0p08_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0989 | -1.0860 | -0.0033 | -0.0098 | 0.0005 | 0.0014 | 0.0644 | 94.0000 | 4 | 0.0031 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p02_byg0p05_lvg0p08_so0_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p015_sap0p01_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.1328 | -0.9728 | -0.0047 | -0.0142 | 0.0007 | 0.0020 | 0.0695 | 88.6667 | 17 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p03_byg0p05_lvg0p08_so0_kpy4_kdy0p5_kpx0_kpvx1_ffp0p015_sap0p01_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.1377 | -0.8871 | -0.0045 | -0.0134 | 0.0010 | 0.0029 | 0.0898 | 84.6667 | 20 | 0.0031 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p2_lo0p03_byg0p05_lvg0p08_so0_kpy4_kdy0p5_kpx0_kpvx0p5_ffp0p015_sap0p01_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.1377 | -0.9652 | -0.0045 | -0.0134 | 0.0001 | 0.0002 | 0.0939 | 88.0000 | 18 | 0.0031 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p03_byg0p05_lvg0p08_som0p02_kpy4_kdy0p5_kpx1_kpvx1_ffp0p015_sap0p01_sk0p08_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.1377 | -1.0432 | -0.0045 | -0.0134 | 0.0002 | 0.0005 | 0.0716 | 90.6667 | 16 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p035_lvg0p08_so0_kpy4_kdy0p5_kpx0_kpvx1_ffp0p005_sap0_sk0p12_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.1377 | -1.0594 | -0.0045 | -0.0134 | 0.0008 | 0.0024 | 0.0695 | 92.0000 | 12 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p03_byg0p035_lvg0p08_so0_kpy4_kdy0p5_kpx1_kpvx1_ffp0p005_sap0p01_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.1377 | -1.0594 | -0.0045 | -0.0134 | 0.0008 | 0.0024 | 0.0695 | 92.0000 | 12 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
