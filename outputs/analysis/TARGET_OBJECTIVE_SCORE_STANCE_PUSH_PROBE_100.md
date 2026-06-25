# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `96`
- mode_count: `48`
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
- `low_forward_velocity`: `48`
- `double_support_dominates`: `40`
- `single_support_not_balanced`: `31`
- `too_little_single_support`: `22`
- `single_contact_pattern_dominates`: `6`
- `high_lateral_velocity`: `3`
- `too_few_contact_transitions`: `1`

### seed_002
- `low_forward_velocity`: `48`
- `double_support_dominates`: `41`
- `too_little_single_support`: `25`
- `high_lateral_velocity`: `9`
- `single_contact_pattern_dominates`: `4`
- `single_support_not_balanced`: `2`
- `too_few_contact_transitions`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p56_hrb0p06_hra0p06_hrph0_hb0_h0p025_kb0p04_k0p14_ab0_a0_ph0p7854_ld0p32_ls0p75_sp0p04_sas0p5 | 0 | seed_002 | -0.2631 | -0.2514 | 0.0089 | 0.0108 | 0.0768 | 92.0000 | 11 | 0.0055 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p64_hrb0p02_hra0p06_hrph0_hb0p02_h0p04_kb0p04_k0p14_ab0_a0_ph0_ld0p4_ls1_sp0p02_sasm0p5 | 0 | seed_000 | -0.3068 | -0.2966 | 0.0015 | 0.0060 | 0.0812 | 91.0000 | 10 | 0.0062 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p64_hrb0p06_hra0p06_hrph0_hb0p02_h0p04_kb0p02_k0p14_ab0_a0p01_ph0p7854_ld0p32_ls0p75_sp0p02_sas0 | 0 | seed_002 | -0.3145 | -0.3028 | 0.0032 | 0.0051 | 0.0773 | 92.0000 | 11 | 0.0055 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p64_hrb0p04_hra0p06_hrph0_hb0_h0p025_kb0p02_k0p14_ab0_am0p00625_ph0p7854_ld0p24_ls1_sp0p04_sasm0p5 | 0 | seed_000 | -0.3216 | -0.3127 | -0.0002 | 0.0018 | 0.1042 | 88.0000 | 6 | 0.0065 | `low_forward_velocity` |
| primitive_p0p72_hrb0p06_hra0p06_hrph1p5708_hb0_h0p04_kb0p04_k0p1_ab0_a0p01_ph0_ld0p4_ls0p75_spm0p04_sasm0p5 | 0 | seed_002 | -0.3418 | -0.3301 | 0.0046 | 0.0087 | 0.1010 | 93.0000 | 9 | 0.0041 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p48_hrb0p04_hra0p06_hrph0_hb0_h0p025_kb0p04_k0p14_ab0_am0p00625_ph1p5708_ld0p32_ls0p75_sp0p02_sasm0p5 | 0 | seed_000 | -0.3448 | -0.3312 | 0.0039 | 0.0047 | 0.1021 | 92.0000 | 9 | 0.0056 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p56_hrb0p04_hra0p06_hrph0_hb0p02_h0p04_kb0p02_k0p1_ab0_a0p01_ph0_ld0p24_ls1_sp0p02_sas0 | 0 | seed_002 | -0.3459 | -0.3179 | 0.0033 | 0.0060 | 0.0718 | 93.0000 | 9 | 0.0057 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p72_hrb0p06_hra0p06_hrphm1p5708_hb0_h0p025_kb0p02_k0p14_ab0_a0_ph0_ld0p24_ls0p75_sp0p04_sasm0p5 | 0 | seed_002 | -0.3499 | -0.3475 | -0.0006 | 0.0011 | 0.0701 | 92.0000 | 9 | 0.0062 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p64_hrb0p06_hra0p06_hrph1p5708_hb0_h0p025_kb0p02_k0p14_ab0_am0p00625_ph0_ld0p4_ls0p75_spm0p04_sas0 | 0 | seed_000 | -0.3557 | -0.3462 | 0.0005 | 0.0026 | 0.0896 | 92.0000 | 9 | 0.0043 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p48_hrb0p02_hra0p06_hrphm1p5708_hb0_h0p025_kb0p04_k0p1_ab0_a0p00625_ph0_ld0p24_ls1_sp0p02_sas0 | 0 | seed_000 | -0.3576 | -0.3178 | 0.0003 | 0.0047 | 0.1122 | 88.0000 | 12 | 0.0044 | `low_forward_velocity` |
| primitive_p0p48_hrb0p02_hra0p06_hrph0_hb0p02_h0p04_kb0p02_k0p1_ab0_a0_ph0_ld0p32_ls0p75_sp0p04_sas0 | 0 | seed_002 | -0.3659 | -0.3510 | 0.0004 | 0.0038 | 0.0922 | 93.0000 | 5 | 0.0057 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p72_hrb0p02_hra0p06_hrphm1p5708_hb0_h0p025_kb0p02_k0p1_ab0_am0p00625_ph0p7854_ld0p4_ls1_spm0p02_sas0p5 | 0 | seed_000 | -0.3712 | -0.3285 | -0.0014 | 0.0038 | 0.0939 | 90.0000 | 6 | 0.0046 | `low_forward_velocity` |
| primitive_p0p56_hrb0p02_hra0p06_hrphm1p5708_hb0_h0p04_kb0p04_k0p1_ab0_a0p01_ph1p5708_ld0p32_ls1_sp0p04_sas0 | 0 | seed_000 | -0.3767 | -0.3565 | 0.0004 | 0.0071 | 0.1124 | 93.0000 | 7 | 0.0057 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p72_hrb0p02_hra0p06_hrphm1p5708_hb0_h0p025_kb0p02_k0p1_ab0_a0p00625_ph1p5708_ld0p4_ls0p75_sp0p04_sas0 | 0 | seed_000 | -0.3799 | -0.3736 | 0.0000 | 0.0036 | 0.1105 | 93.0000 | 9 | 0.0051 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p48_hrb0p04_hra0p06_hrph1p5708_hb0_h0p04_kb0p02_k0p14_ab0_a0_ph0p7854_ld0p24_ls0p75_spm0p02_sas0 | 0 | seed_000 | -0.3826 | -0.3471 | -0.0003 | 0.0032 | 0.1121 | 91.0000 | 7 | 0.0048 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p48_hrb0p04_hra0p04_hrphm1p5708_hb0p02_h0p025_kb0p04_k0p1_ab0_a0_ph0p7854_ld0p32_ls1_sp0p02_sas0 | 0 | seed_002 | -0.3841 | -0.3534 | 0.0042 | 0.0062 | 0.1132 | 94.0000 | 7 | 0.0054 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p72_hrb0p06_hra0p06_hrph1p5708_hb0p02_h0p04_kb0p04_k0p14_ab0_a0p01_ph1p5708_ld0p4_ls0p75_sp0p02_sas0 | 0 | seed_000 | -0.3843 | -0.3768 | 0.0062 | 0.0079 | 0.1100 | 94.0000 | 7 | 0.0080 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p56_hrb0p02_hra0p06_hrphm1p5708_hb0p02_h0p025_kb0p02_k0p1_ab0_am0p00625_ph0_ld0p24_ls0p75_sp0p02_sas0 | 0 | seed_000 | -0.3851 | -0.3473 | -0.0006 | 0.0056 | 0.0893 | 92.0000 | 6 | 0.0052 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p56_hrb0p06_hra0p06_hrph0_hb0p02_h0p025_kb0p04_k0p1_ab0_a0p00625_ph0p7854_ld0p24_ls0p75_sp0p04_sas0p5 | 0 | seed_002 | -0.3865 | -0.3317 | 0.0070 | 0.0104 | 0.0945 | 95.0000 | 5 | 0.0050 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p64_hrb0p02_hra0p06_hrph1p5708_hb0_h0p025_kb0p04_k0p14_ab0_a0p00625_ph1p5708_ld0p24_ls1_spm0p04_sas0p5 | 0 | seed_002 | -0.3948 | -0.3788 | -0.0004 | 0.0036 | 0.1284 | 92.0000 | 7 | 0.0052 | `double_support_dominates, high_lateral_velocity, low_forward_velocity` |
| primitive_p0p64_hrb0p04_hra0p04_hrph0_hb0_h0p04_kb0p04_k0p1_ab0_a0_ph1p5708_ld0p24_ls0p75_sp0p02_sas0p5 | 0 | seed_002 | -0.3984 | -0.3796 | 0.0066 | 0.0091 | 0.1084 | 95.0000 | 5 | 0.0052 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p72_hrb0p02_hra0p06_hrphm1p5708_hb0_h0p04_kb0p04_k0p1_ab0_am0p01_ph0p7854_ld0p32_ls1_sp0p04_sasm0p5 | 0 | seed_000 | -0.4069 | -0.3679 | -0.0034 | 0.0012 | 0.1083 | 91.0000 | 6 | 0.0060 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p56_hrb0p06_hra0p06_hrphm1p5708_hb0p02_h0p025_kb0p02_k0p14_ab0_a0_ph1p5708_ld0p24_ls1_spm0p04_sasm0p5 | 0 | seed_000 | -0.4134 | -0.3305 | 0.0037 | 0.0086 | 0.1206 | 89.0000 | 9 | 0.0049 | `high_lateral_velocity, low_forward_velocity` |
| primitive_p0p56_hrb0p06_hra0p04_hrph1p5708_hb0p02_h0p025_kb0p04_k0p14_ab0_a0p00625_ph0_ld0p24_ls1_spm0p04_sas0p5 | 0 | seed_000 | -0.4175 | -0.3480 | -0.0022 | 0.0046 | 0.0972 | 90.0000 | 7 | 0.0049 | `low_forward_velocity` |
| primitive_p0p48_hrb0p06_hra0p06_hrphm1p5708_hb0_h0p04_kb0p02_k0p1_ab0_am0p01_ph0_ld0p24_ls0p75_sp0p02_sas0 | 0 | seed_000 | -0.4330 | -0.3684 | 0.0008 | 0.0040 | 0.1176 | 91.0000 | 10 | 0.0049 | `double_support_dominates, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
