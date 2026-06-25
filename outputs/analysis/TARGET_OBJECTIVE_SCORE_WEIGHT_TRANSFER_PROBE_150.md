# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `144`
- mode_count: `72`
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
- `low_forward_velocity`: `72`
- `double_support_dominates`: `51`
- `too_little_single_support`: `43`
- `single_support_not_balanced`: `33`
- `single_contact_pattern_dominates`: `16`
- `high_lateral_velocity`: `13`

### seed_002
- `low_forward_velocity`: `72`
- `double_support_dominates`: `56`
- `too_little_single_support`: `51`
- `single_contact_pattern_dominates`: `36`
- `single_support_not_balanced`: `22`
- `high_lateral_velocity`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p48_hrb0p06_hra0p08_hrphm1p5708_hb0_h0p04_kb0p04_k0p1_ab0_a0p01_ph1p5708_ld0p4_ls1 | 0 | seed_000 | -0.3037 | -0.2959 | 0.0018 | 0.0035 | 0.1126 | 88.0000 | 20 | 0.0041 | `low_forward_velocity` |
| primitive_p0p48_hrb0p06_hra0p08_hrph0_hb0_h0p025_kb0p02_k0p1_ab0_a0p00625_ph1p5708_ld0p4_ls1 | 0 | seed_002 | -0.3127 | -0.3126 | 0.0008 | 0.0008 | 0.0841 | 85.3333 | 30 | 0.0047 | `low_forward_velocity` |
| primitive_p0p56_hrb0p06_hra0p08_hrphm1p5708_hb0_h0p025_kb0p04_k0p14_ab0_am0p00625_ph0p7854_ld0p24_ls0p75 | 0 | seed_000 | -0.3141 | -0.3020 | 0.0007 | 0.0033 | 0.0696 | 86.6667 | 26 | 0.0037 | `low_forward_velocity` |
| primitive_p0p56_hrb0p04_hra0p08_hrph0_hb0p02_h0p025_kb0p04_k0p1_ab0_a0p00625_ph0_ld0p24_ls1 | 0 | seed_000 | -0.3164 | -0.3040 | 0.0004 | 0.0032 | 0.1036 | 84.6667 | 31 | 0.0052 | `low_forward_velocity` |
| primitive_p0p64_hrb0p06_hra0p08_hrph1p5708_hb0_h0p04_kb0p02_k0p1_ab0_a0p01_ph0p7854_ld0p4_ls0p75 | 0 | seed_002 | -0.3186 | -0.3136 | 0.0013 | 0.0016 | 0.1041 | 90.6667 | 14 | 0.0045 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p48_hrb0p06_hra0p08_hrphm1p5708_hb0p02_h0p04_kb0p02_k0p1_ab0_a0p01_ph1p5708_ld0p32_ls0p75 | 0 | seed_000 | -0.3203 | -0.3067 | -0.0000 | 0.0030 | 0.0860 | 86.0000 | 29 | 0.0037 | `low_forward_velocity` |
| primitive_p0p72_hrb0p04_hra0p08_hrphm1p5708_hb0_h0p025_kb0p04_k0p14_ab0_am0p00625_ph0_ld0p24_ls1 | 0 | seed_000 | -0.3225 | -0.3097 | -0.0003 | 0.0026 | 0.1017 | 82.6667 | 24 | 0.0039 | `low_forward_velocity` |
| primitive_p0p64_hrb0p02_hra0p06_hrph0_hb0_h0p04_kb0p04_k0p14_ab0_a0p01_ph1p5708_ld0p32_ls1 | 0 | seed_002 | -0.3257 | -0.3243 | 0.0012 | 0.0038 | 0.0896 | 92.0000 | 11 | 0.0047 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p64_hrb0p04_hra0p08_hrph0_hb0_h0p04_kb0p02_k0p14_ab0_a0p01_ph1p5708_ld0p32_ls0p75 | 0 | seed_000 | -0.3260 | -0.3204 | -0.0008 | 0.0006 | 0.1007 | 85.3333 | 25 | 0.0041 | `low_forward_velocity` |
| primitive_p0p72_hrb0p06_hra0p08_hrphm1p5708_hb0_h0p04_kb0p04_k0p14_ab0_a0p01_ph0_ld0p32_ls1 | 0 | seed_000 | -0.3320 | -0.3190 | -0.0015 | 0.0015 | 0.0707 | 84.0000 | 30 | 0.0053 | `low_forward_velocity` |
| primitive_p0p56_hrb0p04_hra0p08_hrph1p5708_hb0p02_h0p025_kb0p02_k0p14_ab0_am0p00625_ph1p5708_ld0p4_ls0p75 | 0 | seed_002 | -0.3334 | -0.3165 | 0.0023 | 0.0030 | 0.0781 | 92.0000 | 17 | 0.0059 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p48_hrb0p04_hra0p08_hrph0_hb0p02_h0p04_kb0p02_k0p1_ab0_am0p01_ph0_ld0p4_ls1 | 0 | seed_000 | -0.3349 | -0.3338 | -0.0019 | -0.0016 | 0.1129 | 68.0000 | 51 | 0.0068 | `low_forward_velocity` |
| primitive_p0p64_hrb0p04_hra0p06_hrph0_hb0p02_h0p025_kb0p02_k0p14_ab0_am0p00625_ph0_ld0p4_ls0p75 | 0 | seed_002 | -0.3604 | -0.3409 | 0.0028 | 0.0059 | 0.0982 | 93.3333 | 9 | 0.0053 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p72_hrb0p02_hra0p06_hrph0_hb0_h0p04_kb0p02_k0p14_ab0_a0_ph0p7854_ld0p24_ls0p75 | 0 | seed_002 | -0.3745 | -0.3717 | 0.0020 | 0.0043 | 0.0889 | 93.3333 | 11 | 0.0046 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p72_hrb0p04_hra0p06_hrph0_hb0_h0p04_kb0p04_k0p14_ab0_am0p01_ph1p5708_ld0p4_ls1 | 0 | seed_000 | -0.3754 | -0.3450 | 0.0042 | 0.0051 | 0.0699 | 92.0000 | 13 | 0.0050 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p72_hrb0p06_hra0p08_hrph0_hb0_h0p025_kb0p02_k0p1_ab0_a0p00625_ph0_ld0p32_ls0p75 | 0 | seed_000 | -0.4001 | -0.3468 | 0.0007 | 0.0029 | 0.1021 | 84.0000 | 25 | 0.0044 | `low_forward_velocity` |
| primitive_p0p72_hrb0p02_hra0p08_hrph1p5708_hb0p02_h0p025_kb0p04_k0p14_ab0_am0p00625_ph0p7854_ld0p24_ls1 | 0 | seed_000 | -0.4011 | -0.3397 | 0.0023 | 0.0046 | 0.1171 | 80.0000 | 30 | 0.0052 | `low_forward_velocity` |
| primitive_p0p56_hrb0p06_hra0p06_hrph1p5708_hb0p02_h0p04_kb0p04_k0p1_ab0_a0p01_ph0p7854_ld0p4_ls1 | 0 | seed_002 | -0.4089 | -0.3999 | 0.0025 | 0.0035 | 0.1000 | 94.0000 | 7 | 0.0052 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p64_hrb0p04_hra0p06_hrphm1p5708_hb0p02_h0p025_kb0p02_k0p1_ab0_a0p00625_ph0p7854_ld0p24_ls1 | 0 | seed_002 | -0.4139 | -0.4136 | 0.0000 | 0.0029 | 0.0576 | 94.0000 | 7 | 0.0041 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p56_hrb0p04_hra0p06_hrph0_hb0p02_h0p04_kb0p02_k0p14_ab0_am0p01_ph0_ld0p4_ls0p75 | 0 | seed_002 | -0.4241 | -0.3668 | 0.0012 | 0.0047 | 0.0737 | 94.6667 | 9 | 0.0053 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p48_hrb0p04_hra0p06_hrphm1p5708_hb0p02_h0p04_kb0p04_k0p14_ab0_a0_ph0_ld0p32_ls1 | 0 | seed_002 | -0.4331 | -0.4305 | 0.0009 | 0.0037 | 0.1152 | 94.6667 | 9 | 0.0043 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p72_hrb0p02_hra0p04_hrph0_hb0_h0p025_kb0p04_k0p14_ab0_am0p00625_ph1p5708_ld0p32_ls1 | 0 | seed_000 | -0.4334 | -0.4150 | 0.0022 | 0.0048 | 0.0763 | 94.0000 | 9 | 0.0048 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p48_hrb0p02_hra0p04_hrphm1p5708_hb0_h0p025_kb0p04_k0p1_ab0_am0p00625_ph0p7854_ld0p32_ls1 | 0 | seed_002 | -0.4347 | -0.4164 | 0.0017 | 0.0035 | 0.0586 | 94.6667 | 7 | 0.0039 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p72_hrb0p04_hra0p08_hrph1p5708_hb0_h0p04_kb0p02_k0p14_ab0_am0p01_ph0p7854_ld0p4_ls1 | 0 | seed_000 | -0.4394 | -0.3854 | 0.0020 | 0.0027 | 0.1245 | 89.3333 | 15 | 0.0048 | `high_lateral_velocity, low_forward_velocity` |
| primitive_p0p64_hrb0p02_hra0p06_hrph0_hb0p02_h0p04_kb0p02_k0p1_ab0_am0p01_ph1p5708_ld0p32_ls0p75 | 0 | seed_002 | -0.4506 | -0.4214 | -0.0007 | 0.0018 | 0.0773 | 94.6667 | 9 | 0.0044 | `double_support_dominates, low_forward_velocity, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
