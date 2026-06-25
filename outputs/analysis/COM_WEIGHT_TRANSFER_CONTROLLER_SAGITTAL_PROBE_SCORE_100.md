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
- `double_support_dominates`: `12`
- `too_little_single_support`: `12`
- `single_support_not_balanced`: `7`

### seed_002
- `low_forward_displacement`: `24`
- `low_forward_velocity`: `24`
- `double_support_dominates`: `8`
- `too_little_single_support`: `5`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_so0p02_kpy2_kdy0p2_kpx0_kpvx1_ffp0p03_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.3794 | -0.3792 | 0.0104 | 0.0209 | 0.0104 | 0.0208 | 0.0865 | 78.0000 | 19 | 0.0073 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_so0p02_kpy2_kdy0p2_kpx2_kpvx1_ffp0p02_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.3907 | -0.3848 | 0.0104 | 0.0209 | 0.0100 | 0.0199 | 0.0865 | 77.0000 | 16 | 0.0073 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_so0p02_kpy2_kdy0p2_kpx2_kpvx2_ffp0p02_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.3907 | -0.3848 | 0.0104 | 0.0209 | 0.0100 | 0.0199 | 0.0865 | 77.0000 | 16 | 0.0073 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_so0_kpy2_kdy0p2_kpx1_kpvx1_ffp0p02_sap0_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.4004 | -0.3897 | 0.0104 | 0.0209 | 0.0096 | 0.0192 | 0.0865 | 80.0000 | 16 | 0.0073 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0_kpy2_kdy0p2_kpx2_kpvx2_ffp0p03_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.4100 | -0.4063 | 0.0092 | 0.0184 | 0.0095 | 0.0190 | 0.0582 | 89.0000 | 18 | 0.0069 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p02_kpy2_kdy0p2_kpx1_kpvx2_ffp0p02_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.4100 | -0.4063 | 0.0092 | 0.0184 | 0.0095 | 0.0190 | 0.0582 | 89.0000 | 18 | 0.0069 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p04_kpy2_kdy0p2_kpx2_kpvx1_ffp0p03_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.4100 | -0.4063 | 0.0092 | 0.0184 | 0.0095 | 0.0190 | 0.0582 | 89.0000 | 18 | 0.0069 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p04_kpy2_kdy0p2_kpx2_kpvx2_ffp0p03_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.4599 | -0.4349 | 0.0092 | 0.0184 | 0.0072 | 0.0144 | 0.0600 | 87.0000 | 22 | 0.0060 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_so0_kpy2_kdy0p2_kpx1_kpvx1_ffp0p02_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.4599 | -0.4349 | 0.0092 | 0.0184 | 0.0072 | 0.0144 | 0.0600 | 87.0000 | 22 | 0.0060 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_so0p02_kpy2_kdy0p2_kpx1_kpvx1_ffp0p03_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.4599 | -0.4349 | 0.0092 | 0.0184 | 0.0072 | 0.0144 | 0.0600 | 87.0000 | 22 | 0.0060 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_so0p02_kpy2_kdy0p2_kpx2_kpvx1_ffp0p02_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.4599 | -0.4349 | 0.0092 | 0.0184 | 0.0072 | 0.0144 | 0.0600 | 87.0000 | 22 | 0.0060 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p04_kpy2_kdy0p2_kpx0_kpvx2_ffp0p02_sap0_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.4683 | -0.4391 | 0.0092 | 0.0184 | 0.0077 | 0.0153 | 0.0602 | 91.0000 | 14 | 0.0066 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_so0_kpy1_kdy0p2_kpx0_kpvx1_ffp0p03_sap0_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.5779 | -0.5454 | 0.0083 | 0.0166 | 0.0065 | 0.0130 | 0.0597 | 93.0000 | 12 | 0.0061 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_so0p02_kpy1_kdy0p2_kpx0_kpvx2_ffp0p02_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.5779 | -0.5454 | 0.0083 | 0.0166 | 0.0065 | 0.0130 | 0.0597 | 93.0000 | 12 | 0.0061 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_so0p02_kpy1_kdy0p2_kpx1_kpvx2_ffp0p02_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.5779 | -0.5454 | 0.0083 | 0.0166 | 0.0065 | 0.0130 | 0.0597 | 93.0000 | 12 | 0.0061 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_so0p04_kpy1_kdy0p2_kpx0_kpvx1_ffp0p02_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.5779 | -0.5454 | 0.0083 | 0.0166 | 0.0065 | 0.0130 | 0.0597 | 93.0000 | 12 | 0.0061 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_so0p04_kpy1_kdy0p2_kpx1_kpvx1_ffp0p02_sap0_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.5779 | -0.5454 | 0.0083 | 0.0166 | 0.0065 | 0.0130 | 0.0597 | 93.0000 | 12 | 0.0061 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_so0p04_kpy1_kdy0p2_kpx2_kpvx1_ffp0p02_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.5785 | -0.5610 | 0.0079 | 0.0157 | 0.0025 | 0.0049 | 0.1138 | 88.0000 | 10 | 0.0077 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p04_kpy1_kdy0p2_kpx1_kpvx1_ffp0p03_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.5810 | -0.5623 | 0.0079 | 0.0157 | 0.0024 | 0.0047 | 0.1138 | 88.0000 | 10 | 0.0077 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p04_kpy1_kdy0p2_kpx2_kpvx1_ffp0p03_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.5810 | -0.5623 | 0.0079 | 0.0157 | 0.0024 | 0.0047 | 0.1138 | 88.0000 | 10 | 0.0077 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_so0_kpy1_kdy0p2_kpx2_kpvx1_ffp0p03_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.5810 | -0.5623 | 0.0079 | 0.0157 | 0.0024 | 0.0047 | 0.1138 | 88.0000 | 10 | 0.0077 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0_kpy1_kdy0p2_kpx0_kpvx1_ffp0p02_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.5886 | -0.5661 | 0.0079 | 0.0157 | 0.0021 | 0.0041 | 0.1138 | 89.0000 | 6 | 0.0077 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p04_kpy1_kdy0p2_kpx0_kpvx1_ffp0p02_sap0_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.6070 | -0.5753 | 0.0079 | 0.0157 | 0.0021 | 0.0042 | 0.1138 | 91.0000 | 6 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_so0_kpy1_kdy0p2_kpx2_kpvx1_ffp0p03_sap0_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.6074 | -0.5755 | 0.0079 | 0.0157 | 0.0021 | 0.0042 | 0.1138 | 91.0000 | 6 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
