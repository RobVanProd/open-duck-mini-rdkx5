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

## Seed Failure Counts

### seed_000
- `low_forward_velocity`: `21`
- `high_body_pitch`: `20`
- `short_done_margin`: `20`
- `low_base_height`: `18`
- `high_lateral_velocity`: `15`
- `single_contact_pattern_dominates`: `3`

### seed_002
- `single_contact_pattern_dominates`: `44`
- `short_done_margin`: `19`
- `high_body_pitch`: `16`
- `low_base_height`: `14`
- `low_forward_velocity`: `14`
- `high_lateral_velocity`: `4`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p55_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p7854 | 1 | seed_002 | -0.0526 | 0.0008 | 0.0541 | 0.0474 | 0.0631 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p7_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p3927 | 1 | seed_002 | -0.0569 | -0.0064 | 0.0441 | 0.0431 | 0.0315 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p55_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p3927 | 1 | seed_002 | -0.0784 | -0.0178 | 0.0428 | 0.0380 | 0.0598 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p7_hrbm0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p08_a0_ph0p7854 | 1 | seed_002 | -0.1500 | -0.0469 | 0.0562 | 0.0606 | 0.0984 | 98.0000 | `short_done_margin, single_contact_pattern_dominates` |
| primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p7854 | 1 | seed_002 | -0.1900 | -0.0661 | 0.0579 | 0.0620 | 0.1158 | 100.0000 | `short_done_margin, single_contact_pattern_dominates` |
| primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0p08_am0p009_ph0p3927 | 0 | seed_002 | -0.0447 | -0.0060 | 0.0527 | 0.0553 | 0.0478 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p08_ab0p04_a0p009_ph0 | 0 | seed_002 | -0.0463 | -0.0209 | 0.0385 | 0.0537 | 0.0534 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p08_a0p009_ph0 | 0 | seed_002 | -0.0586 | -0.0266 | 0.0362 | 0.0414 | 0.0678 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p55_hrbm0p02_hb0p08_h0p05_kb0p03_k0p12_ab0p04_am0p015_ph0 | 0 | seed_000 | -0.0880 | -0.0706 | 0.0258 | 0.0468 | 0.0835 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p7_hrb0_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0p7854 | 0 | seed_000 | -0.0885 | -0.0721 | 0.0257 | 0.0442 | 0.0647 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p7_hrb0_hb0p04_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p7854 | 0 | seed_002 | -0.0992 | -0.0566 | 0.0340 | 0.0356 | 0.0572 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p08_a0_ph0p3927 | 0 | seed_002 | -0.1005 | -0.0819 | 0.0552 | 0.0355 | 0.0639 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p12_ab0p04_a0_ph0p3927 | 0 | seed_000 | -0.1083 | -0.0822 | 0.0235 | 0.0439 | 0.1024 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p7_hrbm0p02_hb0p04_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p3927 | 0 | seed_000 | -0.1124 | -0.1042 | 0.0231 | 0.0360 | 0.0713 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p55_hrb0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0p3927 | 0 | seed_002 | -0.1158 | -0.0962 | 0.0271 | 0.0338 | 0.0701 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p7_hrbm0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0 | 0 | seed_000 | -0.1415 | -0.0969 | 0.0198 | 0.0476 | 0.0443 | 100.0000 | `single_contact_pattern_dominates` |
| primitive_p0p55_hrb0p02_hb0p06_h0p03_kb0p03_k0p12_ab0p04_a0p009_ph0p3927 | 0 | seed_002 | -0.1810 | -0.1474 | 0.0229 | 0.0418 | 0.1478 | 94.0000 | `high_lateral_velocity` |
| primitive_p0p7_hrb0_hb0p06_h0p03_kb0p03_k0p12_ab0p04_am0p009_ph0p7854 | 0 | seed_000 | -0.1944 | -0.1913 | 0.0162 | 0.0258 | 0.0588 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p55_hrb0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p04_a0_ph0p7854 | 0 | seed_002 | -0.1949 | -0.1566 | 0.0224 | 0.0250 | 0.0725 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p55_hrbm0p02_hb0p04_h0p05_kb0p06_k0p08_ab0p04_a0p015_ph0 | 0 | seed_002 | -0.1970 | -0.1638 | 0.0210 | 0.0248 | 0.0602 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p55_hrbm0p02_hb0p08_h0p05_kb0p03_k0p08_ab0p04_a0_ph0 | 0 | seed_000 | -0.1983 | -0.1749 | 0.0157 | 0.0298 | 0.0927 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0 | 0 | seed_002 | -0.2126 | -0.1633 | 0.0229 | 0.0230 | 0.0589 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p55_hrbm0p02_hb0p04_h0p03_kb0p03_k0p12_ab0p04_a0p009_ph0 | 0 | seed_002 | -0.2185 | -0.1826 | 0.0192 | 0.0224 | 0.0756 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p55_hrbm0p02_hb0p04_h0p05_kb0p03_k0p12_ab0p04_a0p015_ph0 | 0 | seed_002 | -0.2291 | -0.1920 | 0.0183 | 0.0212 | 0.0702 | 100.0000 | `low_forward_velocity, single_contact_pattern_dominates` |
| primitive_p0p7_hrb0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p04_a0p009_ph0p7854 | 0 | seed_000 | -0.2331 | -0.1448 | 0.0129 | 0.0436 | 0.0408 | 100.0000 | `single_contact_pattern_dominates` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
