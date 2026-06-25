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

- mined_windows: `91`
- pass_curated_seed_windows: `0`
- review_motion_hints: `80`
- rejected_dataset_seeds: `11`
- curated_source_files: `0`
- curated_modes: `0`
- curated_source_mode_pairs: `0`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| NA | NA | NA | NA | NA | NA | NA | NA | NA | NA | NA |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0646 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0527 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0467 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 0-24 | 0.0618 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 5-29 | 0.0477 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p7854` | 0-24 | 0.0452 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p1781` | 0-24 | 0.0441 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0622 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0505 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0443 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 0-24 | 0.0473 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p7854` | 0-24 | 0.0478 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p1781` | 0-24 | 0.0438 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 0-24 | 0.0427 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 15-39 | 0.0401 | `single_contact_pattern_dominates` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
