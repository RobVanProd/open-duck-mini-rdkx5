# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `32`
- mode_count: `16`
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
- `low_forward_displacement`: `16`
- `low_forward_velocity`: `16`
- `double_support_dominates`: `9`
- `too_little_single_support`: `7`
- `single_contact_pattern_dominates`: `2`
- `single_support_not_balanced`: `2`

### seed_002
- `low_forward_displacement`: `16`
- `low_forward_velocity`: `16`
- `double_support_dominates`: `5`
- `too_little_single_support`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy2_kdy0p2_kpvxm1_ffpm0p02_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_000 | -0.6252 | -0.5840 | 0.0004 | 0.0013 | 0.0029 | 0.0088 | 0.0887 | 77.3333 | 37 | 0.0063 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p2_kpvxm2_ffpm0p02_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6268 | -0.5733 | 0.0004 | 0.0012 | 0.0036 | 0.0109 | 0.0990 | 82.6667 | 30 | 0.0069 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy2_kdy0p2_kpvxm1_ffpm0p02_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6377 | -0.5767 | 0.0001 | 0.0002 | 0.0038 | 0.0113 | 0.1140 | 74.0000 | 32 | 0.0075 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy1_kdy0p2_kpvxm2_ffpm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6538 | -0.5857 | -0.0004 | -0.0013 | 0.0037 | 0.0111 | 0.0967 | 90.0000 | 10 | 0.0074 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy2_kdy0p2_kpvxm2_ffpm0p03_sk0p08_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_000 | -0.6596 | -0.6015 | -0.0006 | -0.0018 | 0.0029 | 0.0088 | 0.0862 | 83.3333 | 30 | 0.0064 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy2_kdy0p2_kpvxm1_ffpm0p03_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_000 | -0.6675 | -0.6094 | -0.0009 | -0.0026 | 0.0027 | 0.0081 | 0.1169 | 76.0000 | 34 | 0.0064 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_kpy1_kdy0p2_kpvxm1_ffpm0p03_sk0p08_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6827 | -0.6134 | -0.0001 | -0.0002 | 0.0029 | 0.0087 | 0.0840 | 89.3333 | 16 | 0.0062 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvxm1_ffpm0p04_sk0p08_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6827 | -0.6134 | -0.0001 | -0.0002 | 0.0029 | 0.0087 | 0.0840 | 89.3333 | 16 | 0.0062 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_kpy2_kdy0p2_kpvxm2_ffpm0p04_sk0p08_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_000 | -0.6905 | -0.6351 | -0.0016 | -0.0047 | 0.0018 | 0.0055 | 0.0996 | 79.3333 | 33 | 0.0062 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvxm2_ffpm0p04_sk0p1_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_000 | -0.7291 | -0.6333 | -0.0007 | -0.0021 | 0.0035 | 0.0105 | 0.0798 | 90.6667 | 14 | 0.0057 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy1_kdy0p2_kpvxm2_ffpm0p02_sk0p1_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_000 | -0.7301 | -0.6225 | 0.0001 | 0.0003 | 0.0038 | 0.0114 | 0.0788 | 89.3333 | 14 | 0.0070 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvxm2_ffpm0p04_sk0p1_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_000 | -0.7301 | -0.6358 | 0.0001 | 0.0003 | 0.0038 | 0.0114 | 0.0788 | 91.3333 | 12 | 0.0068 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy1_kdy0p2_kpvxm2_ffpm0p04_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_000 | -0.7344 | -0.6349 | -0.0004 | -0.0013 | 0.0036 | 0.0107 | 0.0788 | 90.6667 | 12 | 0.0060 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvxm1_ffpm0p02_sk0p08_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_000 | -0.8206 | -0.6852 | -0.0002 | -0.0007 | 0.0027 | 0.0082 | 0.0807 | 89.3333 | 18 | 0.0052 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvxm2_ffpm0p03_sk0p08_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_000 | -0.8585 | -0.7372 | -0.0012 | -0.0036 | 0.0027 | 0.0082 | 0.0781 | 92.6667 | 6 | 0.0055 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvxm1_ffpm0p04_sk0p08_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_000 | -0.8585 | -0.7502 | -0.0012 | -0.0036 | 0.0028 | 0.0083 | 0.0781 | 93.3333 | 6 | 0.0054 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
