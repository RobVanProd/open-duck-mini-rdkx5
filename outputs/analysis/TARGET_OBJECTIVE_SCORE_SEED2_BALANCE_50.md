# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `160`
- mode_count: `80`
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

## Seed Failure Counts

### seed_000
- `low_forward_velocity`: `38`
- `high_lateral_velocity`: `26`
- `short_done_margin`: `23`
- `high_body_pitch`: `22`
- `low_base_height`: `22`
- `single_contact_pattern_dominates`: `6`
- `done_inside_window`: `2`
- `missing_seed_trace_or_window`: `1`

### seed_002
- `single_contact_pattern_dominates`: `76`
- `low_forward_velocity`: `38`
- `short_done_margin`: `22`
- `high_body_pitch`: `20`
- `low_base_height`: `16`
- `high_lateral_velocity`: `4`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927 | 1 | seed_002 | -0.0085 | 0.0240 | 0.0565 | 0.0515 | 0.0507 | 98.0000 | `single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hb0p06_h0p05_kb0p03_k0p1_ab0p08_a0_ph0p3927 | 1 | seed_002 | -0.0484 | -0.0026 | 0.0432 | 0.0516 | 0.0747 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p7_hrbm0p01_hb0p08_h0p05_kb0p06_k0p12_ab0p04_a0_ph0p589 | 1 | seed_002 | -0.0491 | 0.0026 | 0.0543 | 0.0509 | 0.0380 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p55_hrb0p01_hb0p06_h0p05_kb0p03_k0p08_ab0p08_a0p015_ph0p3927 | 1 | seed_002 | -0.0532 | -0.0048 | 0.0435 | 0.0468 | 0.0660 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p7_hrb0p01_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p1963 | 1 | seed_002 | -0.0536 | -0.0016 | 0.0503 | 0.0464 | 0.0403 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hb0p06_h0p04_kb0p03_k0p1_ab0p08_a0_ph0p7854 | 1 | seed_002 | -0.0547 | -0.0069 | 0.0409 | 0.0453 | 0.0737 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p7_hrb0_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p1963 | 1 | seed_002 | -0.0556 | -0.0009 | 0.0537 | 0.0444 | 0.0419 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p7_hrb0p01_hb0p06_h0p05_kb0p06_k0p1_ab0p04_am0p015_ph0p589 | 1 | seed_002 | -0.0761 | -0.0166 | 0.0429 | 0.0382 | 0.0577 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p55_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963 | 1 | seed_002 | -0.1130 | -0.0318 | 0.0494 | 0.0341 | 0.0660 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963 | 1 | seed_002 | -0.1497 | -0.0520 | 0.0458 | 0.0300 | 0.0729 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrbm0p01_hb0p06_h0p04_kb0p03_k0p1_ab0p08_a0p012_ph0p589 | 1 | seed_002 | -0.3403 | -0.1466 | 0.0471 | 0.0656 | 0.0790 | 100.0000 | `high_body_pitch, short_done_margin, single_contact_pattern_dominates` |
| primitive_p0p5_hrbm0p01_hb0p06_h0p04_kb0p03_k0p12_ab0p08_a0_ph0p1963 | 1 | seed_002 | -0.4747 | -0.2111 | 0.0526 | 0.0728 | 0.0895 | 100.0000 | `high_body_pitch, short_done_margin, single_contact_pattern_dominates` |
| primitive_p0p6_hrb0p01_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p589 | 1 | seed_002 | -0.4862 | -0.2198 | 0.0467 | 0.0732 | 0.1061 | 98.0000 | `high_body_pitch, short_done_margin, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0p01_hb0p06_h0p04_kb0p03_k0p12_ab0p08_a0p012_ph0p589 | 1 | seed_002 | -0.6838 | -0.3154 | 0.0530 | 0.0811 | 0.0954 | 100.0000 | `high_body_pitch, short_done_margin, single_contact_pattern_dominates` |
| primitive_p0p7_hrbm0p01_hb0p08_h0p04_kb0p06_k0p08_ab0p04_a0p012_ph0p589 | 0 | seed_002 | -0.0472 | -0.0087 | 0.0389 | 0.0528 | 0.0371 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p5_hrb0p01_hb0p08_h0p05_kb0p06_k0p08_ab0p04_a0p015_ph0p589 | 0 | seed_002 | -0.0507 | -0.0102 | 0.0389 | 0.0493 | 0.0444 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p7_hrb0_hb0p06_h0p04_kb0p03_k0p12_ab0p08_a0_ph0p1963 | 0 | seed_002 | -0.0581 | -0.0098 | 0.0465 | 0.0419 | 0.0529 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p5_hrb0_hb0p06_h0p03_kb0p03_k0p1_ab0p08_a0_ph0p1963 | 0 | seed_002 | -0.0587 | -0.0147 | 0.0403 | 0.0413 | 0.0793 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p55_hrbm0p01_hb0p08_h0p04_kb0p03_k0p12_ab0p04_am0p012_ph0p1963 | 0 | seed_000 | -0.0619 | -0.0547 | 0.0301 | 0.0525 | 0.0706 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p7_hrb0_hb0p06_h0p04_kb0p06_k0p12_ab0p04_a0_ph0 | 0 | seed_000 | -0.0898 | -0.0822 | 0.0256 | 0.0384 | 0.0517 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p5_hrb0p01_hb0p08_h0p05_kb0p03_k0p12_ab0p04_a0p015_ph0p3927 | 0 | seed_000 | -0.0949 | -0.0732 | 0.0250 | 0.0485 | 0.0839 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p6_hrb0p01_hb0p06_h0p04_kb0p06_k0p08_ab0p04_a0p012_ph0p589 | 0 | seed_002 | -0.1048 | -0.1046 | 0.0240 | 0.0350 | 0.0972 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p6_hrb0_hb0p08_h0p03_kb0p03_k0p1_ab0p04_a0p009_ph0p1963 | 0 | seed_000 | -0.1150 | -0.0848 | 0.0250 | 0.0453 | 0.0568 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p7_hrb0_hb0p04_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p589 | 0 | seed_000 | -0.1217 | -0.1151 | 0.0220 | 0.0346 | 0.0613 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p55_hrb0p01_hb0p06_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p7854 | 0 | seed_002 | -0.1253 | -0.0450 | 0.0395 | 0.0327 | 0.0696 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
