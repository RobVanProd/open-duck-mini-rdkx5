# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `64`
- mode_count: `32`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `100`

## Criteria

- min_mean_vx: `0.04`
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
- `low_forward_velocity`: `32`
- `high_lateral_velocity`: `26`
- `double_support_dominates`: `5`
- `action_saturation`: `3`
- `single_support_not_balanced`: `2`
- `too_little_single_support`: `2`
- `single_contact_pattern_dominates`: `1`

### seed_002
- `low_forward_velocity`: `32`
- `high_lateral_velocity`: `29`
- `double_support_dominates`: `4`
- `action_saturation`: `3`
- `single_contact_pattern_dominates`: `1`
- `single_support_not_balanced`: `1`
- `too_little_single_support`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| teacher_p0p56_rs0p04_sk0p08_sa0_spg1p5_pd1_lg0p5_byg0p5_plg0p12_clb0 | 0 | seed_000 | -0.3248 | -0.3215 | -0.0006 | 0.0002 | 0.1166 | 90.0000 | 16 | 0.0031 | `low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p08_sam0p02_spg1_pd1_lg1_bygm1_plg0p12_clb0 | 0 | seed_000 | -0.3594 | -0.3356 | -0.0024 | 0.0011 | 0.1202 | 84.0000 | 20 | 0.0034 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0_sk0p08_sam0p02_spg0p5_pd2_lg1_bygm0p5_plg0p08_clb0p5 | 0 | seed_000 | -0.4046 | -0.3543 | -0.0031 | 0.0060 | 0.1223 | 91.0000 | 14 | 0.0042 | `double_support_dominates, high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p04_sk0p08_sam0p02_spg1p5_pd2_lgm1_byg1_plg0p12_clb0 | 0 | seed_002 | -0.4270 | -0.3836 | -0.0000 | 0.0011 | 0.1321 | 91.0000 | 9 | 0.0042 | `double_support_dominates, high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p04_sk0p08_sa0p02_spg1_pd1_lg0_byg0p5_plg0p12_clb0 | 0 | seed_000 | -0.4471 | -0.3784 | -0.0009 | 0.0056 | 0.1171 | 92.0000 | 7 | 0.0054 | `double_support_dominates, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p08_sa0_spg1_pd2_lgm1_byg0_plg0p06_clb1 | 0 | seed_002 | -0.5715 | -0.5613 | 0.0077 | 0.0144 | 0.1676 | 83.0000 | 22 | 0.0096 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p08_sam0p02_spg1_pd2_lg0p5_byg0_plg0p06_clb0 | 0 | seed_000 | -0.5717 | -0.5496 | -0.0015 | 0.0036 | 0.0847 | 96.0000 | 6 | 0.0038 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| teacher_p0p64_rs0_sk0p08_sa0_spg0p5_pd2_lgm1_byg0_plg0p12_clb1 | 0 | seed_000 | -0.7880 | -0.7838 | 0.0057 | 0.0081 | 0.1866 | 83.0000 | 25 | 0.0074 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0_sk0p08_sa0p02_spg1p5_pd1_lg1_bygm0p5_plg0p06_clb1 | 0 | seed_002 | -0.8393 | -0.7995 | 0.0093 | 0.0060 | 0.1917 | 77.0000 | 34 | 0.0072 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p12_sam0p02_spg0p5_pd1_lg0_bygm0p5_plg0p06_clb1 | 0 | seed_000 | -0.8937 | -0.8846 | 0.0109 | 0.0195 | 0.2114 | 76.0000 | 17 | 0.0094 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p04_sk0p08_sam0p02_spg1p5_pd1_lg1_bygm1_plg0p08_clb0p5 | 0 | seed_002 | -0.9398 | -0.7395 | -0.0001 | -0.0002 | 0.1972 | 79.0000 | 27 | 0.0046 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p12_sa0p02_spg1_pd1_lgm0p5_bygm0p5_plg0p12_clb1 | 0 | seed_000 | -0.9408 | -0.8502 | 0.0204 | 0.0252 | 0.2033 | 57.0000 | 28 | 0.0097 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p12_sa0p02_spg1_pd2_lgm1_byg0_plg0p12_clb0p5 | 0 | seed_002 | -0.9542 | -0.9327 | 0.0206 | 0.0192 | 0.2209 | 60.0000 | 24 | 0.0087 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p16_sa0p02_spg1_pd1_lgm0p5_byg1_plg0p08_clb0 | 0 | seed_002 | -1.0005 | -0.9849 | 0.0226 | 0.0245 | 0.2326 | 78.0000 | 15 | 0.0111 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p12_sa0p02_spg0p5_pd2_lg0_byg0p5_plg0p08_clb0 | 0 | seed_000 | -1.0477 | -0.8519 | 0.0148 | 0.0084 | 0.1715 | 83.0000 | 17 | 0.0066 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0_sk0p12_sa0p02_spg0p5_pd2_lg1_byg0p5_plg0p06_clb0 | 0 | seed_000 | -1.1538 | -1.0820 | 0.0067 | 0.0190 | 0.2276 | 60.0000 | 30 | 0.0077 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p04_sk0p16_sam0p02_spg0p5_pd1_lg0_bygm0p5_plg0p08_clb0 | 0 | seed_002 | -1.3630 | -1.1905 | 0.0080 | 0.0105 | 0.2622 | 79.0000 | 14 | 0.0098 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0_sk0p16_sam0p02_spg0p5_pd2_lg1_bygm1_plg0p08_clb0p5 | 0 | seed_002 | -1.4809 | -1.4637 | 0.0235 | 0.0235 | 0.2916 | 66.0000 | 20 | 0.0095 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p16_sam0p02_spg1_pd1_lgm1_bygm0p5_plg0p12_clb1 | 0 | seed_002 | -1.5138 | -1.4315 | 0.0192 | 0.0224 | 0.2542 | 59.0000 | 14 | 0.0096 | `action_saturation, high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p12_sam0p02_spg0p5_pd2_lg0p5_bygm0p5_plg0p06_clb1 | 0 | seed_002 | -1.5726 | -1.4472 | 0.0178 | 0.0113 | 0.2893 | 57.0000 | 37 | 0.0078 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p16_sam0p02_spg0p5_pd2_lgm1_bygm1_plg0p08_clb1 | 0 | seed_002 | -1.5929 | -1.4339 | 0.0162 | 0.0269 | 0.2638 | 62.0000 | 17 | 0.0095 | `action_saturation, high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p16_sa0_spg0p5_pd1_lgm0p5_byg1_plg0p06_clb0 | 0 | seed_000 | -1.6114 | -1.4162 | 0.0261 | 0.0316 | 0.2682 | 61.0000 | 19 | 0.0108 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p12_sa0p02_spg1_pd2_lg0p5_bygm0p5_plg0p06_clb0p5 | 0 | seed_002 | -1.6431 | -1.4890 | 0.0121 | 0.0213 | 0.3093 | 63.0000 | 26 | 0.0116 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p16_sam0p02_spg1p5_pd2_lg0p5_byg1_plg0p12_clb0p5 | 0 | seed_002 | -1.7038 | -1.6181 | 0.0119 | 0.0229 | 0.3188 | 74.0000 | 20 | 0.0107 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p12_sa0p02_spg1_pd1_lg0p5_byg0p5_plg0p12_clb0p5 | 0 | seed_000 | -1.7312 | -1.7083 | 0.0101 | 0.0247 | 0.3184 | 67.0000 | 27 | 0.0120 | `high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
