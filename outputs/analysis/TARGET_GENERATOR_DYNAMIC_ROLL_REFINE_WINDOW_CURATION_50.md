# Realized Target Window Curation

status: `HOLD_INSUFFICIENT_CURATED_WINDOWS`

This applies stricter dataset-readiness filters to the mined realized
motion windows. It does not export raw traces or start training.

## Criteria

- min_curated_windows: `8`
- min_mean_vx: `0.04`
- max_vy_abs_p95: `0.12`
- max_pitch_abs_p95: `0.35`
- min_base_height: `0.145`
- max_action_saturation_pct: `1.0`
- max_sent_velocity_p95: `2.5`
- max_tracking_p95: `0.12`
- min_done_margin: `50`
- max_contact_dominance_pct: `95.0`
- min_source_files: `2`
- min_source_mode_pairs: `2`

## Counts

- mined_windows: `186`
- pass_curated_seed_windows: `3`
- review_motion_hints: `183`
- rejected_dataset_seeds: `0`
- curated_source_files: `2`
- curated_modes: `3`
- curated_source_mode_pairs: `3`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p34_ld0p3_ls0p65` | 5-54 | 0.0433 | 0.0930 | 0.2889 | 0.1455 | 0.5918 | 0.0721 | None | 94.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p26_ls0p75` | 5-54 | 0.0403 | 0.1122 | 0.2636 | 0.1469 | 0.4819 | 0.0704 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm1_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00495_ph0p34_ld0p26_ls0p65` | 0-49 | 0.0402 | 0.1198 | 0.2715 | 0.1485 | 0.4393 | 0.0760 | None | 92.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 0-49 | 0.0415 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 0-49 | 0.0484 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 10-59 | 0.0420 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 5-54 | 0.0406 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p45_ld0p3_ls0p55` | 0-49 | 0.0442 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0045_ph0p45_ld0p34_ls0p65` | 0-49 | 0.0406 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0045_ph0p45_ld0p34_ls0p65` | 0-49 | 0.0472 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p45_ld0p3_ls0p65` | 0-49 | 0.0455 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p45_ld0p3_ls0p65` | 10-59 | 0.0408 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p34_ld0p26_ls0p65` | 0-49 | 0.0442 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p45_ld0p3_ls0p65` | 0-49 | 0.0406 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p45_ld0p3_ls0p65` | 0-49 | 0.0494 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p45_ld0p3_ls0p65` | 5-54 | 0.0402 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p58_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p37_ld0p26_ls0p75` | 0-49 | 0.0409 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p58_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p37_ld0p26_ls0p75` | 0-49 | 0.0452 | `high_lateral_velocity` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
