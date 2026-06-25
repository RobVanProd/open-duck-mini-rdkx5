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
- min_contact_transitions: `0`
- min_foot_site_z_p95: `-1.0`

## Seed Failure Counts

### seed_000
- `short_done_margin`: `58`
- `high_body_pitch`: `45`
- `low_base_height`: `21`
- `high_lateral_velocity`: `12`

### seed_002
- `single_contact_pattern_dominates`: `87`
- `short_done_margin`: `65`
- `high_body_pitch`: `55`
- `low_base_height`: `35`
- `high_lateral_velocity`: `9`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p014_ph0p3927 | 1 | seed_002 | -0.0147 | 0.0192 | 0.0531 | 0.0453 | 0.1028 | 98.0000 | 2 | NA | `single_contact_pattern_dominates` |
| primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p04_am0p012_ph0p32 | 1 | seed_002 | -0.0405 | 0.0079 | 0.0564 | 0.0595 | 0.0584 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0_ph0p36 | 1 | seed_002 | -0.0414 | 0.0059 | 0.0532 | 0.0586 | 0.0568 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p66_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p3927 | 1 | seed_002 | -0.0424 | 0.0027 | 0.0478 | 0.0576 | 0.0548 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p012_ph0p43 | 1 | seed_002 | -0.0429 | 0.0070 | 0.0568 | 0.0571 | 0.0539 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p007_ph0p43 | 1 | seed_002 | -0.0432 | 0.0047 | 0.0525 | 0.0568 | 0.0512 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p16_ab0p04_am0p0035_ph0p32 | 1 | seed_002 | -0.0435 | 0.0042 | 0.0519 | 0.0565 | 0.0733 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p58_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p005_ph0p36 | 1 | seed_002 | -0.0452 | 0.0039 | 0.0529 | 0.0548 | 0.0603 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p47 | 1 | seed_002 | -0.0454 | 0.0045 | 0.0544 | 0.0546 | 0.0581 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p04_am0p014_ph0p36 | 1 | seed_002 | -0.0458 | 0.0059 | 0.0575 | 0.0542 | 0.0557 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927 | 1 | seed_002 | -0.0461 | 0.0041 | 0.0543 | 0.0539 | 0.0563 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p62_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927 | 1 | seed_002 | -0.0467 | 0.0047 | 0.0562 | 0.0533 | 0.0506 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p04_a0_ph0p47 | 1 | seed_002 | -0.0468 | 0.0005 | 0.0477 | 0.0532 | 0.0534 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0_ph0p47 | 1 | seed_002 | -0.0473 | 0.0036 | 0.0545 | 0.0527 | 0.0499 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p52 | 1 | seed_002 | -0.0478 | 0.0040 | 0.0559 | 0.0522 | 0.0513 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p58_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p47 | 1 | seed_002 | -0.0478 | 0.0038 | 0.0554 | 0.0522 | 0.0651 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p47 | 1 | seed_002 | -0.0479 | 0.0025 | 0.0530 | 0.0521 | 0.0539 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p43 | 1 | seed_002 | -0.0480 | 0.0017 | 0.0514 | 0.0520 | 0.0530 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p32 | 1 | seed_002 | -0.0486 | -0.0001 | 0.0485 | 0.0514 | 0.0521 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p62_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p005_ph0p3927 | 1 | seed_002 | -0.0494 | -0.0002 | 0.0489 | 0.0506 | 0.0502 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p62_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p52 | 1 | seed_002 | -0.0496 | 0.0032 | 0.0561 | 0.0504 | 0.0507 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43 | 1 | seed_002 | -0.0518 | -0.0001 | 0.0517 | 0.0482 | 0.0686 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p47 | 1 | seed_002 | -0.0532 | -0.0004 | 0.0525 | 0.0468 | 0.0701 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p62_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p009_ph0p3927 | 1 | seed_002 | -0.0532 | -0.0021 | 0.0490 | 0.0468 | 0.0430 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p01_ph0p3927 | 1 | seed_002 | -0.0535 | -0.0025 | 0.0484 | 0.0465 | 0.0605 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
