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
- `single_support_not_balanced`: `32`
- `too_little_single_support`: `32`
- `single_contact_pattern_dominates`: `21`

### seed_002
- `double_support_dominates`: `32`
- `low_forward_displacement`: `32`
- `low_forward_velocity`: `32`
- `single_support_not_balanced`: `32`
- `too_little_single_support`: `32`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p03_byg0p035_lvg0p08_so0_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0p01_sk0p08_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.1257 | -1.0988 | -0.0028 | -0.0085 | 0.0013 | 0.0039 | 0.0702 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p05_lvg0p08_so0_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p015_sap0p01_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.1399 | -1.0684 | -0.0029 | -0.0086 | 0.0011 | 0.0034 | 0.0677 | 93.3333 | 6 | 0.0031 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p03_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p005_sap0p01_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.1550 | -1.1135 | -0.0029 | -0.0088 | 0.0013 | 0.0039 | 0.0702 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p03_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0_sk0p08_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.1670 | -1.1195 | -0.0029 | -0.0087 | 0.0013 | 0.0039 | 0.0702 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p03_byg0p05_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.1757 | -1.1051 | -0.0027 | -0.0082 | 0.0012 | 0.0037 | 0.0660 | 94.0000 | 4 | 0.0031 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p03_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0_sk0p08_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.1782 | -1.1251 | -0.0028 | -0.0085 | 0.0013 | 0.0039 | 0.0702 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p03_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.1818 | -1.1269 | -0.0029 | -0.0088 | 0.0013 | 0.0039 | 0.0702 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p005_sap0p01_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.1897 | -1.1308 | -0.0028 | -0.0083 | 0.0013 | 0.0039 | 0.0702 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p05_lvg0p08_so0_kpy3_kdy0p5_kpx0_kpvx1_ffp0p005_sap0_sk0p08_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.2064 | -1.1018 | -0.0029 | -0.0086 | 0.0011 | 0.0034 | 0.0689 | 93.3333 | 6 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p03_byg0p035_lvg0p12_so0_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0_sk0p12_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.2186 | -1.1453 | -0.0028 | -0.0085 | 0.0013 | 0.0039 | 0.0702 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p03_byg0p035_lvg0p08_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0_sk0p12_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.2229 | -1.1474 | -0.0030 | -0.0089 | 0.0013 | 0.0039 | 0.0702 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p02_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx1_ffp0p005_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.3209 | -1.1949 | -0.0037 | -0.0112 | 0.0014 | 0.0042 | 0.0695 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p02_byg0p05_lvg0p12_so0_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p015_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.3209 | -1.1949 | -0.0037 | -0.0112 | 0.0014 | 0.0042 | 0.0695 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p2_lo0p02_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx1_ffp0p005_sap0p01_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.3209 | -1.1949 | -0.0037 | -0.0112 | 0.0014 | 0.0042 | 0.0695 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p02_byg0p05_lvg0p08_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0_sk0p08_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.3209 | -1.1949 | -0.0037 | -0.0112 | 0.0014 | 0.0042 | 0.0695 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p02_byg0p05_lvg0p08_som0p02_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0p01_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.3209 | -1.1949 | -0.0037 | -0.0112 | 0.0014 | 0.0042 | 0.0695 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p02_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0p01_sk0p08_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.3209 | -1.1949 | -0.0037 | -0.0112 | 0.0014 | 0.0042 | 0.0695 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p02_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.3209 | -1.1949 | -0.0037 | -0.0112 | 0.0014 | 0.0042 | 0.0695 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p02_byg0p05_lvg0p12_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0p01_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.3209 | -1.1949 | -0.0037 | -0.0112 | 0.0014 | 0.0042 | 0.0695 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p02_byg0p05_lvg0p12_so0_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p015_sap0p01_sk0p12_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.3209 | -1.1949 | -0.0037 | -0.0112 | 0.0014 | 0.0042 | 0.0695 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p03_byg0p05_lvg0p12_so0_kpy4_kdy0p5_kpx0_kpvx1_ffp0p015_sap0p01_sk0p08_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.3583 | -1.1092 | -0.0037 | -0.0110 | 0.0008 | 0.0025 | 0.0835 | 90.0000 | 11 | 0.0032 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p03_byg0p05_lvg0p08_so0_kpy4_kdy0p5_kpx0_kpvx1_ffp0p005_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.3583 | -1.1414 | -0.0037 | -0.0110 | 0.0009 | 0.0028 | 0.0739 | 91.3333 | 9 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p03_byg0p05_lvg0p12_so0_kpy4_kdy0p5_kpx1_kpvx1_ffp0p005_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.3583 | -1.1978 | -0.0037 | -0.0110 | 0.0015 | 0.0046 | 0.0806 | 94.0000 | 2 | 0.0031 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p03_byg0p035_lvg0p08_so0_kpy4_kdy0p5_kpx1_kpvx1_ffp0p005_sap0_sk0p08_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.3583 | -1.2136 | -0.0037 | -0.0110 | 0.0014 | 0.0042 | 0.0695 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p03_byg0p035_lvg0p08_som0p02_kpy4_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0p01_sk0p08_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.3583 | -1.2136 | -0.0037 | -0.0110 | 0.0014 | 0.0042 | 0.0695 | 94.6667 | 4 | 0.0030 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
