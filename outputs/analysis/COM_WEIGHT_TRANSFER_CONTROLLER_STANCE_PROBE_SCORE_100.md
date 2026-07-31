# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `32`
- mode_count: `16`
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
- `low_forward_displacement`: `16`
- `low_forward_velocity`: `16`
- `double_support_dominates`: `11`
- `too_little_single_support`: `10`
- `single_support_not_balanced`: `5`
- `high_lateral_velocity`: `4`
- `single_contact_pattern_dominates`: `2`
- `too_few_contact_transitions`: `1`

### seed_002
- `low_forward_displacement`: `16`
- `low_forward_velocity`: `16`
- `double_support_dominates`: `6`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p1_kpy2_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_002 | -0.4784 | -0.4684 | 0.0073 | 0.0145 | 0.0065 | 0.0129 | 0.0585 | 87.0000 | 18 | 0.0042 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_002 | -0.4858 | -0.4748 | 0.0070 | 0.0141 | 0.0062 | 0.0123 | 0.0818 | 90.0000 | 14 | 0.0044 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_002 | -0.5070 | -0.4829 | 0.0073 | 0.0145 | 0.0053 | 0.0106 | 0.0816 | 85.0000 | 17 | 0.0045 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p25_lo0p01_byg0p03_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_002 | -0.5070 | -0.4829 | 0.0073 | 0.0145 | 0.0053 | 0.0106 | 0.0816 | 85.0000 | 17 | 0.0045 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p01_byg0p02_lvg0p1_kpy2_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_002 | -0.5070 | -0.4829 | 0.0073 | 0.0145 | 0.0053 | 0.0106 | 0.0816 | 85.0000 | 17 | 0.0045 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p08_kpy2_kdy0p2_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.5416 | -0.5219 | 0.0055 | 0.0111 | 0.0071 | 0.0142 | 0.0550 | 92.0000 | 12 | 0.0041 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.7005 | -0.6383 | 0.0072 | 0.0144 | 0.0026 | 0.0051 | 0.0974 | 87.0000 | 12 | 0.0084 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p03_byg0p02_lvg0p1_kpy2_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.8002 | -0.6660 | -0.0032 | -0.0063 | 0.0059 | 0.0119 | 0.0532 | 92.0000 | 13 | 0.0040 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p03_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.8002 | -0.6970 | -0.0032 | -0.0063 | 0.0018 | 0.0037 | 0.1027 | 90.0000 | 8 | 0.0070 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p01_byg0p02_lvg0p08_kpy1_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.8269 | -0.7071 | -0.0034 | -0.0068 | 0.0021 | 0.0042 | 0.0790 | 87.0000 | 13 | 0.0059 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p03_byg0p02_lvg0p1_kpy2_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.8361 | -0.7077 | -0.0030 | -0.0060 | 0.0024 | 0.0049 | 0.1080 | 89.0000 | 10 | 0.0070 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p02_byg0p02_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.8507 | -0.7263 | -0.0038 | -0.0076 | 0.0023 | 0.0046 | 0.0973 | 91.0000 | 6 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.8507 | -0.7364 | -0.0038 | -0.0076 | 0.0023 | 0.0046 | 0.0973 | 92.0000 | 4 | 0.0077 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p02_lvg0p1_kpy1_kdy0p5_kpvx0p5_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.8580 | -0.7362 | -0.0024 | -0.0048 | 0.0018 | 0.0037 | 0.0921 | 91.0000 | 6 | 0.0079 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p1_kpy1_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -0.9088 | -0.7732 | -0.0029 | -0.0057 | 0.0017 | 0.0034 | 0.0777 | 92.0000 | 4 | 0.0079 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p03_byg0p02_lvg0p08_kpy2_kdy0p2_kpvx0p5_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.0192 | -0.8037 | 0.0072 | 0.0145 | 0.0021 | 0.0041 | 0.1003 | 86.0000 | 12 | 0.0076 | `low_forward_displacement, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
