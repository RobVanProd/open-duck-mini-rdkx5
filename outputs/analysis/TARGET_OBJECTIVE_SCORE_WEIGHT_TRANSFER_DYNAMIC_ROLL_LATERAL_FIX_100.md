# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `320`
- mode_count: `160`
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
- `low_forward_velocity`: `153`
- `double_support_dominates`: `151`
- `too_little_single_support`: `137`
- `single_support_not_balanced`: `101`
- `single_contact_pattern_dominates`: `20`
- `low_base_height`: `6`
- `missing_seed_trace_or_window`: `6`
- `high_lateral_velocity`: `2`
- `high_body_pitch`: `1`
- `short_done_margin`: `1`

### seed_002
- `double_support_dominates`: `159`
- `low_forward_velocity`: `159`
- `too_little_single_support`: `157`
- `single_contact_pattern_dominates`: `112`
- `single_support_not_balanced`: `97`
- `high_lateral_velocity`: `24`
- `too_few_contact_transitions`: `18`
- `low_base_height`: `7`
- `high_body_pitch`: `2`
- `done_inside_window`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p42_ld0p36_ls0p65 | 0 | seed_002 | -0.2479 | -0.2051 | 0.0176 | 0.0213 | 0.1076 | 94.0000 | 7 | 0.0122 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p048_hrphm0p52_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p24_ls0p55 | 0 | seed_002 | -0.2628 | -0.2448 | 0.0148 | 0.0197 | 0.1121 | 94.0000 | 5 | 0.0102 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55 | 0 | seed_000 | -0.2697 | -0.2481 | 0.0145 | 0.0193 | 0.1155 | 93.0000 | 7 | 0.0113 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p3_ls1 | 0 | seed_000 | -0.2795 | -0.2773 | 0.0134 | 0.0183 | 0.1154 | 94.0000 | 7 | 0.0119 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p34_ld0p3_ls0p75 | 0 | seed_002 | -0.2803 | -0.2486 | 0.0204 | 0.0222 | 0.1078 | 95.0000 | 7 | 0.0124 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p54_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p3_ls0p65 | 0 | seed_002 | -0.2881 | -0.2765 | 0.0172 | 0.0213 | 0.1117 | 95.0000 | 7 | 0.0108 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p36_ls0p65 | 0 | seed_002 | -0.2932 | -0.2637 | 0.0184 | 0.0230 | 0.1128 | 95.0000 | 5 | 0.0118 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| primitive_p0p5_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p42_ld0p3_ls1 | 0 | seed_002 | -0.2954 | -0.2571 | 0.0157 | 0.0205 | 0.1134 | 95.0000 | 5 | 0.0124 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p5_hrb0_hra0p032_hrphm0p68_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p36_ls0p55 | 0 | seed_002 | -0.2960 | -0.2756 | 0.0161 | 0.0204 | 0.1132 | 95.0000 | 5 | 0.0112 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p75 | 0 | seed_002 | -0.2980 | -0.2810 | 0.0151 | 0.0202 | 0.1137 | 95.0000 | 5 | 0.0109 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p24_ls0p55 | 0 | seed_002 | -0.3014 | -0.2803 | 0.0157 | 0.0198 | 0.1081 | 95.0000 | 6 | 0.0113 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p42_ld0p24_ls0p55 | 0 | seed_002 | -0.3020 | -0.2704 | 0.0179 | 0.0220 | 0.1139 | 95.0000 | 7 | 0.0120 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p24_ls0p65 | 0 | seed_002 | -0.3055 | -0.2585 | 0.0165 | 0.0194 | 0.1037 | 95.0000 | 7 | 0.0120 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p37_ld0p36_ls0p55 | 0 | seed_002 | -0.3060 | -0.3033 | 0.0186 | 0.0220 | 0.1124 | 95.0000 | 7 | 0.0130 | `double_support_dominates, low_base_height, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p75 | 0 | seed_000 | -0.3062 | -0.2888 | 0.0171 | 0.0210 | 0.1130 | 94.0000 | 5 | 0.0124 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p36_ls0p65 | 0 | seed_000 | -0.3063 | -0.3033 | 0.0171 | 0.0222 | 0.1139 | 95.0000 | 5 | 0.0108 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0063_ph0p42_ld0p36_ls1 | 0 | seed_000 | -0.3070 | -0.3053 | 0.0177 | 0.0218 | 0.1066 | 95.0000 | 7 | 0.0131 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| primitive_p0p5_hrb0_hra0p048_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p37_ld0p36_ls0p65 | 0 | seed_002 | -0.3228 | -0.2652 | 0.0147 | 0.0197 | 0.1126 | 95.0000 | 5 | 0.0112 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| primitive_p0p54_hrb0_hra0p032_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0057_ph0p34_ld0p36_ls0p65 | 0 | seed_002 | -0.3228 | -0.3034 | 0.0196 | 0.0241 | 0.1125 | 96.0000 | 3 | 0.0121 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p34_ld0p24_ls0p55 | 0 | seed_002 | -0.3262 | -0.2380 | 0.0211 | 0.0238 | 0.1042 | 96.0000 | 5 | 0.0137 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0048_ph0p42_ld0p3_ls1 | 0 | seed_002 | -0.3355 | -0.3112 | 0.0126 | 0.0183 | 0.1134 | 95.0000 | 7 | 0.0109 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p37_ld0p36_ls0p75 | 0 | seed_000 | -0.3361 | -0.3100 | 0.0182 | 0.0218 | 0.1133 | 95.0000 | 5 | 0.0125 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p54_hrb0_hra0p048_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p37_ld0p36_ls0p75 | 0 | seed_002 | -0.3381 | -0.2734 | 0.0168 | 0.0224 | 0.1142 | 96.0000 | 5 | 0.0113 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p036_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p47_ld0p36_ls1 | 0 | seed_002 | -0.3479 | -0.3020 | 0.0160 | 0.0213 | 0.1131 | 96.0000 | 3 | 0.0123 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, too_little_single_support` |
| primitive_p0p54_hrb0_hra0p036_hrphm0p68_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55 | 0 | seed_002 | -0.3482 | -0.3097 | 0.0165 | 0.0213 | 0.1096 | 96.0000 | 3 | 0.0112 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
