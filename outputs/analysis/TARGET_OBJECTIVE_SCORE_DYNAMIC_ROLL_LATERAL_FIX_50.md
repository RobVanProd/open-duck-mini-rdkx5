# Target Objective Score

status: `PASS_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `320`
- mode_count: `160`
- robust_mode_count: `2`
- required_seeds: `[0, 2]`
- window_samples: `50`

## Criteria

- min_mean_vx: `0.04`
- max_vy_abs_p95: `0.12`
- max_contact_dominance_pct: `95.0`
- max_pitch_abs_p95: `0.35`
- min_base_height: `0.145`
- max_sent_velocity_p95: `2.5`
- max_tracking_p95: `0.12`
- min_done_margin: `50`
- min_contact_transitions: `3`
- min_foot_site_z_p95: `-1.0`

## Seed Failure Counts

### seed_000
- `low_forward_velocity`: `76`
- `high_lateral_velocity`: `35`
- `too_few_contact_transitions`: `12`
- `low_base_height`: `8`
- `high_body_pitch`: `7`
- `short_done_margin`: `6`
- `single_contact_pattern_dominates`: `2`

### seed_002
- `single_contact_pattern_dominates`: `151`
- `too_few_contact_transitions`: `138`
- `low_forward_velocity`: `67`
- `high_lateral_velocity`: `3`
- `low_base_height`: `1`
- `short_done_margin`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55 | 2 | seed_000 | 0.0416 | 0.0426 | 0.0416 | 0.0437 | 0.0736 | 94.0000 | 4 | 0.0114 | `` |
| primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p24_ls0p65 | 2 | seed_002 | 0.0411 | 0.0417 | 0.0423 | 0.0411 | 0.0431 | 94.0000 | 6 | 0.0118 | `` |
| primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p42_ld0p36_ls0p65 | 1 | seed_002 | 0.0410 | 0.0458 | 0.0517 | 0.0410 | 0.0641 | 94.0000 | 4 | 0.0121 | `` |
| primitive_p0p58_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p3_ls0p65 | 1 | seed_000 | 0.0381 | 0.0416 | 0.0398 | 0.0452 | 0.1086 | 94.0000 | 4 | 0.0129 | `` |
| primitive_p0p58_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p3_ls0p55 | 1 | seed_000 | 0.0372 | 0.0393 | 0.0419 | 0.0415 | 0.1061 | 94.0000 | 4 | 0.0112 | `` |
| primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p34_ld0p24_ls0p55 | 1 | seed_002 | 0.0264 | 0.0347 | 0.0430 | 0.0464 | 0.0650 | 96.0000 | 4 | 0.0134 | `single_contact_pattern_dominates` |
| primitive_p0p58_hrb0_hra0p048_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p42_ld0p24_ls0p55 | 1 | seed_002 | 0.0257 | 0.0346 | 0.0434 | 0.0457 | 0.0730 | 96.0000 | 4 | 0.0120 | `single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p37_ld0p36_ls0p55 | 1 | seed_002 | 0.0253 | 0.0358 | 0.0462 | 0.0453 | 0.0679 | 96.0000 | 4 | 0.0130 | `single_contact_pattern_dominates` |
| primitive_p0p58_hrb0_hra0p032_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p3_ls0p65 | 1 | seed_002 | 0.0250 | 0.0343 | 0.0435 | 0.0450 | 0.1048 | 96.0000 | 4 | 0.0131 | `single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p42_ld0p24_ls0p55 | 1 | seed_002 | 0.0242 | 0.0333 | 0.0424 | 0.0442 | 0.0737 | 96.0000 | 4 | 0.0126 | `single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p75 | 1 | seed_002 | 0.0235 | 0.0318 | 0.0401 | 0.0435 | 0.0910 | 94.0000 | 2 | 0.0128 | `too_few_contact_transitions` |
| primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p34_ld0p3_ls0p75 | 1 | seed_002 | 0.0227 | 0.0383 | 0.0540 | 0.0427 | 0.0773 | 96.0000 | 4 | 0.0124 | `single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p36_ls1 | 1 | seed_002 | 0.0222 | 0.0322 | 0.0423 | 0.0422 | 0.0956 | 96.0000 | 4 | 0.0127 | `single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p3_ls0p65 | 1 | seed_002 | 0.0117 | 0.0263 | 0.0409 | 0.0391 | 0.0671 | 96.0000 | 4 | 0.0107 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p42_ld0p3_ls0p75 | 1 | seed_000 | 0.0075 | 0.0246 | 0.0364 | 0.0416 | 0.1119 | 92.0000 | 6 | 0.0124 | `` |
| primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p36_ls0p65 | 1 | seed_002 | 0.0029 | 0.0235 | 0.0441 | 0.0429 | 0.0687 | 96.0000 | 2 | 0.0118 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p3927_ld0p36_ls0p55 | 1 | seed_002 | -0.0119 | 0.0180 | 0.0480 | 0.0581 | 0.0911 | 96.0000 | 4 | 0.0156 | `short_done_margin, single_contact_pattern_dominates` |
| primitive_p0p58_hrb0_hra0p036_hrphm0p52_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p42_ld0p24_ls0p75 | 1 | seed_002 | -0.0180 | 0.0121 | 0.0422 | 0.0370 | 0.1213 | 96.0000 | 4 | 0.0105 | `high_lateral_velocity, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p58_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p42_ld0p3_ls0p55 | 1 | seed_002 | -0.0286 | 0.0075 | 0.0436 | 0.0514 | 0.1065 | 98.0000 | 2 | 0.0146 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p54_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0063_ph0p37_ld0p3_ls0p65 | 1 | seed_002 | -0.0301 | 0.0084 | 0.0469 | 0.0499 | 0.0778 | 98.0000 | 2 | 0.0143 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p65 | 1 | seed_002 | -0.0306 | 0.0107 | 0.0521 | 0.0494 | 0.0673 | 98.0000 | 2 | 0.0134 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p58_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p47_ld0p36_ls0p75 | 1 | seed_002 | -0.0350 | 0.0049 | 0.0447 | 0.0450 | 0.0829 | 98.0000 | 2 | 0.0121 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p58_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p37_ld0p24_ls1 | 1 | seed_002 | -0.0365 | 0.0048 | 0.0461 | 0.0435 | 0.0889 | 98.0000 | 2 | 0.0139 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p5_hrb0_hra0p04_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p42_ld0p24_ls0p75 | 1 | seed_002 | -0.0367 | 0.0022 | 0.0411 | 0.0433 | 0.0799 | 98.0000 | 2 | 0.0131 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p58_hrb0_hra0p044_hrphm0p9_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p42_ld0p36_ls1 | 1 | seed_002 | -0.0371 | 0.0022 | 0.0416 | 0.0429 | 0.0950 | 98.0000 | 2 | 0.0127 | `single_contact_pattern_dominates, too_few_contact_transitions` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
