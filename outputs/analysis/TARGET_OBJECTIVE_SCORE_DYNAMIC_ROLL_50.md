# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `144`
- mode_count: `72`
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
- `too_few_contact_transitions`: `36`
- `low_forward_velocity`: `28`
- `high_lateral_velocity`: `10`
- `high_body_pitch`: `6`
- `single_contact_pattern_dominates`: `3`
- `low_base_height`: `2`
- `short_done_margin`: `2`

### seed_002
- `single_contact_pattern_dominates`: `70`
- `too_few_contact_transitions`: `68`
- `low_forward_velocity`: `17`
- `high_lateral_velocity`: `5`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65 | 1 | seed_000 | 0.0143 | 0.0280 | 0.0413 | 0.0417 | 0.1110 | 94.0000 | 4 | 0.0123 | `` |
| primitive_p0p52_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p3_ls0p65 | 1 | seed_002 | -0.0347 | 0.0044 | 0.0436 | 0.0453 | 0.0682 | 98.0000 | 2 | 0.0124 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p64_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65 | 1 | seed_002 | -0.1111 | -0.0284 | 0.0543 | 0.0489 | 0.0473 | 100.0000 | 0 | 0.0130 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65 | 1 | seed_002 | -0.1120 | -0.0327 | 0.0466 | 0.0480 | 0.0806 | 100.0000 | 0 | 0.0137 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1 | 1 | seed_002 | -0.1149 | -0.0326 | 0.0497 | 0.0451 | 0.0941 | 100.0000 | 0 | 0.0136 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls0p65 | 1 | seed_002 | -0.1152 | -0.0373 | 0.0407 | 0.0448 | 0.0787 | 100.0000 | 0 | 0.0131 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1 | 1 | seed_002 | -0.1157 | -0.0354 | 0.0448 | 0.0443 | 0.0953 | 100.0000 | 0 | 0.0132 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p32_ld0p22_ls0p65 | 1 | seed_002 | -0.1178 | -0.0358 | 0.0463 | 0.0422 | 0.0738 | 100.0000 | 0 | 0.0111 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p64_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65 | 1 | seed_002 | -0.1181 | -0.0371 | 0.0438 | 0.0419 | 0.0451 | 100.0000 | 0 | 0.0110 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls0p65 | 1 | seed_002 | -0.1184 | -0.0363 | 0.0458 | 0.0416 | 0.0765 | 100.0000 | 0 | 0.0119 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls0p65 | 1 | seed_002 | -0.1186 | -0.0370 | 0.0447 | 0.0414 | 0.0757 | 100.0000 | 0 | 0.0120 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p22_ls0p65 | 1 | seed_002 | -0.1192 | -0.0382 | 0.0428 | 0.0408 | 0.0791 | 100.0000 | 0 | 0.0119 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p22_ls0p65 | 1 | seed_002 | -0.1363 | -0.0464 | 0.0434 | 0.0382 | 0.0730 | 100.0000 | 0 | 0.0099 | `low_forward_velocity, single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p64_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p22_ls0p65 | 1 | seed_002 | -0.1421 | -0.0508 | 0.0405 | 0.0375 | 0.0393 | 100.0000 | 0 | 0.0094 | `low_forward_velocity, single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p64_hrb0_hra0p04_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1 | 0 | seed_002 | 0.0232 | 0.0301 | 0.0538 | 0.0432 | 0.1195 | 96.0000 | 4 | 0.0083 | `single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p02_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p3_ls1 | 0 | seed_000 | -0.0178 | -0.0075 | 0.0380 | 0.0449 | 0.1228 | 96.0000 | 4 | 0.0130 | `high_lateral_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p03_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1 | 0 | seed_002 | -0.0211 | -0.0097 | 0.0416 | 0.0482 | 0.1287 | 94.0000 | 4 | 0.0143 | `high_lateral_velocity` |
| primitive_p0p52_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p3927_ld0p3_ls1 | 0 | seed_002 | -0.0344 | -0.0237 | 0.0385 | 0.0456 | 0.1161 | 98.0000 | 2 | 0.0131 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p64_hrb0_hra0p04_hrph1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls1 | 0 | seed_002 | -0.0354 | -0.0131 | 0.0493 | 0.0446 | 0.0673 | 98.0000 | 2 | 0.0131 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p64_hrb0_hra0p02_hrph0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p3_ls0p65 | 0 | seed_002 | -0.0361 | -0.0146 | 0.0470 | 0.0439 | 0.1090 | 98.0000 | 2 | 0.0101 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p58_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls1 | 0 | seed_002 | -0.0367 | -0.0144 | 0.0479 | 0.0433 | 0.0716 | 98.0000 | 2 | 0.0137 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hra0p04_hrph1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p32_ld0p22_ls0p65 | 0 | seed_002 | -0.0369 | -0.0178 | 0.0413 | 0.0459 | 0.1203 | 98.0000 | 2 | 0.0131 | `high_lateral_velocity, single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p58_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p22_ls0p65 | 0 | seed_002 | -0.0373 | -0.0181 | 0.0391 | 0.0427 | 0.0738 | 98.0000 | 2 | 0.0114 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p64_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p3_ls0p65 | 0 | seed_002 | -0.0379 | -0.0175 | 0.0428 | 0.0421 | 0.0915 | 98.0000 | 2 | 0.0091 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p47_ld0p22_ls0p65 | 0 | seed_002 | -0.0395 | -0.0051 | 0.0388 | 0.0405 | 0.0692 | 98.0000 | 2 | 0.0082 | `single_contact_pattern_dominates, too_few_contact_transitions` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
