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
- `single_contact_pattern_dominates`: `22`
- `low_base_height`: `6`
- `missing_seed_trace_or_window`: `6`
- `high_body_pitch`: `1`
- `high_lateral_velocity`: `1`
- `short_done_margin`: `1`

### seed_002
- `low_forward_velocity`: `159`
- `single_contact_pattern_dominates`: `126`
- `too_few_contact_transitions`: `26`
- `high_lateral_velocity`: `10`
- `low_base_height`: `7`
- `high_body_pitch`: `2`
- `done_inside_window`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p34_ld0p24_ls0p55 | 0 | seed_000 | -0.1297 | -0.1280 | 0.0211 | 0.0238 | 0.1042 | 96.0000 | 5 | 0.0137 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p34_ld0p3_ls0p75 | 0 | seed_000 | -0.1368 | -0.1286 | 0.0204 | 0.0222 | 0.1078 | 95.0000 | 7 | 0.0124 | `low_forward_velocity` |
| primitive_p0p54_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0063_ph0p37_ld0p3_ls0p65 | 0 | seed_002 | -0.1419 | -0.1339 | 0.0216 | 0.0244 | 0.1039 | 97.0000 | 3 | 0.0148 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p032_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0057_ph0p34_ld0p36_ls0p65 | 0 | seed_000 | -0.1439 | -0.1334 | 0.0196 | 0.0241 | 0.1125 | 96.0000 | 3 | 0.0121 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p0048_ph0p3927_ld0p36_ls0p65 | 0 | seed_002 | -0.1485 | -0.1443 | 0.0200 | 0.0235 | 0.1110 | 97.0000 | 3 | 0.0118 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p032_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65 | 0 | seed_002 | -0.1530 | -0.1513 | 0.0189 | 0.0230 | 0.1133 | 97.0000 | 3 | 0.0113 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p032_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p37_ld0p24_ls0p75 | 0 | seed_000 | -0.1539 | -0.1458 | 0.0185 | 0.0225 | 0.1058 | 96.0000 | 3 | 0.0119 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p36_ls0p65 | 0 | seed_000 | -0.1542 | -0.1337 | 0.0184 | 0.0230 | 0.1128 | 95.0000 | 5 | 0.0118 | `low_forward_velocity` |
| primitive_p0p54_hrb0_hra0p032_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p36_ls0p75 | 0 | seed_002 | -0.1551 | -0.1507 | 0.0193 | 0.0228 | 0.1131 | 97.0000 | 3 | 0.0119 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p47_ld0p36_ls0p55 | 0 | seed_000 | -0.1552 | -0.1475 | 0.0183 | 0.0222 | 0.1109 | 96.0000 | 5 | 0.0114 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p37_ld0p36_ls0p75 | 0 | seed_000 | -0.1561 | -0.1400 | 0.0182 | 0.0218 | 0.1133 | 95.0000 | 5 | 0.0125 | `low_forward_velocity` |
| primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p24_ls0p65 | 0 | seed_000 | -0.1572 | -0.1514 | 0.0181 | 0.0194 | 0.1037 | 95.0000 | 7 | 0.0120 | `low_forward_velocity` |
| primitive_p0p54_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p34_ld0p3_ls0p55 | 0 | seed_002 | -0.1574 | -0.1512 | 0.0194 | 0.0225 | 0.1088 | 97.0000 | 3 | 0.0125 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p36_ls0p75 | 0 | seed_002 | -0.1586 | -0.1517 | 0.0195 | 0.0223 | 0.1224 | 96.0000 | 3 | 0.0125 | `high_lateral_velocity, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p42_ld0p24_ls0p55 | 0 | seed_000 | -0.1588 | -0.1404 | 0.0179 | 0.0220 | 0.1139 | 95.0000 | 7 | 0.0120 | `low_forward_velocity` |
| primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p65 | 0 | seed_002 | -0.1598 | -0.1428 | 0.0216 | 0.0223 | 0.1033 | 97.0000 | 3 | 0.0139 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p37_ld0p36_ls0p55 | 0 | seed_000 | -0.1605 | -0.1433 | 0.0186 | 0.0220 | 0.1124 | 95.0000 | 7 | 0.0130 | `low_base_height, low_forward_velocity` |
| primitive_p0p5_hrb0_hra0p04_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p42_ld0p24_ls0p75 | 0 | seed_002 | -0.1612 | -0.1567 | 0.0186 | 0.0221 | 0.1053 | 97.0000 | 3 | 0.0134 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p36_ls0p75 | 0 | seed_002 | -0.1617 | -0.1556 | 0.0189 | 0.0220 | 0.1087 | 97.0000 | 3 | 0.0122 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p3_ls0p75 | 0 | seed_000 | -0.1618 | -0.1537 | 0.0176 | 0.0216 | 0.1131 | 96.0000 | 5 | 0.0116 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p42_ld0p36_ls0p65 | 0 | seed_000 | -0.1623 | -0.1451 | 0.0176 | 0.0213 | 0.1076 | 94.0000 | 7 | 0.0122 | `low_forward_velocity` |
| primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p34_ld0p36_ls0p65 | 0 | seed_000 | -0.1625 | -0.1611 | 0.0175 | 0.0204 | 0.1115 | 96.0000 | 5 | 0.0143 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0063_ph0p42_ld0p36_ls1 | 0 | seed_000 | -0.1640 | -0.1438 | 0.0173 | 0.0218 | 0.1066 | 95.0000 | 7 | 0.0131 | `low_forward_velocity` |
| primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p3_ls0p65 | 0 | seed_002 | -0.1645 | -0.1527 | 0.0199 | 0.0217 | 0.1060 | 97.0000 | 3 | 0.0139 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p3_ls0p65 | 0 | seed_000 | -0.1649 | -0.1465 | 0.0172 | 0.0213 | 0.1117 | 95.0000 | 7 | 0.0108 | `low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
