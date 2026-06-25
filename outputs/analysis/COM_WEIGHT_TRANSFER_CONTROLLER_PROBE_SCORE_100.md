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
- `double_support_dominates`: `16`
- `low_forward_displacement`: `16`
- `low_forward_velocity`: `16`
- `single_contact_pattern_dominates`: `16`
- `single_support_not_balanced`: `16`
- `too_few_contact_transitions`: `16`
- `too_little_single_support`: `16`

### seed_002
- `low_forward_displacement`: `16`
- `low_forward_velocity`: `16`
- `double_support_dominates`: `12`
- `single_support_not_balanced`: `8`
- `too_little_single_support`: `4`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx0p5_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.2381 | -1.0371 | 0.0037 | 0.0074 | 0.0066 | 0.0132 | 0.0937 | 92.0000 | 5 | 0.0043 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.2381 | -1.0371 | 0.0037 | 0.0074 | 0.0066 | 0.0132 | 0.0937 | 92.0000 | 5 | 0.0043 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.2381 | -1.0371 | 0.0037 | 0.0074 | 0.0066 | 0.0132 | 0.0937 | 92.0000 | 5 | 0.0043 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.2381 | -1.0371 | 0.0037 | 0.0074 | 0.0066 | 0.0132 | 0.0937 | 92.0000 | 5 | 0.0043 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.4304 | -1.2237 | 0.0051 | 0.0102 | 0.0054 | 0.0107 | 0.0772 | 94.0000 | 3 | 0.0042 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.4304 | -1.2272 | 0.0051 | 0.0102 | 0.0052 | 0.0105 | 0.0767 | 94.0000 | 3 | 0.0043 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.4304 | -1.2467 | 0.0051 | 0.0102 | 0.0052 | 0.0105 | 0.0767 | 95.0000 | 3 | 0.0043 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx0p5_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.4304 | -1.2473 | 0.0051 | 0.0102 | 0.0052 | 0.0104 | 0.0767 | 95.0000 | 3 | 0.0043 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx0p5_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.4586 | -1.1084 | 0.0045 | 0.0090 | 0.0078 | 0.0156 | 0.0955 | 90.0000 | 11 | 0.0045 | `low_forward_displacement, low_forward_velocity, single_support_not_balanced` |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.4586 | -1.1102 | 0.0045 | 0.0090 | 0.0077 | 0.0154 | 0.0955 | 90.0000 | 11 | 0.0045 | `low_forward_displacement, low_forward_velocity, single_support_not_balanced` |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.4586 | -1.1108 | 0.0045 | 0.0090 | 0.0077 | 0.0154 | 0.0955 | 90.0000 | 11 | 0.0045 | `low_forward_displacement, low_forward_velocity, single_support_not_balanced` |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.4586 | -1.1108 | 0.0045 | 0.0090 | 0.0077 | 0.0154 | 0.0955 | 90.0000 | 11 | 0.0045 | `low_forward_displacement, low_forward_velocity, single_support_not_balanced` |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx0p5_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.4610 | -1.2586 | 0.0045 | 0.0089 | 0.0017 | 0.0034 | 0.1162 | 91.0000 | 4 | 0.0055 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.4610 | -1.2586 | 0.0045 | 0.0089 | 0.0017 | 0.0034 | 0.1162 | 91.0000 | 4 | 0.0055 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.4610 | -1.2586 | 0.0045 | 0.0089 | 0.0017 | 0.0034 | 0.1162 | 91.0000 | 4 | 0.0055 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.4610 | -1.2586 | 0.0045 | 0.0089 | 0.0017 | 0.0034 | 0.1162 | 91.0000 | 4 | 0.0055 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
