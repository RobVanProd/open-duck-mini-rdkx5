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
- `double_support_dominates`: `11`
- `too_little_single_support`: `10`
- `single_contact_pattern_dominates`: `9`
- `single_support_not_balanced`: `7`

### seed_002
- `low_forward_displacement`: `16`
- `low_forward_velocity`: `16`
- `double_support_dominates`: `8`
- `too_little_single_support`: `4`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p1_kpy2_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.6529 | -0.6112 | -0.0004 | -0.0012 | 0.0021 | 0.0064 | 0.0804 | 82.0000 | 31 | 0.0049 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.6769 | -0.6285 | -0.0012 | -0.0035 | 0.0018 | 0.0055 | 0.1003 | 83.3333 | 24 | 0.0050 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p08_kpy2_kdy0p2_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.6784 | -0.6100 | -0.0004 | -0.0011 | 0.0030 | 0.0089 | 0.0860 | 85.3333 | 24 | 0.0050 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.6820 | -0.6430 | -0.0013 | -0.0039 | 0.0011 | 0.0033 | 0.0958 | 77.3333 | 34 | 0.0051 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p25_lo0p01_byg0p03_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.6820 | -0.6430 | -0.0013 | -0.0039 | 0.0011 | 0.0033 | 0.0958 | 77.3333 | 34 | 0.0051 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p01_byg0p02_lvg0p1_kpy2_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.6820 | -0.6430 | -0.0013 | -0.0039 | 0.0011 | 0.0033 | 0.0958 | 77.3333 | 34 | 0.0051 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p01_byg0p02_lvg0p08_kpy1_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.8209 | -0.6951 | -0.0007 | -0.0020 | 0.0029 | 0.0088 | 0.0603 | 91.3333 | 14 | 0.0044 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.8227 | -0.6833 | -0.0001 | -0.0003 | 0.0033 | 0.0099 | 0.0793 | 90.6667 | 14 | 0.0044 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p03_byg0p02_lvg0p1_kpy2_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.8378 | -0.6908 | -0.0006 | -0.0017 | 0.0029 | 0.0087 | 0.0641 | 88.6667 | 20 | 0.0045 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p03_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.8378 | -0.7113 | -0.0006 | -0.0017 | 0.0029 | 0.0087 | 0.0642 | 92.0000 | 12 | 0.0045 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p03_byg0p02_lvg0p1_kpy2_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.8854 | -0.7175 | -0.0004 | -0.0011 | 0.0031 | 0.0094 | 0.0736 | 90.6667 | 16 | 0.0044 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p02_byg0p02_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.9048 | -0.7817 | -0.0010 | -0.0030 | 0.0031 | 0.0092 | 0.0751 | 94.0000 | 6 | 0.0044 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.9048 | -0.7951 | -0.0010 | -0.0030 | 0.0031 | 0.0092 | 0.0751 | 94.6667 | 4 | 0.0044 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p02_lvg0p1_kpy1_kdy0p5_kpvx0p5_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.9080 | -0.7758 | -0.0003 | -0.0008 | 0.0027 | 0.0082 | 0.0665 | 93.3333 | 8 | 0.0044 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p1_kpy1_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.9573 | -0.8291 | -0.0005 | -0.0016 | 0.0026 | 0.0078 | 0.0602 | 94.6667 | 4 | 0.0044 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p03_byg0p02_lvg0p08_kpy2_kdy0p2_kpvx0p5_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.0224 | -0.7811 | -0.0001 | -0.0002 | 0.0030 | 0.0091 | 0.0805 | 88.6667 | 18 | 0.0045 | `low_forward_displacement, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
