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
- `low_forward_velocity`: `27`
- `high_body_pitch`: `19`
- `short_done_margin`: `15`
- `low_base_height`: `12`
- `high_lateral_velocity`: `10`
- `single_contact_pattern_dominates`: `6`

### seed_002
- `single_contact_pattern_dominates`: `96`
- `low_forward_velocity`: `21`
- `short_done_margin`: `6`
- `high_body_pitch`: `2`
- `high_lateral_velocity`: `1`
- `low_base_height`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p0035_ph0p47_ld0p3_ls0p35 | 1 | seed_002 | -0.0081 | 0.0213 | 0.0508 | 0.0519 | 0.0937 | 98.0000 | 2 | NA | `single_contact_pattern_dominates` |
| primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p3927_ld0p22_ls0p35 | 1 | seed_002 | -0.0131 | 0.0154 | 0.0440 | 0.0469 | 0.0940 | 98.0000 | 2 | NA | `single_contact_pattern_dominates` |
| primitive_p0p56_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p0075_ph0p32_ld0p38_ls0p65 | 1 | seed_002 | -0.0162 | 0.0121 | 0.0403 | 0.0438 | 0.1079 | 98.0000 | 2 | NA | `single_contact_pattern_dominates` |
| primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p014_ph0p3927_ld0p3_ls0p35 | 1 | seed_002 | -0.0179 | 0.0127 | 0.0433 | 0.0421 | 0.1108 | 98.0000 | 2 | NA | `single_contact_pattern_dominates` |
| primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p012_ph0p32_ld0p3_ls0p35 | 1 | seed_002 | -0.0179 | 0.0121 | 0.0421 | 0.0421 | 0.1072 | 98.0000 | 2 | NA | `single_contact_pattern_dominates` |
| primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p0075_ph0p54_ld0p38_ls0p65 | 1 | seed_002 | -0.0191 | 0.0105 | 0.0400 | 0.0409 | 0.1158 | 98.0000 | 2 | NA | `single_contact_pattern_dominates` |
| primitive_p0p68_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_a0_ph0p32_ld0p38_ls1 | 1 | seed_002 | -0.0417 | 0.0008 | 0.0433 | 0.0376 | 0.1172 | 98.0000 | 2 | NA | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p54_ld0p3_ls0p35 | 1 | seed_002 | -0.0434 | 0.0059 | 0.0552 | 0.0566 | 0.0535 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p00875_ph0p32_ld0p38_ls0p35 | 1 | seed_002 | -0.0445 | 0.0065 | 0.0575 | 0.0555 | 0.0710 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p68_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_a0_ph0p54_ld0p22_ls0p35 | 1 | seed_002 | -0.0455 | 0.0061 | 0.0577 | 0.0545 | 0.0666 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p47_ld0p38_ls0p65 | 1 | seed_002 | -0.0485 | 0.0010 | 0.0505 | 0.0515 | 0.0667 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p54_ld0p38_ls0p35 | 1 | seed_002 | -0.0487 | 0.0001 | 0.0489 | 0.0513 | 0.0466 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p54_ld0p22_ls0p35 | 1 | seed_002 | -0.0489 | -0.0010 | 0.0469 | 0.0511 | 0.0456 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p56_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p003_ph0p3927_ld0p38_ls0p65 | 1 | seed_002 | -0.0498 | 0.0001 | 0.0501 | 0.0502 | 0.0717 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p54_ld0p22_ls0p35 | 1 | seed_002 | -0.0504 | -0.0003 | 0.0498 | 0.0496 | 0.0782 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_a0_ph0p3927_ld0p22_ls0p65 | 1 | seed_002 | -0.0509 | 0.0003 | 0.0515 | 0.0491 | 0.0392 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p56_hrbm0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p38_ls0p65 | 1 | seed_002 | -0.0509 | -0.0038 | 0.0433 | 0.0491 | 0.1064 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p56_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p38_ls0p35 | 1 | seed_002 | -0.0511 | -0.0008 | 0.0494 | 0.0489 | 0.0710 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p012_ph0p3927_ld0p22_ls0p65 | 1 | seed_002 | -0.0516 | -0.0002 | 0.0512 | 0.0484 | 0.0414 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p68_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p32_ld0p38_ls0p35 | 1 | seed_002 | -0.0521 | -0.0031 | 0.0458 | 0.0479 | 0.0396 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927_ld0p3_ls0p35 | 1 | seed_002 | -0.0526 | -0.0037 | 0.0451 | 0.0474 | 0.0969 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p00625_ph0p3927_ld0p38_ls0p35 | 1 | seed_002 | -0.0531 | -0.0045 | 0.0442 | 0.0469 | 0.0381 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p32_ld0p38_ls0p35 | 1 | seed_002 | -0.0534 | -0.0041 | 0.0451 | 0.0466 | 0.0361 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p68_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p38_ls0p65 | 1 | seed_002 | -0.0537 | -0.0036 | 0.0466 | 0.0463 | 0.0423 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |
| primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p01_ph0p47_ld0p38_ls0p35 | 1 | seed_002 | -0.0537 | -0.0039 | 0.0458 | 0.0463 | 0.0462 | 100.0000 | 0 | NA | `single_contact_pattern_dominates` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
