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
- `double_support_dominates`: `10`
- `too_little_single_support`: `10`
- `single_support_not_balanced`: `5`
- `single_contact_pattern_dominates`: `3`

### seed_002
- `low_forward_displacement`: `16`
- `low_forward_velocity`: `16`
- `double_support_dominates`: `3`
- `too_little_single_support`: `3`
- `single_support_not_balanced`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy2_kdy0p2_kpvxm1_ffpm0p02_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.3790 | -0.3732 | 0.0104 | 0.0209 | 0.0109 | 0.0218 | 0.0865 | 76.0000 | 16 | 0.0073 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p2_kpvxm2_ffpm0p02_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.4119 | -0.4109 | 0.0092 | 0.0184 | 0.0091 | 0.0182 | 0.0602 | 88.0000 | 20 | 0.0066 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy2_kdy0p2_kpvxm1_ffpm0p02_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_002 | -0.4373 | -0.4284 | 0.0088 | 0.0176 | 0.0081 | 0.0162 | 0.0585 | 80.0000 | 24 | 0.0059 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy2_kdy0p2_kpvxm1_ffpm0p03_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_002 | -0.4523 | -0.4367 | 0.0088 | 0.0175 | 0.0075 | 0.0150 | 0.0849 | 81.0000 | 21 | 0.0060 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy2_kdy0p2_kpvxm2_ffpm0p03_sk0p08_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_000 | -0.4599 | -0.4435 | 0.0072 | 0.0144 | 0.0085 | 0.0170 | 0.0484 | 89.0000 | 14 | 0.0054 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_kpy2_kdy0p2_kpvxm2_ffpm0p04_sk0p08_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_002 | -0.4732 | -0.4614 | 0.0076 | 0.0152 | 0.0067 | 0.0133 | 0.0626 | 84.0000 | 17 | 0.0055 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy1_kdy0p2_kpvxm2_ffpm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_002 | -0.6012 | -0.5724 | 0.0079 | 0.0157 | 0.0016 | 0.0031 | 0.1138 | 86.0000 | 8 | 0.0077 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_kpy1_kdy0p2_kpvxm1_ffpm0p03_sk0p08_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6111 | -0.5709 | 0.0076 | 0.0151 | 0.0076 | 0.0151 | 0.0568 | 93.0000 | 12 | 0.0059 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvxm1_ffpm0p04_sk0p08_sa0_shr0p1_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6111 | -0.5709 | 0.0076 | 0.0151 | 0.0076 | 0.0151 | 0.0568 | 93.0000 | 12 | 0.0059 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvxm2_ffpm0p04_sk0p1_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6316 | -0.6072 | 0.0067 | 0.0135 | 0.0023 | 0.0046 | 0.0980 | 88.0000 | 12 | 0.0077 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvxm1_ffpm0p02_sk0p08_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_000 | -0.6580 | -0.6262 | 0.0065 | 0.0130 | 0.0018 | 0.0036 | 0.1127 | 86.0000 | 14 | 0.0084 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy1_kdy0p2_kpvxm2_ffpm0p04_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 0 | seed_000 | -0.7088 | -0.6486 | 0.0076 | 0.0153 | 0.0021 | 0.0041 | 0.0979 | 87.0000 | 10 | 0.0077 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy1_kdy0p2_kpvxm2_ffpm0p02_sk0p1_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_000 | -0.7090 | -0.6251 | 0.0092 | 0.0185 | 0.0096 | 0.0191 | 0.0592 | 94.0000 | 8 | 0.0067 | `double_support_dominates, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvxm2_ffpm0p04_sk0p1_sa0_shr0p1_srs0p5_pt0_pd1 | 0 | seed_000 | -0.7090 | -0.6506 | 0.0092 | 0.0185 | 0.0019 | 0.0038 | 0.1037 | 89.0000 | 10 | 0.0077 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvxm1_ffpm0p04_sk0p08_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_000 | -0.8162 | -0.7084 | -0.0040 | -0.0080 | 0.0016 | 0.0032 | 0.0987 | 90.0000 | 6 | 0.0077 | `low_forward_displacement, low_forward_velocity` |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvxm2_ffpm0p03_sk0p08_sa0_shr0p08_srs0p3_pt0_pd1 | 0 | seed_000 | -0.8162 | -0.7115 | -0.0040 | -0.0080 | 0.0013 | 0.0027 | 0.0987 | 89.0000 | 6 | 0.0077 | `low_forward_displacement, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
