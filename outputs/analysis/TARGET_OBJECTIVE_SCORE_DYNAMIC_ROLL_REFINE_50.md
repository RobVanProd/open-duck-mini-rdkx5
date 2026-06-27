# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `192`
- mode_count: `96`
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
- `low_forward_velocity`: `77`
- `high_lateral_velocity`: `42`
- `too_few_contact_transitions`: `2`

### seed_002
- `single_contact_pattern_dominates`: `91`
- `too_few_contact_transitions`: `85`
- `low_forward_velocity`: `74`
- `low_base_height`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p26_ls0p75 | 1 | seed_000 | 0.0089 | 0.0246 | 0.0365 | 0.0403 | 0.1122 | 94.0000 | 4 | 0.0118 | `` |
| primitive_p0p52_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p34_ld0p3_ls0p65 | 1 | seed_000 | 0.0037 | 0.0235 | 0.0360 | 0.0433 | 0.0930 | 94.0000 | 6 | 0.0129 | `` |
| primitive_p0p54_hrb0_hra0p038_hrphm1_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00495_ph0p34_ld0p26_ls0p65 | 1 | seed_002 | -0.1680 | -0.0639 | 0.0402 | 0.0347 | 0.0664 | 100.0000 | 0 | 0.0088 | `low_forward_velocity, single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hra0p042_hrphm1_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p45_ld0p34_ls0p75 | 0 | seed_000 | 0.0197 | 0.0200 | 0.0431 | 0.0404 | 0.0825 | 96.0000 | 4 | 0.0113 | `single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p3927_ld0p34_ls0p65 | 0 | seed_000 | 0.0187 | 0.0316 | 0.0376 | 0.0446 | 0.1118 | 94.0000 | 6 | 0.0136 | `low_base_height` |
| primitive_p0p54_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0075_ph0p42_ld0p26_ls0p75 | 0 | seed_002 | 0.0119 | 0.0122 | 0.0369 | 0.0391 | 0.1156 | 96.0000 | 4 | 0.0111 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p37_ld0p34_ls0p75 | 0 | seed_002 | 0.0106 | 0.0166 | 0.0381 | 0.0390 | 0.1155 | 96.0000 | 4 | 0.0108 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p3927_ld0p26_ls0p55 | 0 | seed_002 | 0.0043 | 0.0147 | 0.0399 | 0.0360 | 0.0672 | 94.0000 | 4 | 0.0099 | `low_forward_velocity` |
| primitive_p0p5_hrb0_hra0p038_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p34_ld0p26_ls0p65 | 0 | seed_000 | 0.0038 | 0.0127 | 0.0381 | 0.0415 | 0.1126 | 96.0000 | 4 | 0.0129 | `single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00495_ph0p34_ld0p34_ls0p65 | 0 | seed_000 | 0.0008 | 0.0081 | 0.0356 | 0.0395 | 0.1073 | 96.0000 | 4 | 0.0112 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p45_ld0p3_ls0p65 | 0 | seed_002 | 0.0002 | 0.0098 | 0.0406 | 0.0402 | 0.0785 | 96.0000 | 2 | 0.0115 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p45_ld0p3_ls0p55 | 0 | seed_002 | -0.0031 | 0.0129 | 0.0406 | 0.0397 | 0.0709 | 96.0000 | 2 | 0.0112 | `low_forward_velocity, single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p34_ld0p26_ls0p75 | 0 | seed_002 | -0.0049 | 0.0024 | 0.0366 | 0.0372 | 0.0464 | 96.0000 | 4 | 0.0097 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65 | 0 | seed_000 | -0.0062 | -0.0040 | 0.0349 | 0.0398 | 0.0540 | 96.0000 | 2 | 0.0109 | `low_forward_velocity, single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p5_hrb0_hra0p046_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p34_ls0p55 | 0 | seed_002 | -0.0077 | -0.0056 | 0.0383 | 0.0391 | 0.0566 | 96.0000 | 2 | 0.0108 | `low_forward_velocity, single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p3927_ld0p26_ls0p65 | 0 | seed_002 | -0.0084 | -0.0078 | 0.0348 | 0.0368 | 0.0449 | 92.0000 | 2 | 0.0095 | `low_forward_velocity, too_few_contact_transitions` |
| primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p34_ld0p26_ls0p55 | 0 | seed_002 | -0.0147 | 0.0038 | 0.0390 | 0.0361 | 0.0726 | 96.0000 | 4 | 0.0097 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p0066_ph0p45_ld0p26_ls0p65 | 0 | seed_002 | -0.0179 | 0.0003 | 0.0390 | 0.0380 | 0.0518 | 96.0000 | 2 | 0.0100 | `low_forward_velocity, single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p5_hrb0_hra0p046_hrphm0p58_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p34_ld0p26_ls0p75 | 0 | seed_002 | -0.0200 | -0.0084 | 0.0359 | 0.0378 | 0.0532 | 96.0000 | 2 | 0.0101 | `low_forward_velocity, single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p54_hrb0_hra0p04_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65 | 0 | seed_002 | -0.0213 | -0.0011 | 0.0377 | 0.0376 | 0.0695 | 96.0000 | 2 | 0.0102 | `low_forward_velocity, single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p34_ld0p3_ls0p65 | 0 | seed_002 | -0.0226 | -0.0047 | 0.0411 | 0.0375 | 0.0688 | 96.0000 | 2 | 0.0102 | `low_forward_velocity, single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p37_ld0p34_ls0p75 | 0 | seed_002 | -0.0373 | -0.0006 | 0.0396 | 0.0427 | 0.0923 | 98.0000 | 2 | 0.0118 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75 | 0 | seed_002 | -0.0394 | -0.0229 | 0.0415 | 0.0406 | 0.1142 | 98.0000 | 2 | 0.0118 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p5_hrb0_hra0p038_hrphm1_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p42_ld0p34_ls0p55 | 0 | seed_002 | -0.0396 | -0.0032 | 0.0392 | 0.0404 | 0.0808 | 98.0000 | 2 | 0.0118 | `single_contact_pattern_dominates, too_few_contact_transitions` |
| primitive_p0p5_hrb0_hra0p034_hrphm0p9_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p42_ld0p3_ls0p55 | 0 | seed_002 | -0.0396 | -0.0110 | 0.0393 | 0.0404 | 0.0610 | 98.0000 | 2 | 0.0115 | `single_contact_pattern_dominates, too_few_contact_transitions` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
