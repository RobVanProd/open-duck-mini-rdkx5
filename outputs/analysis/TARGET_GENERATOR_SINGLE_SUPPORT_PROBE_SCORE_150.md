# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `64`
- mode_count: `32`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `150`

## Criteria

- min_mean_vx: `0.04`
- min_forward_displacement_m: `0.006`
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
- `missing_seed_trace_or_window`: `26`
- `double_support_dominates`: `6`
- `low_forward_velocity`: `6`
- `single_contact_pattern_dominates`: `6`
- `single_support_not_balanced`: `6`
- `too_little_single_support`: `6`
- `low_base_height`: `4`

### seed_002
- `missing_seed_trace_or_window`: `23`
- `double_support_dominates`: `9`
- `single_contact_pattern_dominates`: `9`
- `single_support_not_balanced`: `9`
- `too_little_single_support`: `9`
- `low_forward_velocity`: `8`
- `low_base_height`: `4`
- `high_body_pitch`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p37_ld0p24_ls1_sp0p02_sas0p2 | 0 | seed_000 | -1.0765 | -1.0692 | 0.0161 | 0.0483 | 0.0190 | 0.0571 | 0.0776 | 97.3333 | 3 | 0.0153 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p24_ls1_sp0p02_sas0p2 | 0 | seed_000 | -1.0772 | -1.0707 | 0.0159 | 0.0476 | 0.0188 | 0.0564 | 0.0790 | 97.3333 | 3 | 0.0152 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p52_ld0p24_ls1_sp0p02_sas0p2 | 0 | seed_000 | -1.1579 | -1.1115 | 0.0158 | 0.0474 | 0.0187 | 0.0561 | 0.0844 | 97.3333 | 3 | 0.0153 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p52_ld0p24_ls1_sp0p02_sas0p2 | 0 | seed_000 | -1.1590 | -1.1111 | 0.0159 | 0.0478 | 0.0189 | 0.0567 | 0.0837 | 97.3333 | 3 | 0.0154 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p52_ld0p24_ls1_sp0p02_sas0p4 | 0 | seed_002 | -1.4812 | -1.3190 | 0.0162 | 0.0486 | 0.0433 | 0.1298 | 0.1063 | 96.6667 | 5 | 0.0213 | `double_support_dominates, high_body_pitch, low_base_height, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p52_ld0p32_ls1_sp0p02_sas0p2 | 0 | seed_002 | -999.0000 | -500.0115 | 0.0162 | 0.0487 | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p52_ld0p24_ls1_sp0p02_sas0p4 | 0 | seed_000 | -999.0000 | -500.0229 | NA | NA | 0.0187 | 0.0562 | 0.0958 | 96.6667 | 5 | 0.0175 | `double_support_dominates, high_body_pitch, low_base_height, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p24_ls1_sp0p02_sas0p4 | 0 | seed_000 | -999.0000 | -500.0299 | NA | NA | 0.0193 | 0.0579 | 0.0819 | 97.3333 | 3 | 0.0156 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p37_ld0p24_ls1_sp0p02_sas0p4 | 0 | seed_000 | -999.0000 | -500.0304 | NA | NA | 0.0194 | 0.0582 | 0.0800 | 97.3333 | 3 | 0.0159 | `double_support_dominates, low_base_height, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p52_ld0p32_ls1_sp0p02_sas0p4 | 0 | seed_000 | -999.0000 | -500.0581 | NA | NA | 0.0193 | 0.0580 | 0.0849 | 98.0000 | 3 | 0.0166 | `double_support_dominates, low_base_height, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p24_ls1_sp0p04_sas0p2 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p24_ls1_sp0p04_sas0p4 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p32_ls1_sp0p02_sas0p2 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p32_ls1_sp0p02_sas0p4 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p32_ls1_sp0p04_sas0p2 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p32_ls1_sp0p04_sas0p4 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p52_ld0p24_ls1_sp0p04_sas0p2 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p52_ld0p24_ls1_sp0p04_sas0p4 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p52_ld0p32_ls1_sp0p04_sas0p2 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p52_ld0p32_ls1_sp0p04_sas0p4 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p37_ld0p24_ls1_sp0p04_sas0p2 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p37_ld0p24_ls1_sp0p04_sas0p4 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p37_ld0p32_ls1_sp0p02_sas0p2 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p37_ld0p32_ls1_sp0p02_sas0p4 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |
| primitive_p0p65_hrb0_hra0p032_hrphm0p8_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p37_ld0p32_ls1_sp0p04_sas0p2 | 0 | seed_000 | -999.0000 | -999.0000 | NA | NA | NA | NA | NA | NA | NA | NA | `missing_seed_trace_or_window` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
