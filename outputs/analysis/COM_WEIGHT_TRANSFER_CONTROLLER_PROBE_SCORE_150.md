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
- min_forward_displacement_m: `0.06`
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
- `double_support_dominates`: `16`
- `low_forward_displacement`: `16`
- `low_forward_velocity`: `16`
- `single_contact_pattern_dominates`: `16`
- `single_support_not_balanced`: `16`
- `too_little_single_support`: `16`

### seed_002
- `low_forward_displacement`: `16`
- `low_forward_velocity`: `16`
- `double_support_dominates`: `12`
- `high_lateral_velocity`: `8`
- `too_little_single_support`: `8`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx0p5_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.7478 | -1.5555 | -0.0001 | -0.0003 | 0.0030 | 0.0091 | 0.1248 | 90.6667 | 9 | 0.0045 | `double_support_dominates, high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.7478 | -1.5555 | -0.0001 | -0.0003 | 0.0030 | 0.0091 | 0.1248 | 90.6667 | 9 | 0.0045 | `double_support_dominates, high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.7478 | -1.5555 | -0.0001 | -0.0003 | 0.0030 | 0.0091 | 0.1248 | 90.6667 | 9 | 0.0045 | `double_support_dominates, high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.7478 | -1.5555 | -0.0001 | -0.0003 | 0.0030 | 0.0091 | 0.1248 | 90.6667 | 9 | 0.0045 | `double_support_dominates, high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.8848 | -1.6666 | 0.0002 | 0.0007 | 0.0020 | 0.0060 | 0.1164 | 92.6667 | 7 | 0.0044 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.8848 | -1.6694 | 0.0002 | 0.0007 | 0.0019 | 0.0058 | 0.1164 | 92.6667 | 7 | 0.0045 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx0p5_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.8848 | -1.6785 | 0.0002 | 0.0007 | 0.0020 | 0.0061 | 0.1164 | 93.3333 | 7 | 0.0045 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.8848 | -1.6798 | 0.0002 | 0.0007 | 0.0020 | 0.0060 | 0.1164 | 93.3333 | 7 | 0.0045 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx0p5_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.8994 | -1.5968 | 0.0000 | 0.0000 | 0.0045 | 0.0134 | 0.1303 | 89.3333 | 15 | 0.0048 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.8994 | -1.5976 | 0.0000 | 0.0000 | 0.0044 | 0.0133 | 0.1303 | 89.3333 | 15 | 0.0048 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.8994 | -1.5976 | 0.0000 | 0.0000 | 0.0044 | 0.0133 | 0.1303 | 89.3333 | 15 | 0.0048 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.8994 | -1.5988 | 0.0000 | 0.0000 | 0.0044 | 0.0132 | 0.1303 | 89.3333 | 15 | 0.0048 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx0p5_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.9041 | -1.6950 | -0.0001 | -0.0002 | 0.0022 | 0.0067 | 0.0871 | 94.0000 | 4 | 0.0044 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.9041 | -1.6950 | -0.0001 | -0.0002 | 0.0022 | 0.0067 | 0.0871 | 94.0000 | 4 | 0.0044 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.9041 | -1.6950 | -0.0001 | -0.0002 | 0.0022 | 0.0067 | 0.0871 | 94.0000 | 4 | 0.0044 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.9041 | -1.6950 | -0.0001 | -0.0002 | 0.0022 | 0.0067 | 0.0871 | 94.0000 | 4 | 0.0044 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
