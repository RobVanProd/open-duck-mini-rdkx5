# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `60`
- mode_count: `30`
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
- `low_forward_velocity`: `30`
- `double_support_dominates`: `21`
- `single_support_not_balanced`: `17`
- `too_little_single_support`: `15`
- `high_lateral_velocity`: `9`
- `single_contact_pattern_dominates`: `3`

### seed_002
- `low_forward_velocity`: `30`
- `high_lateral_velocity`: `12`
- `double_support_dominates`: `11`
- `too_little_single_support`: `3`
- `high_sent_target_velocity`: `1`
- `single_contact_pattern_dominates`: `1`
- `single_support_not_balanced`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| planner_p0p56_bf0p55_rs0p06_lg0p1_byg0p06_pg0p12_sk0p16_sa0p02_shr0p09_srs0p5_spg1p5_pt0_pd1_lfgm1_bygf0p5 | 0 | seed_000 | -0.3064 | -0.2980 | 0.0015 | 0.0034 | 0.1197 | 85.0000 | 22 | 0.0066 | `low_forward_velocity` |
| planner_p0p64_bf0p25_rs0p06_lg0p1_byg0p06_pg0p18_sk0p08_sa0p02_shr0p03_srs0p5_spg0p5_pt0p03_pd2_lfgm1_bygfm0p5 | 0 | seed_000 | -0.3077 | -0.2982 | 0.0014 | 0.0035 | 0.0869 | 83.0000 | 24 | 0.0051 | `low_forward_velocity` |
| planner_p0p64_bf0p4_rs0p02_lg0p06_byg0p06_pg0p24_sk0p16_sa0_shr0p03_srs0p5_spg1_pt0_pd1_lfg1_bygf0p5 | 0 | seed_002 | -0.3212 | -0.3150 | 0.0012 | -0.0002 | 0.1181 | 83.0000 | 22 | 0.0054 | `low_forward_velocity` |
| planner_p0p56_bf0p25_rs0p06_lg0p1_byg0p02_pg0p24_sk0p08_sa0_shr0p09_srs1_spg0p5_ptm0p03_pd2_lfgm1_bygf0p5 | 0 | seed_000 | -0.3212 | -0.2943 | -0.0000 | 0.0058 | 0.0552 | 90.0000 | 15 | 0.0052 | `low_forward_velocity` |
| planner_p0p64_bf0p55_rs0p02_lg0p08_byg0p02_pg0p24_sk0p12_sam0p02_shr0p09_srs1_spg0p5_pt0_pd1_lfg1_bygf0 | 0 | seed_000 | -0.3636 | -0.3324 | -0.0030 | 0.0021 | 0.1124 | 88.0000 | 12 | 0.0038 | `low_forward_velocity` |
| planner_p0p72_bf0p55_rs0p04_lg0p06_byg0p02_pg0p24_sk0p08_sa0_shr0p03_srs0p5_spg0p5_pt0_pd1_lfgm1_bygfm0p5 | 0 | seed_000 | -0.3753 | -0.3533 | -0.0033 | 0.0010 | 0.1185 | 91.0000 | 8 | 0.0047 | `double_support_dominates, low_forward_velocity` |
| planner_p0p72_bf0p55_rs0p02_lg0p08_byg0p04_pg0p18_sk0p12_sam0p02_shr0p06_srs1_spg1p5_pt0p03_pd2_lfgm1_bygf1 | 0 | seed_000 | -0.3790 | -0.3580 | -0.0024 | 0.0003 | 0.1115 | 91.0000 | 8 | 0.0047 | `double_support_dominates, low_forward_velocity` |
| planner_p0p64_bf0p4_rs0p04_lg0p08_byg0p02_pg0p18_sk0p12_sa0p02_shr0p03_srs1_spg0p5_pt0p03_pd2_lfgm0p5_bygfm0p5 | 0 | seed_002 | -0.4033 | -0.3683 | -0.0017 | 0.0030 | 0.1313 | 91.0000 | 8 | 0.0058 | `double_support_dominates, high_lateral_velocity, low_forward_velocity` |
| planner_p0p56_bf0p4_rs0p02_lg0p08_byg0p06_pg0p12_sk0p08_sam0p02_shr0p06_srs0p5_spg1_pt0_pd1_lfgm1_bygf0 | 0 | seed_002 | -0.4081 | -0.4031 | -0.0022 | -0.0010 | 0.0727 | 93.0000 | 5 | 0.0038 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| planner_p0p56_bf0p25_rs0p02_lg0p08_byg0p02_pg0p18_sk0p12_sa0p02_shr0p03_srs1_spg1p5_ptm0p03_pd2_lfg1_bygf0p5 | 0 | seed_000 | -0.4556 | -0.3976 | -0.0019 | -0.0025 | 0.0883 | 90.0000 | 17 | 0.0037 | `low_forward_velocity` |
| planner_p0p72_bf0p55_rs0p02_lg0p1_byg0p06_pg0p24_sk0p16_sam0p02_shr0p09_srs0p5_spg1p5_pt0_pd1_lfgm1_bygf0p5 | 0 | seed_000 | -0.4569 | -0.3953 | -0.0021 | 0.0007 | 0.1184 | 91.0000 | 8 | 0.0061 | `double_support_dominates, low_forward_velocity` |
| planner_p0p64_bf0p4_rs0p04_lg0p06_byg0p04_pg0p18_sk0p16_sa0_shr0p03_srs0p5_spg1p5_pt0_pd1_lfg0p5_bygfm0p5 | 0 | seed_000 | -0.4670 | -0.4132 | -0.0009 | -0.0024 | 0.1128 | 91.0000 | 12 | 0.0058 | `double_support_dominates, low_forward_velocity` |
| planner_p0p72_bf0p25_rs0p02_lg0p08_byg0p06_pg0p24_sk0p12_sa0p02_shr0p09_srs0p5_spg1p5_ptm0p03_pd1_lfg0p5_bygf0p5 | 0 | seed_000 | -0.4823 | -0.4100 | -0.0028 | -0.0022 | 0.1092 | 90.0000 | 13 | 0.0064 | `low_forward_velocity` |
| planner_p0p64_bf0p25_rs0p02_lg0p08_byg0p02_pg0p24_sk0p12_sa0p02_shr0p09_srs1_spg0p5_pt0p03_pd1_lfgm1_bygf0p5 | 0 | seed_000 | -0.4912 | -0.4435 | -0.0014 | 0.0083 | 0.1388 | 90.0000 | 8 | 0.0076 | `high_lateral_velocity, low_forward_velocity` |
| planner_p0p56_bf0p55_rs0p04_lg0p08_byg0p02_pg0p18_sk0p08_sam0p02_shr0p09_srs1_spg1p5_pt0_pd1_lfgm1_bygf1 | 0 | seed_000 | -0.4928 | -0.4270 | -0.0016 | -0.0026 | 0.0745 | 91.0000 | 14 | 0.0041 | `double_support_dominates, low_forward_velocity` |
| planner_p0p56_bf0p4_rs0p04_lg0p08_byg0p06_pg0p18_sk0p16_sa0p02_shr0p06_srs1_spg1_pt0p03_pd2_lfg0_bygf1 | 0 | seed_000 | -0.5005 | -0.4327 | 0.0022 | 0.0053 | 0.1215 | 93.0000 | 6 | 0.0057 | `double_support_dominates, high_lateral_velocity, low_forward_velocity, too_little_single_support` |
| planner_p0p72_bf0p4_rs0p04_lg0p1_byg0p06_pg0p24_sk0p08_sa0_shr0p03_srs1_spg0p5_pt0_pd1_lfgm0p5_bygf0p5 | 0 | seed_000 | -0.5296 | -0.4552 | -0.0012 | 0.0019 | 0.1272 | 91.0000 | 8 | 0.0048 | `double_support_dominates, high_lateral_velocity, low_forward_velocity` |
| planner_p0p64_bf0p4_rs0p04_lg0p08_byg0p06_pg0p18_sk0p16_sa0_shr0p03_srs0p5_spg1p5_pt0p03_pd2_lfg0p5_bygf1 | 0 | seed_002 | -0.5647 | -0.4687 | -0.0022 | 0.0010 | 0.1518 | 73.0000 | 30 | 0.0048 | `high_lateral_velocity, low_forward_velocity` |
| planner_p0p56_bf0p25_rs0p04_lg0p08_byg0p04_pg0p12_sk0p16_sam0p02_shr0p06_srs1_spg1_ptm0p03_pd2_lfg0p5_bygf0 | 0 | seed_000 | -0.5696 | -0.4738 | -0.0031 | -0.0023 | 0.1042 | 92.0000 | 12 | 0.0037 | `double_support_dominates, low_forward_velocity` |
| planner_p0p56_bf0p25_rs0p06_lg0p06_byg0p06_pg0p12_sk0p12_sa0_shr0p03_srs1_spg1p5_ptm0p03_pd1_lfg1_bygfm0p5 | 0 | seed_000 | -0.5728 | -0.5058 | -0.0041 | -0.0039 | 0.1309 | 83.0000 | 18 | 0.0037 | `high_lateral_velocity, low_forward_velocity` |
| planner_p0p64_bf0p4_rs0p04_lg0p1_byg0p06_pg0p24_sk0p16_sa0_shr0p06_srs1_spg1_ptm0p03_pd2_lfgm1_bygf1 | 0 | seed_002 | -0.5930 | -0.5342 | 0.0005 | 0.0030 | 0.0978 | 97.0000 | 5 | 0.0056 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| planner_p0p64_bf0p4_rs0p04_lg0p1_byg0p04_pg0p24_sk0p12_sam0p02_shr0p09_srs0p5_spg0p5_ptm0p03_pd1_lfg0p5_bygfm1 | 0 | seed_000 | -0.6083 | -0.4819 | -0.0015 | -0.0012 | 0.1233 | 87.0000 | 19 | 0.0050 | `high_lateral_velocity, low_forward_velocity` |
| planner_p0p56_bf0p4_rs0p02_lg0p08_byg0p06_pg0p24_sk0p12_sam0p02_shr0p03_srs1_spg0p5_pt0_pd1_lfg0_bygf1 | 0 | seed_000 | -0.6309 | -0.4570 | 0.0010 | 0.0041 | 0.1177 | 90.0000 | 8 | 0.0051 | `low_forward_velocity` |
| planner_p0p64_bf0p55_rs0p06_lg0p06_byg0p06_pg0p18_sk0p12_sa0p02_shr0p06_srs0p5_spg1p5_ptm0p03_pd1_lfg0p5_bygfm0p5 | 0 | seed_002 | -0.6321 | -0.5815 | -0.0026 | -0.0022 | 0.1568 | 80.0000 | 32 | 0.0046 | `high_lateral_velocity, low_forward_velocity` |
| planner_p0p56_bf0p25_rs0p06_lg0p1_byg0p04_pg0p24_sk0p12_sa0p02_shr0p03_srs1_spg0p5_ptm0p03_pd2_lfg0p5_bygfm1 | 0 | seed_000 | -0.6498 | -0.4894 | -0.0019 | -0.0011 | 0.1060 | 85.0000 | 19 | 0.0037 | `low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
