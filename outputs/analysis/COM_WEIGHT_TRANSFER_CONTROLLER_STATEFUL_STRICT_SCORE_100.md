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
- `single_support_not_balanced`: `32`
- `too_little_single_support`: `32`

### seed_002
- `double_support_dominates`: `32`
- `low_forward_velocity`: `32`
- `too_little_single_support`: `32`
- `single_support_not_balanced`: `28`
- `low_forward_displacement`: `13`
- `high_lateral_velocity`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p05_lvg0p08_so0_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p015_sap0p01_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0090 | -0.9090 | -0.0024 | -0.0048 | 0.0017 | 0.0034 | 0.0943 | 90.0000 | 6 | 0.0074 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p03_byg0p035_lvg0p08_so0_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0p01_sk0p08_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0280 | -0.9763 | -0.0023 | -0.0047 | 0.0019 | 0.0038 | 0.0918 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p03_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p005_sap0p01_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0310 | -0.9777 | -0.0025 | -0.0049 | 0.0019 | 0.0038 | 0.0918 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p03_byg0p05_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0640 | -0.9689 | -0.0022 | -0.0043 | 0.0018 | 0.0036 | 0.1208 | 91.0000 | 4 | 0.0074 | `double_support_dominates, high_lateral_velocity, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p03_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0_sk0p08_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0668 | -0.9956 | -0.0023 | -0.0046 | 0.0019 | 0.0038 | 0.0918 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p03_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0_sk0p08_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0692 | -0.9969 | -0.0024 | -0.0048 | 0.0019 | 0.0038 | 0.0918 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p03_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0718 | -0.9981 | -0.0025 | -0.0050 | 0.0019 | 0.0038 | 0.0918 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p005_sap0p01_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.0848 | -1.0047 | -0.0022 | -0.0044 | 0.0019 | 0.0038 | 0.0918 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p05_lvg0p08_so0_kpy3_kdy0p5_kpx0_kpvx1_ffp0p005_sap0_sk0p08_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.1088 | -0.9590 | -0.0024 | -0.0047 | 0.0017 | 0.0034 | 0.0936 | 90.0000 | 6 | 0.0075 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p03_byg0p035_lvg0p12_so0_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0_sk0p12_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.1275 | -1.0260 | -0.0023 | -0.0046 | 0.0019 | 0.0038 | 0.0918 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p03_byg0p035_lvg0p08_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0_sk0p12_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.1323 | -1.0284 | -0.0025 | -0.0050 | 0.0019 | 0.0038 | 0.0918 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p02_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx1_ffp0p005_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.2106 | -1.0661 | -0.0058 | -0.0115 | 0.0020 | 0.0041 | 0.0950 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p02_byg0p05_lvg0p12_so0_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p015_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.2106 | -1.0661 | -0.0058 | -0.0115 | 0.0020 | 0.0041 | 0.0950 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p2_lo0p02_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx1_ffp0p005_sap0p01_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.2106 | -1.0661 | -0.0058 | -0.0115 | 0.0020 | 0.0041 | 0.0950 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p02_byg0p05_lvg0p08_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0_sk0p08_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.2106 | -1.0661 | -0.0058 | -0.0115 | 0.0020 | 0.0041 | 0.0950 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p02_byg0p05_lvg0p08_som0p02_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0p01_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.2106 | -1.0661 | -0.0058 | -0.0115 | 0.0020 | 0.0041 | 0.0950 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p02_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0p01_sk0p08_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.2106 | -1.0661 | -0.0058 | -0.0115 | 0.0020 | 0.0041 | 0.0950 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p02_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.2106 | -1.0661 | -0.0058 | -0.0115 | 0.0020 | 0.0041 | 0.0950 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p02_byg0p05_lvg0p12_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0p01_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.2106 | -1.0661 | -0.0058 | -0.0115 | 0.0020 | 0.0041 | 0.0950 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p02_byg0p05_lvg0p12_so0_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p015_sap0p01_sk0p12_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.2106 | -1.0661 | -0.0058 | -0.0115 | 0.0020 | 0.0041 | 0.0950 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p03_byg0p05_lvg0p12_so0_kpy4_kdy0p5_kpx0_kpvx1_ffp0p015_sap0p01_sk0p08_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.2477 | -0.9341 | -0.0057 | -0.0113 | 0.0013 | 0.0025 | 0.0950 | 85.0000 | 11 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p03_byg0p05_lvg0p08_so0_kpy4_kdy0p5_kpx0_kpvx1_ffp0p005_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.2477 | -0.9728 | -0.0057 | -0.0113 | 0.0014 | 0.0027 | 0.1072 | 87.0000 | 9 | 0.0075 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p03_byg0p05_lvg0p12_so0_kpy4_kdy0p5_kpx1_kpvx1_ffp0p005_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.2477 | -1.0707 | -0.0057 | -0.0113 | 0.0023 | 0.0047 | 0.1218 | 91.0000 | 2 | 0.0083 | `double_support_dominates, high_lateral_velocity, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p03_byg0p035_lvg0p08_so0_kpy4_kdy0p5_kpx1_kpvx1_ffp0p005_sap0_sk0p08_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.2477 | -1.0847 | -0.0057 | -0.0113 | 0.0020 | 0.0041 | 0.0950 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p03_byg0p035_lvg0p08_som0p02_kpy4_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0p01_sk0p08_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 0 | seed_000 | -1.2477 | -1.0847 | -0.0057 | -0.0113 | 0.0020 | 0.0041 | 0.0950 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
