# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `360`
- mode_count: `180`
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
- `low_forward_velocity`: `151`
- `low_base_height`: `80`
- `high_body_pitch`: `34`
- `missing_seed_trace_or_window`: `24`
- `single_contact_pattern_dominates`: `9`
- `short_done_margin`: `6`
- `high_lateral_velocity`: `4`

### seed_002
- `low_forward_velocity`: `153`
- `single_contact_pattern_dominates`: `101`
- `low_base_height`: `82`
- `high_body_pitch`: `31`
- `missing_seed_trace_or_window`: `19`
- `too_few_contact_transitions`: `19`
- `high_lateral_velocity`: `11`
- `short_done_margin`: `8`
- `done_inside_window`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p52_hrb0_hra0p044_hrphm1p05_hb0p08_h0p048_kb0p06_k0p2_ab0p04_a0_ph0p34_ld0p3_ls0p55 | 0 | seed_000 | -0.1442 | -0.1211 | 0.0206 | 0.0256 | 0.1169 | 94.0000 | 7 | 0.0135 | `low_base_height, low_forward_velocity` |
| primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p042_kb0p06_k0p2_ab0p04_a0p00336_ph0p34_ld0p3_ls0p75 | 0 | seed_002 | -0.1457 | -0.1342 | 0.0219 | 0.0242 | 0.1044 | 97.0000 | 3 | 0.0154 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p036_hrphm1p05_hb0p08_h0p054_kb0p06_k0p2_ab0p04_a0p00432_ph0p37_ld0p24_ls0p55 | 0 | seed_000 | -0.1467 | -0.1342 | 0.0193 | 0.0271 | 0.1139 | 96.0000 | 5 | 0.0148 | `high_body_pitch, low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p036_hrphm0p52_hb0p08_h0p048_kb0p06_k0p22_ab0p04_a0p00576_ph0p37_ld0p3_ls0p65 | 0 | seed_002 | -0.1469 | -0.1434 | 0.0200 | 0.0237 | 0.1116 | 97.0000 | 3 | 0.0128 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p22_ab0p04_a0p00336_ph0p47_ld0p24_ls0p65 | 0 | seed_000 | -0.1473 | -0.1317 | 0.0192 | 0.0228 | 0.1126 | 95.0000 | 5 | 0.0136 | `low_base_height, low_forward_velocity` |
| primitive_p0p52_hrb0_hra0p044_hrphm1p05_hb0p08_h0p042_kb0p06_k0p2_ab0p04_a0p00336_ph0p42_ld0p36_ls0p65 | 0 | seed_000 | -0.1478 | -0.1338 | 0.0196 | 0.0229 | 0.1148 | 95.0000 | 7 | 0.0135 | `low_base_height, low_forward_velocity` |
| primitive_p0p46_hrb0_hra0p044_hrph0p7854_hb0p08_h0p042_kb0p06_k0p22_ab0p04_a0_ph0p42_ld0p24_ls0p75 | 0 | seed_000 | -0.1527 | -0.1450 | 0.0189 | 0.0206 | 0.1046 | 95.0000 | 7 | 0.0153 | `low_base_height, low_forward_velocity` |
| primitive_p0p52_hrb0_hra0p044_hrphm1p05_hb0p08_h0p054_kb0p06_k0p22_ab0p04_a0p00432_ph0p37_ld0p3_ls0p75 | 0 | seed_002 | -0.1536 | -0.1512 | 0.0190 | 0.0229 | 0.1156 | 97.0000 | 3 | 0.0127 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p044_hrph0_hb0p08_h0p042_kb0p06_k0p2_ab0p04_a0p00336_ph0p42_ld0p24_ls0p75 | 0 | seed_000 | -0.1545 | -0.1487 | 0.0184 | 0.0219 | 0.1083 | 96.0000 | 5 | 0.0123 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p044_hrph0_hb0p08_h0p042_kb0p06_k0p2_ab0p04_a0p00336_ph0p37_ld0p24_ls0p65 | 0 | seed_000 | -0.1566 | -0.1403 | 0.0182 | 0.0218 | 0.1084 | 95.0000 | 7 | 0.0120 | `low_forward_velocity` |
| primitive_p0p5_hrb0_hra0p036_hrphm0p52_hb0p08_h0p048_kb0p06_k0p2_ab0p04_a0p00576_ph0p42_ld0p3_ls0p75 | 0 | seed_000 | -0.1601 | -0.1541 | 0.0178 | 0.0213 | 0.1122 | 96.0000 | 5 | 0.0126 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p044_hrphm1p05_hb0p08_h0p048_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p36_ls0p75 | 0 | seed_000 | -0.1603 | -0.1441 | 0.0182 | 0.0216 | 0.1153 | 95.0000 | 7 | 0.0131 | `low_base_height, low_forward_velocity` |
| primitive_p0p52_hrb0_hra0p036_hrphm0p52_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p42_ld0p3_ls0p65 | 0 | seed_000 | -0.1612 | -0.1516 | 0.0176 | 0.0220 | 0.1117 | 96.0000 | 3 | 0.0121 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p036_hrphm1p05_hb0p08_h0p054_kb0p06_k0p2_ab0p04_a0_ph0p47_ld0p36_ls0p65 | 0 | seed_002 | -0.1612 | -0.1488 | 0.0205 | 0.0230 | 0.1139 | 97.0000 | 3 | 0.0142 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p46_hrb0_hra0p052_hrph0p7854_hb0p08_h0p054_kb0p06_k0p2_ab0p04_a0p00432_ph0p34_ld0p3_ls0p75 | 0 | seed_000 | -0.1613 | -0.1573 | 0.0182 | 0.0210 | 0.1037 | 96.0000 | 3 | 0.0158 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p052_hrph0p7854_hb0p08_h0p048_kb0p06_k0p2_ab0p04_a0p00576_ph0p42_ld0p24_ls0p55 | 0 | seed_000 | -0.1615 | -0.1491 | 0.0227 | 0.0285 | 0.1035 | 95.0000 | 7 | 0.0169 | `high_body_pitch, low_base_height, low_forward_velocity` |
| primitive_p0p5_hrb0_hra0p052_hrph0_hb0p08_h0p048_kb0p06_k0p2_ab0p04_a0_ph0p47_ld0p3_ls0p65 | 0 | seed_000 | -0.1617 | -0.1474 | 0.0176 | 0.0208 | 0.1075 | 93.0000 | 7 | 0.0124 | `low_forward_velocity` |
| primitive_p0p48_hrb0_hra0p036_hrphm1p05_hb0p08_h0p048_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p36_ls0p75 | 0 | seed_000 | -0.1629 | -0.1585 | 0.0175 | 0.0207 | 0.1137 | 96.0000 | 5 | 0.0133 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p036_hrph0_hb0p08_h0p048_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p75 | 0 | seed_002 | -0.1632 | -0.1579 | 0.0186 | 0.0219 | 0.1093 | 97.0000 | 3 | 0.0126 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p036_hrphm1p05_hb0p08_h0p054_kb0p06_k0p2_ab0p04_a0p00648_ph0p37_ld0p24_ls0p55 | 0 | seed_000 | -0.1639 | -0.1558 | 0.0174 | 0.0220 | 0.1140 | 96.0000 | 5 | 0.0139 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p036_hrphm0p52_hb0p08_h0p048_kb0p06_k0p22_ab0p04_a0p00384_ph0p42_ld0p36_ls0p65 | 0 | seed_000 | -0.1654 | -0.1633 | 0.0184 | 0.0228 | 0.1118 | 97.0000 | 3 | 0.0138 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p044_hrphm0p52_hb0p08_h0p054_kb0p06_k0p18_ab0p04_a0p00432_ph0p34_ld0p36_ls0p75 | 0 | seed_000 | -0.1662 | -0.1446 | 0.0171 | 0.0219 | 0.1128 | 95.0000 | 7 | 0.0124 | `low_forward_velocity` |
| primitive_p0p52_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p048_kb0p06_k0p18_ab0p04_a0p00384_ph0p42_ld0p36_ls0p55 | 0 | seed_002 | -0.1674 | -0.1656 | 0.0182 | 0.0219 | 0.1130 | 97.0000 | 3 | 0.0133 | `low_base_height, low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p052_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p2_ab0p04_a0_ph0p42_ld0p36_ls0p75 | 0 | seed_000 | -0.1676 | -0.1548 | 0.0174 | 0.0220 | 0.1134 | 96.0000 | 5 | 0.0120 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p46_hrb0_hra0p036_hrphm1p05_hb0p08_h0p054_kb0p06_k0p22_ab0p04_a0p00648_ph0p47_ld0p36_ls0p75 | 0 | seed_000 | -0.1679 | -0.1591 | 0.0191 | 0.0195 | 0.1141 | 95.0000 | 7 | 0.0143 | `low_base_height, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
