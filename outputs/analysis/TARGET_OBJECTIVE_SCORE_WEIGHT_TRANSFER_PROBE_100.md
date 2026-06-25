# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `144`
- mode_count: `72`
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
- `low_forward_velocity`: `72`
- `double_support_dominates`: `44`
- `single_support_not_balanced`: `32`
- `too_little_single_support`: `22`
- `high_lateral_velocity`: `11`
- `too_few_contact_transitions`: `3`
- `single_contact_pattern_dominates`: `1`

### seed_002
- `low_forward_velocity`: `72`
- `double_support_dominates`: `51`
- `too_little_single_support`: `40`
- `high_lateral_velocity`: `6`
- `single_contact_pattern_dominates`: `5`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p72_hrb0p06_hra0p08_hrphm1p5708_hb0_h0p04_kb0p04_k0p14_ab0_a0p01_ph0_ld0p32_ls1 | 0 | seed_002 | -0.2817 | -0.2806 | 0.0045 | 0.0043 | 0.0590 | 87.0000 | 19 | 0.0051 | `low_forward_velocity` |
| primitive_p0p56_hrb0p04_hra0p08_hrph1p5708_hb0p02_h0p025_kb0p02_k0p14_ab0_am0p00625_ph1p5708_ld0p4_ls0p75 | 0 | seed_000 | -0.2834 | -0.2830 | 0.0041 | 0.0064 | 0.1138 | 91.0000 | 13 | 0.0061 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p64_hrb0p04_hra0p08_hrph0_hb0_h0p04_kb0p02_k0p14_ab0_a0p01_ph1p5708_ld0p32_ls0p75 | 0 | seed_000 | -0.2865 | -0.2694 | 0.0038 | 0.0075 | 0.0963 | 88.0000 | 13 | 0.0039 | `low_forward_velocity` |
| primitive_p0p56_hrb0p04_hra0p08_hrph0_hb0_h0p04_kb0p02_k0p14_ab0_a0_ph0_ld0p32_ls0p75 | 0 | seed_000 | -0.2880 | -0.2768 | 0.0036 | 0.0060 | 0.0964 | 82.0000 | 21 | 0.0047 | `low_forward_velocity` |
| primitive_p0p48_hrb0p06_hra0p08_hrphm1p5708_hb0_h0p04_kb0p04_k0p1_ab0_a0p01_ph1p5708_ld0p4_ls1 | 0 | seed_000 | -0.2894 | -0.2765 | 0.0034 | 0.0063 | 0.1027 | 88.0000 | 13 | 0.0040 | `low_forward_velocity` |
| primitive_p0p48_hrb0p06_hra0p08_hrph0_hb0_h0p025_kb0p02_k0p1_ab0_a0p00625_ph1p5708_ld0p4_ls1 | 0 | seed_000 | -0.2961 | -0.2886 | 0.0027 | 0.0043 | 0.0754 | 86.0000 | 19 | 0.0046 | `low_forward_velocity` |
| primitive_p0p64_hrb0p06_hra0p08_hrph1p5708_hb0_h0p04_kb0p02_k0p1_ab0_a0p01_ph0p7854_ld0p4_ls0p75 | 0 | seed_002 | -0.3001 | -0.2988 | 0.0025 | 0.0022 | 0.0942 | 90.0000 | 12 | 0.0042 | `low_forward_velocity` |
| primitive_p0p64_hrb0p04_hra0p06_hrph0_hb0p02_h0p025_kb0p02_k0p14_ab0_am0p00625_ph0_ld0p4_ls0p75 | 0 | seed_000 | -0.3046 | -0.2894 | 0.0017 | 0.0051 | 0.1103 | 90.0000 | 9 | 0.0054 | `low_forward_velocity` |
| primitive_p0p72_hrb0p04_hra0p08_hrphm1p5708_hb0_h0p025_kb0p04_k0p14_ab0_am0p00625_ph0_ld0p24_ls1 | 0 | seed_002 | -0.3047 | -0.2955 | 0.0037 | 0.0069 | 0.1258 | 86.0000 | 12 | 0.0039 | `high_lateral_velocity, low_forward_velocity` |
| primitive_p0p72_hrb0p02_hra0p08_hrph1p5708_hb0p02_h0p025_kb0p04_k0p14_ab0_am0p00625_ph0p7854_ld0p24_ls1 | 0 | seed_000 | -0.3048 | -0.2750 | 0.0017 | 0.0083 | 0.0627 | 85.0000 | 15 | 0.0037 | `low_forward_velocity` |
| primitive_p0p56_hrb0p02_hra0p08_hrph1p5708_hb0p02_h0p025_kb0p02_k0p1_ab0_a0p00625_ph0_ld0p4_ls0p75 | 0 | seed_000 | -0.3082 | -0.2889 | 0.0013 | 0.0056 | 0.0878 | 87.0000 | 13 | 0.0039 | `low_forward_velocity` |
| primitive_p0p72_hrb0p04_hra0p06_hrph0_hb0_h0p04_kb0p04_k0p14_ab0_am0p01_ph1p5708_ld0p4_ls1 | 0 | seed_000 | -0.3119 | -0.3060 | 0.0009 | 0.0022 | 0.0877 | 89.0000 | 11 | 0.0059 | `low_forward_velocity` |
| primitive_p0p48_hrb0p06_hra0p08_hrphm1p5708_hb0p02_h0p04_kb0p02_k0p1_ab0_a0p01_ph1p5708_ld0p32_ls0p75 | 0 | seed_000 | -0.3137 | -0.2934 | 0.0007 | 0.0052 | 0.0636 | 90.0000 | 16 | 0.0036 | `low_forward_velocity` |
| primitive_p0p72_hrb0p04_hra0p08_hrph1p5708_hb0_h0p04_kb0p02_k0p14_ab0_am0p01_ph0p7854_ld0p4_ls1 | 0 | seed_000 | -0.3159 | -0.3146 | 0.0027 | 0.0052 | 0.0709 | 92.0000 | 9 | 0.0044 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p56_hrb0p04_hra0p08_hrph0_hb0p02_h0p025_kb0p04_k0p1_ab0_a0p00625_ph0_ld0p24_ls1 | 0 | seed_000 | -0.3174 | -0.2950 | 0.0016 | 0.0053 | 0.0687 | 85.0000 | 20 | 0.0050 | `low_forward_velocity` |
| primitive_p0p56_hrb0p04_hra0p06_hrph0_hb0p02_h0p04_kb0p02_k0p14_ab0_am0p01_ph0_ld0p4_ls0p75 | 0 | seed_002 | -0.3179 | -0.3025 | 0.0036 | 0.0091 | 0.1089 | 93.0000 | 7 | 0.0054 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p64_hrb0p06_hra0p08_hrphm1p5708_hb0_h0p025_kb0p02_k0p14_ab0_a0_ph1p5708_ld0p32_ls1 | 0 | seed_000 | -0.3187 | -0.2834 | 0.0001 | 0.0080 | 0.0746 | 83.0000 | 27 | 0.0047 | `low_forward_velocity` |
| primitive_p0p48_hrb0p04_hra0p08_hrph0_hb0p02_h0p04_kb0p02_k0p1_ab0_am0p01_ph0_ld0p4_ls1 | 0 | seed_000 | -0.3231 | -0.3108 | -0.0004 | 0.0024 | 0.1005 | 70.0000 | 32 | 0.0065 | `low_forward_velocity` |
| primitive_p0p56_hrb0p04_hra0p06_hrphm1p5708_hb0_h0p04_kb0p02_k0p14_ab0_a0p01_ph0p7854_ld0p32_ls0p75 | 0 | seed_000 | -0.3232 | -0.2995 | 0.0041 | 0.0071 | 0.0702 | 91.0000 | 8 | 0.0043 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p72_hrb0p02_hra0p06_hrph0_hb0_h0p04_kb0p02_k0p14_ab0_a0_ph0p7854_ld0p24_ls0p75 | 0 | seed_000 | -0.3268 | -0.3111 | -0.0008 | 0.0027 | 0.1047 | 90.0000 | 11 | 0.0048 | `low_forward_velocity` |
| primitive_p0p72_hrb0p06_hra0p08_hrph0_hb0_h0p025_kb0p02_k0p1_ab0_a0p00625_ph0_ld0p32_ls0p75 | 0 | seed_000 | -0.3291 | -0.3070 | -0.0011 | 0.0039 | 0.0808 | 85.0000 | 17 | 0.0044 | `low_forward_velocity` |
| primitive_p0p48_hrb0p06_hra0p04_hrphm1p5708_hb0_h0p04_kb0p04_k0p1_ab0_am0p01_ph1p5708_ld0p4_ls1 | 0 | seed_002 | -0.3407 | -0.3245 | 0.0035 | 0.0066 | 0.1145 | 93.0000 | 7 | 0.0050 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p56_hrb0p02_hra0p08_hrphm1p5708_hb0p02_h0p04_kb0p04_k0p14_ab0_am0p01_ph1p5708_ld0p32_ls0p75 | 0 | seed_000 | -0.3415 | -0.3012 | 0.0021 | 0.0066 | 0.1064 | 81.0000 | 19 | 0.0053 | `low_forward_velocity` |
| primitive_p0p64_hrb0p04_hra0p06_hrphm1p5708_hb0p02_h0p025_kb0p02_k0p1_ab0_a0p00625_ph0p7854_ld0p24_ls1 | 0 | seed_000 | -0.3427 | -0.3232 | -0.0003 | 0.0040 | 0.1030 | 91.0000 | 7 | 0.0049 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p64_hrb0p04_hra0p06_hrphm1p5708_hb0p02_h0p04_kb0p02_k0p14_ab0_a0_ph1p5708_ld0p32_ls0p75 | 0 | seed_002 | -0.3446 | -0.3086 | 0.0053 | 0.0062 | 0.0756 | 93.0000 | 9 | 0.0055 | `double_support_dominates, low_forward_velocity, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
