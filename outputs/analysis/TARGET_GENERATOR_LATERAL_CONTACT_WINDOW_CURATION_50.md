# Realized Target Window Curation

status: `HOLD_INSUFFICIENT_CURATED_DIVERSITY`

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

- mined_windows: `56`
- pass_curated_seed_windows: `8`
- review_motion_hints: `48`
- rejected_dataset_seeds: `0`
- curated_source_files: `1`
- curated_modes: `5`
- curated_source_mode_pairs: `5`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p3927` | 0-49 | 0.0428 | 0.1039 | 0.2779 | 0.1493 | 0.5605 | 0.0743 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p7854` | 5-54 | 0.0579 | 0.0626 | 0.3320 | 0.1481 | 0.5682 | 0.0741 | 50 | 94.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p7854` | 0-49 | 0.0568 | 0.1158 | 0.3281 | 0.1481 | 0.5647 | 0.0824 | 55 | 90.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p7854` | 0-49 | 0.0541 | 0.1057 | 0.3159 | 0.1476 | 0.5818 | 0.0834 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p7854` | 5-54 | 0.0539 | 0.0599 | 0.3226 | 0.1476 | 0.6811 | 0.0728 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p3927` | 5-54 | 0.0441 | 0.0496 | 0.2748 | 0.1486 | 0.3147 | 0.0647 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p3927` | 0-49 | 0.0402 | 0.1159 | 0.2588 | 0.1486 | 0.2951 | 0.0714 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p08_a0_ph0p7854` | 5-54 | 0.0562 | 0.0524 | 0.3310 | 0.1473 | 0.3746 | 0.0639 | 54 | 92.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 0-49 | 0.0476 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p08_a0p009_ph0` | 0-49 | 0.0403 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p08_a0p009_ph0` | 0-49 | 0.0512 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p08_a0p009_ph0` | 5-54 | 0.0414 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p3927` | 0-49 | 0.0483 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0_ph0` | 0-49 | 0.0625 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0_ph0` | 5-54 | 0.0563 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0_ph0` | 10-59 | 0.0505 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p12_ab0p04_a0_ph0p3927` | 0-49 | 0.0532 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p12_ab0p04_a0_ph0p3927` | 5-54 | 0.0439 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p12_ab0p04_a0_ph0p3927` | 10-59 | 0.0435 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p12_ab0p04_a0_ph0p3927` | 15-64 | 0.0427 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p12_ab0p04_a0_ph0p3927` | 20-69 | 0.0406 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0p02_hb0p06_h0p03_kb0p03_k0p12_ab0p04_a0p009_ph0p3927` | 0-49 | 0.0418 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0p3927` | 0-49 | 0.0473 | `high_lateral_velocity` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
