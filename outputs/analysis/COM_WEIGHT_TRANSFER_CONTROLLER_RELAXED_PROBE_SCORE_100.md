# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `24`
- mode_count: `12`
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
- `double_support_dominates`: `12`
- `low_forward_displacement`: `12`
- `low_forward_velocity`: `12`
- `too_little_single_support`: `12`
- `single_support_not_balanced`: `11`
- `single_contact_pattern_dominates`: `8`
- `high_lateral_velocity`: `4`
- `too_few_contact_transitions`: `3`

### seed_002
- `low_forward_displacement`: `12`
- `low_forward_velocity`: `12`
- `double_support_dominates`: `8`
- `single_support_not_balanced`: `8`
- `too_little_single_support`: `7`
- `too_few_contact_transitions`: `2`
- `high_lateral_velocity`: `1`
- `single_contact_pattern_dominates`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy2_kdy0p5_kpvx1_ffp0p02_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.1642 | -1.0740 | 0.0044 | 0.0088 | 0.0060 | 0.0121 | 0.0768 | 94.0000 | 2 | 0.0043 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_few_contact_transitions, too_little_single_support` |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p04_lvg0p12_kpy2_kdy0p5_kpvx1_ffp0p02_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.1642 | -1.0740 | 0.0044 | 0.0088 | 0.0060 | 0.0121 | 0.0768 | 94.0000 | 2 | 0.0043 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_few_contact_transitions, too_little_single_support` |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.1723 | -1.1210 | 0.0036 | 0.0073 | 0.0014 | 0.0029 | 0.1164 | 91.0000 | 4 | 0.0061 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p3_uf0p2_lo0p03_byg0p04_lvg0p12_kpy2_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.2114 | -0.9524 | 0.0036 | 0.0073 | 0.0095 | 0.0190 | 0.1105 | 85.0000 | 17 | 0.0046 | `low_forward_displacement, low_forward_velocity, single_support_not_balanced` |
| com_p0p56_lf0p3_uf0p2_lo0p03_byg0p03_lvg0p12_kpy2_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.2167 | -0.9786 | 0.0035 | 0.0070 | 0.0095 | 0.0189 | 0.1305 | 85.0000 | 17 | 0.0051 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.2201 | -1.0710 | 0.0041 | 0.0082 | 0.0061 | 0.0122 | 0.0732 | 93.0000 | 4 | 0.0043 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_p0p56_lf0p3_uf0p2_lo0p03_byg0p03_lvg0p12_kpy1_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.2582 | -1.2106 | 0.0034 | 0.0069 | 0.0057 | 0.0113 | 0.0791 | 97.0000 | 3 | 0.0043 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| com_p0p56_lf0p3_uf0p2_lo0p03_byg0p04_lvg0p12_kpy2_kdy0p2_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.2700 | -1.0063 | 0.0043 | 0.0086 | 0.0077 | 0.0154 | 0.0981 | 87.0000 | 15 | 0.0048 | `low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p3_uf0p2_lo0p03_byg0p04_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.2700 | -1.0063 | 0.0043 | 0.0086 | 0.0077 | 0.0154 | 0.0981 | 87.0000 | 15 | 0.0048 | `low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p04_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.2956 | -1.0778 | 0.0042 | 0.0083 | 0.0086 | 0.0171 | 0.0839 | 94.0000 | 3 | 0.0043 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy2_kdy0p2_kpvx1_ffp0p02_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.2956 | -1.0883 | 0.0042 | 0.0083 | 0.0090 | 0.0179 | 0.0970 | 95.0000 | 3 | 0.0043 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p04_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p02_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.2956 | -1.0883 | 0.0042 | 0.0083 | 0.0090 | 0.0179 | 0.0970 | 95.0000 | 3 | 0.0043 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
