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
- `double_support_dominates`: `24`
- `single_support_not_balanced`: `14`
- `too_little_single_support`: `14`
- `high_lateral_velocity`: `5`
- `single_contact_pattern_dominates`: `2`
- `too_few_contact_transitions`: `1`

### seed_002
- `low_forward_velocity`: `31`
- `double_support_dominates`: `27`
- `too_little_single_support`: `21`
- `high_lateral_velocity`: `5`
- `single_contact_pattern_dominates`: `4`
- `missing_seed_trace_or_window`: `1`
- `single_support_not_balanced`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p64_hrb0p06_hra0p06_hrph0_hb0p02_h0p04_kb0p04_k0p1_ab0_am0p01_ph1p5708_ld0p32_ls1_spm0p02_sasm0p5_vpg1 | 0 | seed_002 | -0.2653 | -0.2611 | 0.0070 | 0.0061 | 0.0997 | 90.0000 | 9 | 0.0065 | `low_forward_velocity` |
| primitive_p0p64_hrb0p06_hra0p06_hrph0_hb0p02_h0p04_kb0p02_k0p14_ab0_a0p01_ph0p7854_ld0p24_ls0p75_sp0p02_sas0p5_vpg1 | 0 | seed_002 | -0.2680 | -0.2647 | 0.0065 | 0.0080 | 0.1022 | 91.0000 | 9 | 0.0056 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p48_hrb0p04_hra0p06_hrph0_hb0p02_h0p025_kb0p04_k0p14_ab0_am0p00625_ph0_ld0p4_ls0p75_sp0_sasm0p5_vpgm1 | 0 | seed_000 | -0.2834 | -0.2647 | 0.0041 | 0.0082 | 0.1113 | 89.0000 | 11 | 0.0086 | `low_forward_velocity` |
| primitive_p0p48_hrb0p06_hra0p06_hrph1p5708_hb0_h0p025_kb0p04_k0p14_ab0_a0_ph0_ld0p24_ls0p75_sp0p02_sasm0p5_vpgm1 | 0 | seed_000 | -0.2986 | -0.2944 | 0.0046 | 0.0055 | 0.1062 | 91.0000 | 7 | 0.0051 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p56_hrb0p06_hra0p06_hrph0_hb0p02_h0p04_kb0p04_k0p14_ab0_a0_ph0_ld0p4_ls0p75_spm0p02_sas0_vpg0p5 | 0 | seed_002 | -0.3184 | -0.3168 | 0.0049 | 0.0092 | 0.1276 | 91.0000 | 10 | 0.0054 | `double_support_dominates, high_lateral_velocity, low_forward_velocity` |
| primitive_p0p64_hrb0p02_hra0p06_hrph0_hb0p02_h0p04_kb0p02_k0p1_ab0_a0p01_ph0p7854_ld0p32_ls0p75_sp0_sasm0p5_vpgm1 | 0 | seed_000 | -0.3291 | -0.3196 | 0.0034 | 0.0056 | 0.0683 | 92.0000 | 7 | 0.0057 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p64_hrb0p04_hra0p06_hrph0_hb0_h0p04_kb0p02_k0p1_ab0_a0_ph0p7854_ld0p24_ls1_sp0p02_sasm0p5_vpgm1 | 0 | seed_000 | -0.3483 | -0.3083 | 0.0016 | 0.0057 | 0.0822 | 90.0000 | 9 | 0.0075 | `low_forward_velocity` |
| primitive_p0p48_hrb0p02_hra0p06_hrph0_hb0_h0p025_kb0p04_k0p14_ab0_a0p00625_ph0_ld0p4_ls1_spm0p02_sasm0p5_vpg1 | 0 | seed_000 | -0.3597 | -0.3044 | 0.0045 | 0.0079 | 0.1141 | 90.0000 | 16 | 0.0045 | `low_forward_velocity` |
| primitive_p0p48_hrb0p02_hra0p04_hrph0_hb0p02_h0p025_kb0p04_k0p1_ab0_a0_ph0p7854_ld0p24_ls0p75_sp0_sas0p5_vpg0p5 | 0 | seed_002 | -0.3704 | -0.3453 | 0.0044 | 0.0077 | 0.1075 | 94.0000 | 7 | 0.0054 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p56_hrb0p02_hra0p06_hrphm1p5708_hb0_h0p04_kb0p04_k0p1_ab0_am0p01_ph1p5708_ld0p32_ls1_sp0_sas0p5_vpg0p5 | 0 | seed_002 | -0.3797 | -0.3634 | -0.0009 | 0.0067 | 0.0911 | 94.0000 | 5 | 0.0045 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p56_hrb0p02_hra0p04_hrph1p5708_hb0p02_h0p025_kb0p02_k0p14_ab0_a0_ph0p7854_ld0p4_ls0p75_sp0p02_sasm0p5_vpgm1 | 0 | seed_000 | -0.3983 | -0.3895 | 0.0046 | 0.0066 | 0.0689 | 94.0000 | 7 | 0.0057 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p56_hrb0p02_hra0p04_hrphm1p5708_hb0p02_h0p025_kb0p02_k0p14_ab0_a0p00625_ph0p7854_ld0p24_ls1_sp0_sas0p5_vpgm1 | 0 | seed_000 | -0.4041 | -0.3559 | 0.0018 | 0.0058 | 0.0740 | 92.0000 | 7 | 0.0054 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p56_hrb0p02_hra0p04_hrph0_hb0_h0p025_kb0p02_k0p1_ab0_a0p00625_ph0_ld0p24_ls1_spm0p02_sasm0p5_vpgm1 | 0 | seed_002 | -0.4050 | -0.3679 | 0.0051 | 0.0083 | 0.0923 | 95.0000 | 5 | 0.0053 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p48_hrb0p06_hra0p04_hrph0_hb0p02_h0p04_kb0p02_k0p14_ab0_a0p01_ph0_ld0p24_ls1_spm0p02_sasm0p5_vpgm1 | 0 | seed_002 | -0.4071 | -0.3537 | 0.0022 | 0.0081 | 0.0891 | 95.0000 | 5 | 0.0057 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p56_hrb0p02_hra0p06_hrphm1p5708_hb0p02_h0p04_kb0p02_k0p1_ab0_a0p01_ph0p7854_ld0p32_ls0p75_sp0p02_sasm0p5_vpg0p5 | 0 | seed_000 | -0.4152 | -0.3402 | 0.0028 | 0.0105 | 0.1189 | 92.0000 | 8 | 0.0062 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p56_hrb0p02_hra0p04_hrph0_hb0p02_h0p025_kb0p04_k0p1_ab0_a0p00625_ph1p5708_ld0p32_ls0p75_vpg0p5 | 0 | seed_002 | -0.4170 | -0.3836 | 0.0033 | 0.0070 | 0.1076 | 95.0000 | 5 | 0.0062 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p48_hrb0p02_hra0p06_hrph1p5708_hb0p02_h0p04_kb0p04_k0p1_ab0_a0p01_ph1p5708_ld0p24_ls1_sp0p02_sas0p5_vpgm1 | 0 | seed_002 | -0.4188 | -0.3839 | 0.0034 | 0.0034 | 0.1212 | 94.0000 | 5 | 0.0067 | `double_support_dominates, high_lateral_velocity, low_forward_velocity, too_little_single_support` |
| primitive_p0p56_hrb0p04_hra0p04_hrph0_hb0_h0p04_kb0p04_k0p14_ab0_a0_ph0p7854_ld0p24_ls0p75_spm0p02_sas0_vpgm1 | 0 | seed_000 | -0.4236 | -0.4090 | 0.0063 | 0.0095 | 0.0859 | 95.0000 | 3 | 0.0051 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p64_hrb0p02_hra0p04_hrphm1p5708_hb0p02_h0p025_kb0p02_k0p14_ab0_am0p00625_ph1p5708_ld0p4_ls1_sp0_sasm0p5_vpgm1 | 0 | seed_002 | -0.4279 | -0.3383 | 0.0079 | 0.0075 | 0.1219 | 95.0000 | 5 | 0.0059 | `double_support_dominates, high_lateral_velocity, low_forward_velocity, too_little_single_support` |
| primitive_p0p64_hrb0p06_hra0p04_hrph0_hb0p02_h0p04_kb0p02_k0p14_ab0_a0p01_ph0_ld0p4_ls1_sp0_sas0p5_vpg0p5 | 0 | seed_002 | -0.4285 | -0.3902 | 0.0006 | 0.0068 | 0.1312 | 93.0000 | 9 | 0.0068 | `double_support_dominates, high_lateral_velocity, low_forward_velocity, too_little_single_support` |
| primitive_p0p56_hrb0p06_hra0p04_hrph1p5708_hb0p02_h0p04_kb0p02_k0p1_ab0_am0p01_ph0_ld0p4_ls0p75_spm0p02_sas0p5_vpg0p5 | 0 | seed_000 | -0.4294 | -0.3936 | 0.0012 | 0.0063 | 0.1218 | 93.0000 | 5 | 0.0052 | `double_support_dominates, high_lateral_velocity, low_forward_velocity, too_little_single_support` |
| primitive_p0p48_hrb0p02_hra0p04_hrphm1p5708_hb0p02_h0p025_kb0p04_k0p14_ab0_a0_ph1p5708_ld0p4_ls1_sp0p02_sas0p5_vpg0p5 | 0 | seed_002 | -0.4490 | -0.3905 | 0.0076 | 0.0101 | 0.1082 | 96.0000 | 3 | 0.0054 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, too_little_single_support` |
| primitive_p0p56_hrb0p04_hra0p04_hrph1p5708_hb0_h0p025_kb0p02_k0p14_ab0_a0p00625_ph1p5708_ld0p4_ls0p75_vpg1 | 0 | seed_000 | -0.4515 | -0.4396 | 0.0032 | 0.0058 | 0.0881 | 95.0000 | 3 | 0.0057 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p64_hrb0p06_hra0p04_hrph0_hb0_h0p04_kb0p02_k0p14_ab0_a0_ph0_ld0p24_ls0p75_spm0p02_sasm0p5_vpg1 | 0 | seed_002 | -0.4672 | -0.4518 | -0.0046 | 0.0014 | 0.1109 | 95.0000 | 5 | 0.0049 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p48_hrb0p06_hra0p04_hrph1p5708_hb0_h0p04_kb0p02_k0p1_ab0_a0_ph0p7854_ld0p32_ls0p75_sp0p02_sas0p5_vpgm1 | 0 | seed_000 | -0.4720 | -0.4392 | 0.0009 | 0.0037 | 0.1101 | 94.0000 | 5 | 0.0051 | `double_support_dominates, low_forward_velocity, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
