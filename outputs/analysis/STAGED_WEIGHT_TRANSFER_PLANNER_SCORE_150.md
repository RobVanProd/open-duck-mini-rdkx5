# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `60`
- mode_count: `30`
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
- `low_forward_velocity`: `30`
- `double_support_dominates`: `20`
- `single_support_not_balanced`: `18`
- `too_little_single_support`: `15`
- `high_lateral_velocity`: `14`
- `single_contact_pattern_dominates`: `8`

### seed_002
- `low_forward_velocity`: `30`
- `high_lateral_velocity`: `17`
- `double_support_dominates`: `10`
- `too_little_single_support`: `10`
- `high_sent_target_velocity`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| planner_p0p64_bf0p25_rs0p06_lg0p1_byg0p06_pg0p18_sk0p08_sa0p02_shr0p03_srs0p5_spg0p5_pt0p03_pd2_lfgm1_bygfm0p5 | 0 | seed_000 | -0.3236 | -0.3198 | -0.0004 | 0.0004 | 0.1069 | 82.6667 | 33 | 0.0053 | `low_forward_velocity` |
| planner_p0p56_bf0p25_rs0p06_lg0p1_byg0p02_pg0p24_sk0p08_sa0_shr0p09_srs1_spg0p5_ptm0p03_pd2_lfgm1_bygf0p5 | 0 | seed_000 | -0.3236 | -0.3142 | -0.0005 | 0.0017 | 0.1030 | 85.3333 | 29 | 0.0058 | `low_forward_velocity` |
| planner_p0p64_bf0p55_rs0p02_lg0p08_byg0p02_pg0p24_sk0p12_sam0p02_shr0p09_srs1_spg0p5_pt0_pd1_lfg1_bygf0 | 0 | seed_000 | -0.3912 | -0.3575 | -0.0022 | -0.0005 | 0.1168 | 86.0000 | 21 | 0.0039 | `low_forward_velocity` |
| planner_p0p64_bf0p4_rs0p04_lg0p08_byg0p02_pg0p18_sk0p12_sa0p02_shr0p03_srs1_spg0p5_pt0p03_pd2_lfgm0p5_bygfm0p5 | 0 | seed_002 | -0.4142 | -0.4047 | -0.0011 | 0.0029 | 0.0920 | 94.0000 | 8 | 0.0055 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| planner_p0p72_bf0p55_rs0p04_lg0p06_byg0p02_pg0p24_sk0p08_sa0_shr0p03_srs0p5_spg0p5_pt0_pd1_lfgm1_bygfm0p5 | 0 | seed_002 | -0.4264 | -0.4032 | -0.0025 | 0.0015 | 0.0876 | 94.0000 | 8 | 0.0045 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| planner_p0p56_bf0p55_rs0p06_lg0p1_byg0p06_pg0p12_sk0p16_sa0p02_shr0p09_srs0p5_spg1p5_pt0_pd1_lfgm1_bygf0p5 | 0 | seed_002 | -0.4337 | -0.3862 | -0.0023 | 0.0012 | 0.1305 | 81.3333 | 39 | 0.0071 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| planner_p0p72_bf0p55_rs0p02_lg0p08_byg0p04_pg0p18_sk0p12_sam0p02_shr0p06_srs1_spg1p5_pt0p03_pd2_lfgm1_bygf1 | 0 | seed_000 | -0.4794 | -0.4453 | -0.0016 | 0.0032 | 0.0826 | 94.0000 | 8 | 0.0044 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| planner_p0p56_bf0p25_rs0p02_lg0p08_byg0p02_pg0p18_sk0p12_sa0p02_shr0p03_srs1_spg1p5_ptm0p03_pd2_lfg1_bygf0p5 | 0 | seed_000 | -0.4927 | -0.4213 | -0.0016 | 0.0004 | 0.1242 | 86.0000 | 27 | 0.0044 | `high_lateral_velocity, low_forward_velocity` |
| planner_p0p64_bf0p4_rs0p02_lg0p06_byg0p06_pg0p24_sk0p16_sa0_shr0p03_srs0p5_spg1_pt0_pd1_lfg1_bygf0p5 | 0 | seed_000 | -0.4997 | -0.4474 | -0.0008 | 0.0033 | 0.1330 | 79.3333 | 32 | 0.0058 | `high_lateral_velocity, low_forward_velocity` |
| planner_p0p56_bf0p4_rs0p02_lg0p08_byg0p06_pg0p12_sk0p08_sam0p02_shr0p06_srs0p5_spg1_pt0_pd1_lfgm1_bygf0 | 0 | seed_000 | -0.5024 | -0.4393 | -0.0011 | 0.0012 | 0.0942 | 92.6667 | 7 | 0.0040 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| planner_p0p72_bf0p25_rs0p02_lg0p08_byg0p06_pg0p24_sk0p12_sa0p02_shr0p09_srs0p5_spg1p5_ptm0p03_pd1_lfg0p5_bygf0p5 | 0 | seed_000 | -0.5404 | -0.4364 | -0.0017 | 0.0009 | 0.1226 | 88.0000 | 19 | 0.0065 | `high_lateral_velocity, low_forward_velocity` |
| planner_p0p72_bf0p55_rs0p02_lg0p1_byg0p06_pg0p24_sk0p16_sam0p02_shr0p09_srs0p5_spg1p5_pt0_pd1_lfgm1_bygf0p5 | 0 | seed_000 | -0.5453 | -0.4881 | -0.0007 | 0.0010 | 0.1101 | 94.0000 | 8 | 0.0065 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| planner_p0p64_bf0p4_rs0p04_lg0p06_byg0p04_pg0p18_sk0p16_sa0_shr0p03_srs0p5_spg1p5_pt0_pd1_lfg0p5_bygfm0p5 | 0 | seed_000 | -0.5470 | -0.5359 | -0.0019 | 0.0027 | 0.1486 | 85.3333 | 22 | 0.0060 | `high_lateral_velocity, low_forward_velocity` |
| planner_p0p64_bf0p4_rs0p04_lg0p1_byg0p06_pg0p24_sk0p16_sa0_shr0p06_srs1_spg1_ptm0p03_pd2_lfgm1_bygf1 | 0 | seed_000 | -0.5864 | -0.4953 | -0.0008 | 0.0010 | 0.1068 | 93.3333 | 11 | 0.0058 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| planner_p0p64_bf0p25_rs0p02_lg0p08_byg0p02_pg0p24_sk0p12_sa0p02_shr0p09_srs1_spg0p5_pt0p03_pd1_lfgm1_bygf0p5 | 0 | seed_000 | -0.5875 | -0.5017 | -0.0009 | -0.0003 | 0.1033 | 93.3333 | 8 | 0.0065 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| planner_p0p56_bf0p55_rs0p04_lg0p08_byg0p02_pg0p18_sk0p08_sam0p02_shr0p09_srs1_spg1p5_pt0_pd1_lfgm1_bygf1 | 0 | seed_000 | -0.5886 | -0.4442 | -0.0011 | 0.0022 | 0.0973 | 89.3333 | 22 | 0.0042 | `low_forward_velocity` |
| planner_p0p72_bf0p4_rs0p04_lg0p1_byg0p06_pg0p24_sk0p08_sa0_shr0p03_srs1_spg0p5_pt0_pd1_lfgm0p5_bygf0p5 | 0 | seed_000 | -0.6148 | -0.5155 | 0.0006 | 0.0026 | 0.1023 | 94.0000 | 8 | 0.0043 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| planner_p0p56_bf0p4_rs0p04_lg0p08_byg0p06_pg0p18_sk0p16_sa0p02_shr0p06_srs1_spg1_pt0p03_pd2_lfg0_bygf1 | 0 | seed_000 | -0.6178 | -0.4895 | 0.0002 | 0.0041 | 0.1215 | 92.6667 | 9 | 0.0065 | `double_support_dominates, high_lateral_velocity, low_forward_velocity, too_little_single_support` |
| planner_p0p64_bf0p4_rs0p04_lg0p08_byg0p06_pg0p18_sk0p16_sa0_shr0p03_srs0p5_spg1p5_pt0p03_pd2_lfg0p5_bygf1 | 0 | seed_002 | -0.6630 | -0.6116 | -0.0028 | 0.0039 | 0.1673 | 71.3333 | 40 | 0.0054 | `high_lateral_velocity, low_forward_velocity` |
| planner_p0p56_bf0p4_rs0p02_lg0p08_byg0p06_pg0p24_sk0p12_sam0p02_shr0p03_srs1_spg0p5_pt0_pd1_lfg0_bygf1 | 0 | seed_000 | -0.6979 | -0.5442 | 0.0002 | 0.0025 | 0.1079 | 93.3333 | 8 | 0.0040 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| planner_p0p56_bf0p25_rs0p06_lg0p06_byg0p06_pg0p12_sk0p12_sa0_shr0p03_srs1_spg1p5_ptm0p03_pd1_lfg1_bygfm0p5 | 0 | seed_000 | -0.7986 | -0.7944 | -0.0023 | -0.0012 | 0.1776 | 73.3333 | 34 | 0.0053 | `high_lateral_velocity, low_forward_velocity` |
| planner_p0p72_bf0p4_rs0p02_lg0p1_byg0p04_pg0p18_sk0p16_sam0p02_shr0p09_srs0p5_spg1_ptm0p03_pd1_lfg0p5_bygf0p5 | 0 | seed_000 | -0.8049 | -0.6643 | -0.0028 | -0.0000 | 0.1455 | 83.3333 | 34 | 0.0066 | `high_lateral_velocity, low_forward_velocity` |
| planner_p0p64_bf0p4_rs0p04_lg0p1_byg0p04_pg0p24_sk0p12_sam0p02_shr0p09_srs0p5_spg0p5_ptm0p03_pd1_lfg0p5_bygfm1 | 0 | seed_000 | -0.8323 | -0.6883 | -0.0025 | -0.0012 | 0.1468 | 77.3333 | 37 | 0.0052 | `high_lateral_velocity, low_forward_velocity` |
| planner_p0p72_bf0p25_rs0p04_lg0p08_byg0p04_pg0p18_sk0p12_sa0_shr0p06_srs0p5_spg1_pt0p03_pd2_lfg1_bygf0 | 0 | seed_000 | -0.8398 | -0.7836 | -0.0030 | -0.0018 | 0.1692 | 76.6667 | 32 | 0.0053 | `high_lateral_velocity, low_forward_velocity` |
| planner_p0p56_bf0p25_rs0p06_lg0p1_byg0p04_pg0p24_sk0p12_sa0p02_shr0p03_srs1_spg0p5_ptm0p03_pd2_lfg0p5_bygfm1 | 0 | seed_000 | -0.8700 | -0.7334 | -0.0023 | 0.0001 | 0.1547 | 79.3333 | 33 | 0.0055 | `high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
