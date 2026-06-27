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
- min_forward_displacement_m: `0.004`
- max_vy_abs_p95: `0.12`
- max_contact_dominance_pct: `95.0`
- max_double_support_pct: `75.0`
- max_no_support_pct: `100.0`
- min_single_support_pct: `20.0`
- min_each_single_support_pct: `5.0`
- max_pitch_abs_p95: `0.35`
- min_base_height: `0.145`
- max_sent_velocity_p95: `3.75`
- max_tracking_p95: `0.12`
- min_done_margin: `50`
- min_contact_transitions: `2`
- min_foot_site_z_p95: `-1.0`

## Seed Failure Counts

### seed_000
- `missing_seed_trace_or_window`: `21`
- `double_support_dominates`: `11`
- `single_support_not_balanced`: `11`
- `too_little_single_support`: `11`
- `low_base_height`: `9`
- `low_forward_velocity`: `8`
- `high_body_pitch`: `6`
- `short_done_margin`: `5`
- `single_contact_pattern_dominates`: `4`
- `high_lateral_velocity`: `1`

### seed_002
- `double_support_dominates`: `20`
- `single_support_not_balanced`: `20`
- `too_little_single_support`: `20`
- `low_base_height`: `15`
- `high_body_pitch`: `13`
- `missing_seed_trace_or_window`: `12`
- `high_lateral_velocity`: `11`
- `short_done_margin`: `11`
- `low_forward_velocity`: `10`
- `single_contact_pattern_dominates`: `9`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p24_ls1_sp0p02_sas0p2 | 0 | seed_000 | -0.9228 | -0.9122 | 0.0219 | 0.0438 | 0.0265 | 0.0530 | 0.1114 | 96.0000 | 3 | 0.0154 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p37_ld0p24_ls1_sp0p02_sas0p2 | 0 | seed_000 | -0.9230 | -0.9116 | 0.0220 | 0.0441 | 0.0267 | 0.0533 | 0.1114 | 96.0000 | 3 | 0.0157 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p52_ld0p24_ls1_sp0p02_sas0p2 | 0 | seed_000 | -1.0492 | -0.9751 | 0.0215 | 0.0430 | 0.0265 | 0.0531 | 0.1114 | 96.0000 | 3 | 0.0160 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p52_ld0p24_ls1_sp0p02_sas0p4 | 0 | seed_000 | -1.0497 | -1.0254 | 0.0230 | 0.0460 | 0.0318 | 0.0636 | 0.1436 | 95.0000 | 5 | 0.0189 | `double_support_dominates, high_body_pitch, high_lateral_velocity, low_base_height, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p52_ld0p24_ls1_sp0p02_sas0p2 | 0 | seed_000 | -1.0500 | -0.9763 | 0.0211 | 0.0422 | 0.0264 | 0.0527 | 0.1114 | 96.0000 | 3 | 0.0158 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p24_ls1_sp0p02_sas0p4 | 0 | seed_000 | -1.1331 | -1.0150 | 0.0337 | 0.0675 | 0.0270 | 0.0540 | 0.1114 | 96.0000 | 3 | 0.0157 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p52_ld0p32_ls1_sp0p02_sas0p4 | 0 | seed_000 | -1.3201 | -1.1489 | 0.0401 | 0.0802 | 0.0273 | 0.0547 | 0.1119 | 97.0000 | 3 | 0.0171 | `double_support_dominates, low_base_height, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p52_ld0p24_ls1_sp0p02_sas0p4 | 0 | seed_000 | -2.0314 | -1.5256 | 0.0635 | 0.1270 | 0.0303 | 0.0606 | 0.1436 | 95.0000 | 5 | 0.0183 | `double_support_dominates, high_body_pitch, high_lateral_velocity, low_base_height, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p52_ld0p32_ls1_sp0p02_sas0p2 | 0 | seed_002 | -3.1413 | -2.0699 | 0.0304 | 0.0608 | 0.0936 | 0.1871 | 0.1718 | 94.0000 | 6 | 0.0358 | `double_support_dominates, high_body_pitch, high_lateral_velocity, low_base_height, short_done_margin, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p37_ld0p24_ls1_sp0p02_sas0p4 | 0 | seed_000 | -3.2493 | -2.0729 | 0.0925 | 0.1850 | 0.0273 | 0.0546 | 0.1114 | 96.0000 | 3 | 0.0161 | `double_support_dominates, low_base_height, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p52_ld0p32_ls1_sp0p02_sas0p2 | 0 | seed_002 | -3.8837 | -2.3748 | 0.0218 | 0.0437 | 0.1088 | 0.2175 | 0.2054 | 94.0000 | 6 | 0.0393 | `double_support_dominates, high_body_pitch, high_lateral_velocity, low_base_height, short_done_margin, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p37_ld0p32_ls1_sp0p02_sas0p4 | 0 | seed_000 | -999.0000 | -500.1286 | NA | NA | 0.0425 | 0.0851 | 0.1117 | 96.0000 | 3 | 0.0220 | `double_support_dominates, high_body_pitch, low_base_height, short_done_margin, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p32_ls1_sp0p02_sas0p4 | 0 | seed_000 | -999.0000 | -500.1522 | NA | NA | 0.0391 | 0.0782 | 0.1441 | 95.0000 | 5 | 0.0216 | `double_support_dominates, high_body_pitch, high_lateral_velocity, low_base_height, low_forward_velocity, short_done_margin, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p52_ld0p32_ls1_sp0p02_sas0p4 | 0 | seed_000 | -999.0000 | -500.1960 | NA | NA | 0.0434 | 0.0868 | 0.1119 | 97.0000 | 3 | 0.0219 | `double_support_dominates, high_body_pitch, low_base_height, short_done_margin, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p32_ls1_sp0p02_sas0p2 | 0 | seed_000 | -999.0000 | -500.5753 | NA | NA | 0.0676 | 0.1351 | 0.1442 | 95.0000 | 5 | 0.0294 | `double_support_dominates, high_body_pitch, high_lateral_velocity, low_base_height, short_done_margin, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p24_ls1_sp0p04_sas0p2 | 0 | seed_000 | -999.0000 | -501.3513 | NA | NA | 0.1039 | 0.2078 | 0.2118 | 94.0000 | 6 | 0.0387 | `double_support_dominates, high_body_pitch, high_lateral_velocity, low_base_height, short_done_margin, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p37_ld0p32_ls1_sp0p02_sas0p2 | 0 | seed_000 | -999.0000 | -501.5460 | NA | NA | 0.1147 | 0.2294 | 0.2157 | 93.0000 | 9 | 0.0415 | `double_support_dominates, high_body_pitch, high_lateral_velocity, low_base_height, short_done_margin, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p52_ld0p24_ls1_sp0p04_sas0p2 | 0 | seed_000 | -999.0000 | -501.5691 | NA | NA | 0.1157 | 0.2313 | 0.2217 | 93.0000 | 8 | 0.0413 | `double_support_dominates, high_body_pitch, high_lateral_velocity, low_base_height, short_done_margin, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p37_ld0p24_ls1_sp0p04_sas0p2 | 0 | seed_000 | -999.0000 | -501.7897 | NA | NA | 0.1326 | 0.2652 | 0.2251 | 90.0000 | 10 | 0.0467 | `double_support_dominates, high_body_pitch, high_lateral_velocity, low_base_height, short_done_margin, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p52_ld0p24_ls1_sp0p04_sas0p2 | 0 | seed_000 | -999.0000 | -501.8233 | NA | NA | 0.1340 | 0.2680 | 0.2264 | 90.0000 | 9 | 0.0468 | `double_support_dominates, high_body_pitch, high_lateral_velocity, low_base_height, short_done_margin, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p24_ls1_sp0p04_sas0p4 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p32_ls1_sp0p04_sas0p2 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p32_ls1_sp0p04_sas0p4 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p52_ld0p24_ls1_sp0p04_sas0p4 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p52_ld0p32_ls1_sp0p04_sas0p2 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
