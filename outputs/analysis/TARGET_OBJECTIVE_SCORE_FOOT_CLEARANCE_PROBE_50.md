# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `96`
- mode_count: `48`
- robust_mode_count: `0`
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
- `too_few_contact_transitions`: `25`
- `high_lateral_velocity`: `19`
- `short_done_margin`: `13`
- `high_body_pitch`: `12`
- `low_forward_velocity`: `10`
- `low_base_height`: `7`
- `single_contact_pattern_dominates`: `5`

### seed_002
- `single_contact_pattern_dominates`: `48`
- `too_few_contact_transitions`: `48`
- `short_done_margin`: `14`
- `high_body_pitch`: `5`
- `low_base_height`: `5`
- `low_forward_velocity`: `3`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65 | 1 | seed_002 | -0.0965 | -0.0245 | 0.0475 | 0.0565 | 0.1166 | 98.0000 | 2 | 0.0159 | `high_body_pitch, short_done_margin, single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p22_ls0p65 | 1 | seed_002 | -0.1020 | -0.0276 | 0.0468 | 0.0580 | 0.0646 | 100.0000 | 0 | 0.0146 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0_ph0p3927_ld0p16_ls0p65 | 1 | seed_002 | -0.1049 | -0.0293 | 0.0463 | 0.0551 | 0.1021 | 100.0000 | 0 | 0.0154 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p0105_ph0p3927_ld0p22_ls0p65 | 1 | seed_002 | -0.2220 | -0.0855 | 0.0510 | 0.0580 | 0.1030 | 100.0000 | 0 | 0.0161 | `short_done_margin, single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p22_ls1 | 0 | seed_002 | -0.0348 | -0.0256 | 0.0382 | 0.0452 | 0.1163 | 98.0000 | 2 | 0.0127 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p16_ls0p65 | 0 | seed_002 | -0.1032 | -0.0324 | 0.0548 | 0.0568 | 0.0821 | 100.0000 | 0 | 0.0149 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p3927_ld0p16_ls0p65 | 0 | seed_002 | -0.1049 | -0.0454 | 0.0540 | 0.0551 | 0.0548 | 100.0000 | 0 | 0.0137 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p06_a0p0075_ph0p47_ld0p3_ls0p65 | 0 | seed_002 | -0.1065 | -0.0463 | 0.0538 | 0.0535 | 0.0498 | 100.0000 | 0 | 0.0139 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p0105_ph0p47_ld0p22_ls0p65 | 0 | seed_002 | -0.1084 | -0.0470 | 0.0544 | 0.0516 | 0.0483 | 100.0000 | 0 | 0.0135 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p3_ls0p65 | 0 | seed_002 | -0.1094 | -0.0510 | 0.0474 | 0.0506 | 0.0700 | 100.0000 | 0 | 0.0135 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p16_ls0p65 | 0 | seed_002 | -0.1100 | -0.0421 | 0.0457 | 0.0500 | 0.0718 | 100.0000 | 0 | 0.0132 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p00375_ph0p3927_ld0p3_ls0p65 | 0 | seed_002 | -0.1113 | -0.0520 | 0.0473 | 0.0487 | 0.0718 | 100.0000 | 0 | 0.0130 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p00525_ph0p32_ld0p22_ls1 | 0 | seed_002 | -0.1117 | -0.0515 | 0.0486 | 0.0483 | 0.0861 | 100.0000 | 0 | 0.0136 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p32_ld0p16_ls1 | 0 | seed_002 | -0.1117 | -0.0521 | 0.0558 | 0.0483 | 0.0923 | 100.0000 | 0 | 0.0105 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p16_ls1 | 0 | seed_002 | -0.1119 | -0.0521 | 0.0477 | 0.0481 | 0.0929 | 100.0000 | 0 | 0.0132 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p00375_ph0p47_ld0p16_ls1 | 0 | seed_002 | -0.1119 | -0.0489 | 0.0542 | 0.0481 | 0.0883 | 100.0000 | 0 | 0.0110 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0p00525_ph0p3927_ld0p16_ls1 | 0 | seed_002 | -0.1120 | -0.0514 | 0.0491 | 0.0480 | 0.0925 | 100.0000 | 0 | 0.0134 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p22_ls0p65 | 0 | seed_002 | -0.1123 | -0.0524 | 0.0476 | 0.0477 | 0.0748 | 100.0000 | 0 | 0.0126 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0p00525_ph0p47_ld0p16_ls1 | 0 | seed_002 | -0.1124 | -0.0530 | 0.0463 | 0.0476 | 0.0948 | 100.0000 | 0 | 0.0130 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p3927_ld0p22_ls1 | 0 | seed_002 | -0.1140 | -0.0646 | 0.0383 | 0.0460 | 0.0715 | 100.0000 | 0 | 0.0127 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p0105_ph0p3927_ld0p16_ls0p65 | 0 | seed_002 | -0.1148 | -0.0394 | 0.0421 | 0.0452 | 0.0610 | 100.0000 | 0 | 0.0131 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p22_ls0p65 | 0 | seed_002 | -0.1149 | -0.0487 | 0.0413 | 0.0451 | 0.0467 | 100.0000 | 0 | 0.0118 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00525_ph0p47_ld0p16_ls0p65 | 0 | seed_002 | -0.1157 | -0.0496 | 0.0399 | 0.0443 | 0.0603 | 100.0000 | 0 | 0.0128 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65 | 0 | seed_002 | -0.1158 | -0.0706 | 0.0392 | 0.0442 | 0.0534 | 100.0000 | 0 | 0.0112 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1 | 0 | seed_002 | -0.1160 | -0.0563 | 0.0434 | 0.0440 | 0.0712 | 100.0000 | 0 | 0.0123 | `single_contact_pattern_dominates, too_few_contact_transitions` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
