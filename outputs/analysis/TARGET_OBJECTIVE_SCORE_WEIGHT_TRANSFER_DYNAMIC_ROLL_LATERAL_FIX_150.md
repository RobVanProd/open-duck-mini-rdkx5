# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `320`
- mode_count: `160`
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
- `double_support_dominates`: `153`
- `low_forward_velocity`: `153`
- `too_little_single_support`: `153`
- `single_contact_pattern_dominates`: `137`
- `single_support_not_balanced`: `135`
- `missing_seed_trace_or_window`: `7`
- `low_base_height`: `5`

### seed_002
- `double_support_dominates`: `159`
- `low_forward_velocity`: `159`
- `too_little_single_support`: `159`
- `single_support_not_balanced`: `158`
- `single_contact_pattern_dominates`: `157`
- `too_few_contact_transitions`: `17`
- `low_base_height`: `6`
- `high_body_pitch`: `1`
- `missing_seed_trace_or_window`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55 | 0 | seed_000 | -0.4163 | -0.4123 | 0.0093 | 0.0117 | 0.0736 | 95.3333 | 7 | 0.0106 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p42_ld0p36_ls0p65 | 0 | seed_002 | -0.4212 | -0.3585 | 0.0132 | 0.0147 | 0.0567 | 96.0000 | 7 | 0.0117 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p58_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p3_ls0p65 | 0 | seed_000 | -0.4259 | -0.4160 | 0.0097 | 0.0119 | 0.0696 | 95.3333 | 7 | 0.0110 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p3_ls1 | 0 | seed_002 | -0.4323 | -0.4243 | 0.0093 | 0.0120 | 0.0919 | 96.0000 | 7 | 0.0107 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p048_hrphm0p52_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p24_ls0p55 | 0 | seed_002 | -0.4445 | -0.4121 | 0.0097 | 0.0121 | 0.0548 | 96.0000 | 5 | 0.0099 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p75 | 0 | seed_000 | -0.4516 | -0.4424 | 0.0128 | 0.0148 | 0.0650 | 96.0000 | 5 | 0.0121 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p34_ld0p24_ls0p55 | 0 | seed_000 | -0.4662 | -0.4503 | 0.0112 | 0.0132 | 0.0764 | 96.0000 | 7 | 0.0117 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p34_ld0p3_ls0p75 | 0 | seed_002 | -0.4665 | -0.4353 | 0.0121 | 0.0141 | 0.0586 | 96.6667 | 7 | 0.0120 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p5_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p42_ld0p3_ls1 | 0 | seed_002 | -0.4674 | -0.4159 | 0.0114 | 0.0140 | 0.0856 | 96.6667 | 5 | 0.0118 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0063_ph0p42_ld0p36_ls1 | 0 | seed_002 | -0.4693 | -0.4396 | 0.0130 | 0.0153 | 0.0768 | 96.6667 | 7 | 0.0125 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p36_ls0p65 | 0 | seed_002 | -0.4709 | -0.4629 | 0.0124 | 0.0151 | 0.0761 | 96.6667 | 5 | 0.0105 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p24_ls0p55 | 0 | seed_002 | -0.4713 | -0.4411 | 0.0114 | 0.0136 | 0.0677 | 96.6667 | 6 | 0.0110 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p54_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p3_ls0p65 | 0 | seed_002 | -0.4750 | -0.4517 | 0.0109 | 0.0132 | 0.0574 | 96.6667 | 7 | 0.0104 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p24_ls0p65 | 0 | seed_002 | -0.4766 | -0.4223 | 0.0110 | 0.0130 | 0.0456 | 96.6667 | 7 | 0.0117 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p75 | 0 | seed_002 | -0.4768 | -0.4495 | 0.0101 | 0.0129 | 0.0607 | 96.6667 | 5 | 0.0106 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p36_ls0p65 | 0 | seed_002 | -0.4781 | -0.4424 | 0.0118 | 0.0143 | 0.0612 | 96.6667 | 5 | 0.0115 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p5_hrb0_hra0p032_hrphm0p68_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p36_ls0p55 | 0 | seed_002 | -0.4781 | -0.4490 | 0.0104 | 0.0128 | 0.0599 | 96.6667 | 5 | 0.0109 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p3927_ld0p24_ls0p75 | 0 | seed_000 | -0.4808 | -0.4763 | 0.0110 | 0.0135 | 0.0811 | 96.6667 | 5 | 0.0116 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p42_ld0p24_ls0p55 | 0 | seed_002 | -0.4837 | -0.4478 | 0.0113 | 0.0137 | 0.0737 | 96.6667 | 7 | 0.0117 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p37_ld0p36_ls0p55 | 0 | seed_002 | -0.4847 | -0.4761 | 0.0119 | 0.0140 | 0.0679 | 96.6667 | 7 | 0.0125 | `double_support_dominates, low_base_height, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p42_ld0p3_ls1 | 0 | seed_002 | -0.4850 | -0.4773 | 0.0093 | 0.0120 | 0.0789 | 96.6667 | 5 | 0.0116 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p5_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p0064_ph0p37_ld0p24_ls1 | 0 | seed_002 | -0.4873 | -0.4764 | 0.0098 | 0.0118 | 0.0810 | 96.6667 | 5 | 0.0120 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p34_ld0p24_ls0p55 | 0 | seed_002 | -0.4896 | -0.4002 | 0.0143 | 0.0160 | 0.0699 | 97.3333 | 5 | 0.0134 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p34_ld0p24_ls1 | 0 | seed_002 | -0.4898 | -0.4583 | 0.0081 | 0.0115 | 0.0809 | 96.6667 | 5 | 0.0107 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p37_ld0p36_ls0p75 | 0 | seed_000 | -0.4919 | -0.4728 | 0.0128 | 0.0155 | 0.0661 | 96.6667 | 5 | 0.0120 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
