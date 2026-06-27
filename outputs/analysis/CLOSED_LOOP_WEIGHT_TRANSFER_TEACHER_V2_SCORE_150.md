# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `64`
- mode_count: `32`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `150`

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
- `high_lateral_velocity`: `31`
- `single_support_not_balanced`: `4`
- `action_saturation`: `3`
- `double_support_dominates`: `3`
- `too_little_single_support`: `3`

### seed_002
- `low_forward_velocity`: `32`
- `high_lateral_velocity`: `31`
- `action_saturation`: `3`
- `double_support_dominates`: `3`
- `too_little_single_support`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| teacher_p0p64_rs0p04_sk0p08_sam0p02_spg1p5_pd2_lgm1_byg1_plg0p12_clb0 | 0 | seed_000 | -0.4502 | -0.4403 | 0.0003 | 0.0011 | 0.1039 | 94.0000 | 9 | 0.0037 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| teacher_p0p64_rs0p04_sk0p08_sa0p02_spg1_pd1_lg0_byg0p5_plg0p12_clb0 | 0 | seed_000 | -0.5024 | -0.4332 | 0.0013 | 0.0044 | 0.1254 | 92.0000 | 9 | 0.0059 | `double_support_dominates, high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p08_sa0_spg1_pd2_lgm1_byg0_plg0p06_clb1 | 0 | seed_002 | -0.6471 | -0.6237 | 0.0075 | 0.0099 | 0.1720 | 79.3333 | 34 | 0.0096 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p08_sam0p02_spg1_pd2_lg0p5_byg0_plg0p06_clb0 | 0 | seed_000 | -0.7922 | -0.6487 | -0.0008 | 0.0023 | 0.1341 | 93.3333 | 11 | 0.0040 | `double_support_dominates, high_lateral_velocity, low_forward_velocity, too_little_single_support` |
| teacher_p0p64_rs0_sk0p08_sam0p02_spg0p5_pd2_lg1_bygm0p5_plg0p08_clb0p5 | 0 | seed_000 | -0.8454 | -0.6265 | -0.0014 | 0.0047 | 0.1362 | 85.3333 | 26 | 0.0049 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0_sk0p08_sa0_spg0p5_pd2_lgm1_byg0_plg0p12_clb1 | 0 | seed_000 | -0.8495 | -0.8466 | 0.0044 | 0.0052 | 0.1912 | 78.6667 | 38 | 0.0076 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p12_sa0p02_spg1_pd1_lgm0p5_bygm0p5_plg0p12_clb1 | 0 | seed_000 | -1.0130 | -0.9556 | 0.0224 | 0.0198 | 0.2145 | 51.3333 | 38 | 0.0099 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p12_sam0p02_spg0p5_pd1_lg0_bygm0p5_plg0p06_clb1 | 0 | seed_000 | -1.0706 | -1.0090 | 0.0160 | 0.0176 | 0.2182 | 73.3333 | 31 | 0.0097 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0_sk0p08_sa0p02_spg1p5_pd1_lg1_bygm0p5_plg0p06_clb1 | 0 | seed_000 | -1.1003 | -0.9796 | 0.0099 | 0.0129 | 0.2019 | 68.6667 | 51 | 0.0099 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p08_sa0_spg1p5_pd1_lg0p5_byg0p5_plg0p12_clb0 | 0 | seed_000 | -1.1376 | -0.8559 | 0.0006 | 0.0030 | 0.1552 | 81.3333 | 28 | 0.0060 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p08_sam0p02_spg1_pd1_lg1_bygm1_plg0p12_clb0 | 0 | seed_000 | -1.1384 | -0.8140 | -0.0005 | 0.0035 | 0.1451 | 77.3333 | 35 | 0.0066 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p12_sa0p02_spg1_pd2_lgm1_byg0_plg0p12_clb0p5 | 0 | seed_002 | -1.1486 | -1.1279 | 0.0219 | 0.0217 | 0.2479 | 54.6667 | 40 | 0.0099 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p12_sa0p02_spg0p5_pd2_lg0_byg0p5_plg0p08_clb0 | 0 | seed_000 | -1.1638 | -0.9769 | 0.0147 | 0.0131 | 0.1935 | 76.6667 | 29 | 0.0080 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p16_sa0p02_spg1_pd1_lgm0p5_byg1_plg0p08_clb0 | 0 | seed_000 | -1.1754 | -1.1248 | 0.0184 | 0.0209 | 0.2378 | 70.6667 | 26 | 0.0114 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p04_sk0p08_sam0p02_spg1p5_pd1_lg1_bygm1_plg0p08_clb0p5 | 0 | seed_000 | -1.1898 | -1.0774 | 0.0004 | 0.0034 | 0.2044 | 74.0000 | 39 | 0.0062 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0_sk0p12_sa0p02_spg0p5_pd2_lg1_byg0p5_plg0p06_clb0 | 0 | seed_000 | -1.2408 | -1.1455 | 0.0071 | 0.0134 | 0.2264 | 64.0000 | 42 | 0.0072 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p12_sam0p02_spg0p5_pd2_lg0p5_bygm0p5_plg0p06_clb1 | 0 | seed_002 | -1.5875 | -1.5792 | 0.0196 | 0.0179 | 0.2986 | 55.3333 | 53 | 0.0081 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0_sk0p16_sam0p02_spg0p5_pd2_lg1_bygm1_plg0p08_clb0p5 | 0 | seed_002 | -1.5939 | -1.5506 | 0.0232 | 0.0220 | 0.3040 | 66.0000 | 33 | 0.0093 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p04_sk0p16_sam0p02_spg0p5_pd1_lg0_bygm0p5_plg0p08_clb0 | 0 | seed_002 | -1.5971 | -1.5418 | 0.0103 | 0.0157 | 0.2973 | 72.0000 | 26 | 0.0098 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p16_sam0p02_spg1_pd1_lgm1_bygm0p5_plg0p12_clb1 | 0 | seed_002 | -1.7053 | -1.5503 | 0.0196 | 0.0242 | 0.2787 | 57.3333 | 27 | 0.0099 | `action_saturation, high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p12_sa0p02_spg1_pd2_lg0p5_bygm0p5_plg0p06_clb0p5 | 0 | seed_002 | -1.7209 | -1.5468 | 0.0089 | 0.0140 | 0.3109 | 68.0000 | 32 | 0.0111 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p16_sa0_spg0p5_pd1_lgm0p5_byg1_plg0p06_clb0 | 0 | seed_000 | -1.7229 | -1.4978 | 0.0250 | 0.0299 | 0.2727 | 56.6667 | 31 | 0.0110 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p16_sam0p02_spg0p5_pd2_lgm1_bygm1_plg0p08_clb1 | 0 | seed_002 | -1.7843 | -1.5592 | 0.0161 | 0.0237 | 0.2869 | 56.0000 | 33 | 0.0097 | `action_saturation, high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p02_sk0p12_sa0p02_spg1_pd1_lg0p5_byg0p5_plg0p12_clb0p5 | 0 | seed_000 | -1.8185 | -1.7890 | 0.0082 | 0.0193 | 0.3216 | 65.3333 | 42 | 0.0112 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p16_sam0p02_spg1p5_pd2_lg0p5_byg1_plg0p12_clb0p5 | 0 | seed_000 | -1.9059 | -1.8389 | 0.0078 | 0.0158 | 0.3193 | 73.3333 | 31 | 0.0100 | `high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
