# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `48`
- mode_count: `24`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `150`

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
- `double_support_dominates`: `5`

### seed_002
- `low_forward_displacement`: `24`
- `low_forward_velocity`: `24`
- `double_support_dominates`: `4`
- `too_little_single_support`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0_kpy2_kdy0p2_kpx2_kpvx2_ffp0p03_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6268 | -0.5599 | 0.0004 | 0.0012 | 0.0045 | 0.0134 | 0.0945 | 81.3333 | 30 | 0.0073 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p02_kpy2_kdy0p2_kpx1_kpvx2_ffp0p02_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6268 | -0.5599 | 0.0004 | 0.0012 | 0.0045 | 0.0134 | 0.0945 | 81.3333 | 30 | 0.0073 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p04_kpy2_kdy0p2_kpx2_kpvx1_ffp0p03_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6268 | -0.5599 | 0.0004 | 0.0012 | 0.0045 | 0.0134 | 0.0945 | 81.3333 | 30 | 0.0073 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p04_kpy2_kdy0p2_kpx2_kpvx2_ffp0p03_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6268 | -0.5750 | 0.0004 | 0.0012 | 0.0035 | 0.0106 | 0.0945 | 82.6667 | 32 | 0.0066 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_so0_kpy2_kdy0p2_kpx1_kpvx1_ffp0p02_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6268 | -0.5750 | 0.0004 | 0.0012 | 0.0035 | 0.0106 | 0.0945 | 82.6667 | 32 | 0.0066 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_so0p02_kpy2_kdy0p2_kpx1_kpvx1_ffp0p03_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6268 | -0.5750 | 0.0004 | 0.0012 | 0.0035 | 0.0106 | 0.0945 | 82.6667 | 32 | 0.0066 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_so0p02_kpy2_kdy0p2_kpx2_kpvx1_ffp0p02_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6268 | -0.5750 | 0.0004 | 0.0012 | 0.0035 | 0.0106 | 0.0945 | 82.6667 | 32 | 0.0066 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p04_kpy2_kdy0p2_kpx0_kpvx2_ffp0p02_sap0_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6268 | -0.5756 | 0.0004 | 0.0012 | 0.0035 | 0.0105 | 0.0945 | 85.3333 | 22 | 0.0071 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_so0p02_kpy2_kdy0p2_kpx0_kpvx1_ffp0p03_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6377 | -0.5789 | 0.0001 | 0.0002 | 0.0036 | 0.0109 | 0.1140 | 75.3333 | 34 | 0.0075 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_so0p02_kpy2_kdy0p2_kpx2_kpvx1_ffp0p02_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6377 | -0.5805 | 0.0001 | 0.0002 | 0.0035 | 0.0106 | 0.1140 | 75.3333 | 30 | 0.0075 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_so0p02_kpy2_kdy0p2_kpx2_kpvx2_ffp0p02_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6377 | -0.5805 | 0.0001 | 0.0002 | 0.0035 | 0.0106 | 0.1140 | 75.3333 | 30 | 0.0075 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_so0_kpy2_kdy0p2_kpx1_kpvx1_ffp0p02_sap0_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6377 | -0.5836 | 0.0001 | 0.0002 | 0.0033 | 0.0100 | 0.1140 | 77.3333 | 30 | 0.0075 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p04_kpy1_kdy0p2_kpx1_kpvx1_ffp0p03_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6538 | -0.6042 | -0.0004 | -0.0013 | 0.0026 | 0.0078 | 0.0800 | 90.0000 | 16 | 0.0062 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p04_kpy1_kdy0p2_kpx2_kpvx1_ffp0p03_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6538 | -0.6042 | -0.0004 | -0.0013 | 0.0026 | 0.0078 | 0.0800 | 90.0000 | 16 | 0.0062 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_so0_kpy1_kdy0p2_kpx2_kpvx1_ffp0p03_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6538 | -0.6042 | -0.0004 | -0.0013 | 0.0026 | 0.0078 | 0.0800 | 90.0000 | 16 | 0.0062 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_so0p04_kpy1_kdy0p2_kpx2_kpvx1_ffp0p02_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6538 | -0.6056 | -0.0004 | -0.0013 | 0.0029 | 0.0087 | 0.0800 | 90.6667 | 12 | 0.0062 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_so0_kpy1_kdy0p2_kpx2_kpvx1_ffp0p03_sap0_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6538 | -0.6186 | -0.0004 | -0.0013 | 0.0029 | 0.0088 | 0.0800 | 92.0000 | 10 | 0.0063 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0_kpy1_kdy0p2_kpx0_kpvx1_ffp0p02_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6538 | -0.6188 | -0.0004 | -0.0013 | 0.0025 | 0.0075 | 0.0800 | 91.3333 | 8 | 0.0064 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p04_kpy1_kdy0p2_kpx0_kpvx1_ffp0p02_sap0_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6538 | -0.6467 | -0.0004 | -0.0013 | 0.0028 | 0.0085 | 0.0800 | 93.3333 | 8 | 0.0063 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_so0_kpy1_kdy0p2_kpx0_kpvx1_ffp0p03_sap0_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6724 | -0.6035 | 0.0002 | 0.0007 | 0.0032 | 0.0096 | 0.0854 | 89.3333 | 18 | 0.0067 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_so0p02_kpy1_kdy0p2_kpx0_kpvx2_ffp0p02_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6724 | -0.6035 | 0.0002 | 0.0007 | 0.0032 | 0.0096 | 0.0854 | 89.3333 | 18 | 0.0067 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_so0p02_kpy1_kdy0p2_kpx1_kpvx2_ffp0p02_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6724 | -0.6035 | 0.0002 | 0.0007 | 0.0032 | 0.0096 | 0.0854 | 89.3333 | 18 | 0.0067 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_so0p04_kpy1_kdy0p2_kpx0_kpvx1_ffp0p02_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6724 | -0.6035 | 0.0002 | 0.0007 | 0.0032 | 0.0096 | 0.0854 | 89.3333 | 18 | 0.0067 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_so0p04_kpy1_kdy0p2_kpx1_kpvx1_ffp0p02_sap0_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6724 | -0.6035 | 0.0002 | 0.0007 | 0.0032 | 0.0096 | 0.0854 | 89.3333 | 18 | 0.0067 | `low_forward_displacement, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
