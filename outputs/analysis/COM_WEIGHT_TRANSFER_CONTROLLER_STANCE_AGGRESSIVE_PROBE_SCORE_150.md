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
- `double_support_dominates`: `13`
- `too_little_single_support`: `10`
- `single_support_not_balanced`: `6`
- `single_contact_pattern_dominates`: `2`

### seed_002
- `low_forward_displacement`: `24`
- `low_forward_velocity`: `24`
- `double_support_dominates`: `7`
- `too_little_single_support`: `6`
- `high_lateral_velocity`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx2_ffp0p03_sk0p1_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_000 | -0.6207 | -0.5814 | 0.0006 | 0.0018 | 0.0039 | 0.0117 | 0.1238 | 76.0000 | 32 | 0.0077 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p03_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_000 | -0.6252 | -0.5651 | 0.0004 | 0.0013 | 0.0041 | 0.0123 | 0.0860 | 79.3333 | 28 | 0.0067 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p04_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_000 | -0.6252 | -0.5685 | 0.0004 | 0.0013 | 0.0039 | 0.0117 | 0.0903 | 83.3333 | 26 | 0.0065 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p04_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6268 | -0.5695 | 0.0004 | 0.0012 | 0.0039 | 0.0116 | 0.0945 | 82.0000 | 28 | 0.0070 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_kpy2_kdy0p2_kpvx2_ffp0p04_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6377 | -0.5836 | 0.0001 | 0.0002 | 0.0033 | 0.0100 | 0.1140 | 77.3333 | 30 | 0.0075 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p02_byg0p03_lvg0p12_kpy2_kdy0p2_kpvx2_ffp0p03_sk0p1_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6464 | -0.5892 | -0.0002 | -0.0006 | 0.0033 | 0.0098 | 0.0904 | 79.3333 | 27 | 0.0064 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p03_sk0p1_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6466 | -0.6148 | -0.0002 | -0.0006 | 0.0017 | 0.0052 | 0.1059 | 76.6667 | 32 | 0.0060 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx2_ffp0p02_sk0p08_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_000 | -0.6596 | -0.6024 | -0.0006 | -0.0018 | 0.0029 | 0.0086 | 0.0858 | 85.3333 | 27 | 0.0063 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx2_ffp0p04_sk0p08_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_000 | -0.6652 | -0.6013 | -0.0008 | -0.0024 | 0.0031 | 0.0093 | 0.0872 | 86.6667 | 25 | 0.0072 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_kpy2_kdy0p2_kpvx2_ffp0p04_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_000 | -0.6675 | -0.6107 | -0.0009 | -0.0026 | 0.0026 | 0.0078 | 0.1169 | 77.3333 | 30 | 0.0064 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx2_ffp0p04_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_000 | -0.6675 | -0.6111 | -0.0009 | -0.0026 | 0.0026 | 0.0077 | 0.1169 | 77.3333 | 30 | 0.0064 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p02_byg0p03_lvg0p12_kpy2_kdy0p2_kpvx1_ffp0p03_sk0p08_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6694 | -0.6126 | -0.0005 | -0.0015 | 0.0026 | 0.0077 | 0.0834 | 86.0000 | 24 | 0.0056 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx2_ffp0p04_sk0p08_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6827 | -0.6134 | -0.0001 | -0.0002 | 0.0029 | 0.0087 | 0.0840 | 89.3333 | 16 | 0.0062 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx2_ffp0p04_sk0p1_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6835 | -0.6034 | 0.0003 | 0.0009 | 0.0035 | 0.0106 | 0.0822 | 86.6667 | 18 | 0.0059 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx2_ffp0p04_sk0p1_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_000 | -0.7138 | -0.6171 | 0.0006 | 0.0018 | 0.0036 | 0.0109 | 0.0812 | 86.6667 | 24 | 0.0071 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p12_kpy1_kdy0p2_kpvx2_ffp0p03_sk0p08_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_000 | -0.7251 | -0.6687 | -0.0002 | -0.0005 | 0.0029 | 0.0086 | 0.0803 | 92.6667 | 10 | 0.0066 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p04_sk0p08_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_000 | -0.7251 | -0.6687 | -0.0002 | -0.0005 | 0.0029 | 0.0086 | 0.0803 | 92.6667 | 10 | 0.0066 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p02_sk0p08_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_000 | -0.7251 | -0.6687 | -0.0002 | -0.0005 | 0.0029 | 0.0086 | 0.0803 | 92.6667 | 10 | 0.0066 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx2_ffp0p04_sk0p1_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_000 | -0.7301 | -0.6464 | 0.0001 | 0.0003 | 0.0036 | 0.0107 | 0.0788 | 92.0000 | 12 | 0.0068 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p02_sk0p1_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_000 | -0.7301 | -0.6583 | 0.0001 | 0.0003 | 0.0036 | 0.0109 | 0.0788 | 92.6667 | 10 | 0.0068 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p12_kpy1_kdy0p2_kpvx2_ffp0p02_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_000 | -0.7472 | -0.6358 | 0.0004 | 0.0012 | 0.0035 | 0.0105 | 0.0814 | 84.0000 | 22 | 0.0061 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p02_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_000 | -0.7472 | -0.6358 | 0.0004 | 0.0012 | 0.0035 | 0.0105 | 0.0814 | 84.0000 | 22 | 0.0061 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy1_kdy0p2_kpvx1_ffp0p03_sk0p08_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_000 | -0.8585 | -0.7508 | -0.0012 | -0.0036 | 0.0027 | 0.0082 | 0.0781 | 93.3333 | 4 | 0.0048 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p04_sk0p08_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_000 | -0.8585 | -0.7635 | -0.0012 | -0.0036 | 0.0028 | 0.0083 | 0.0781 | 94.0000 | 4 | 0.0049 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
