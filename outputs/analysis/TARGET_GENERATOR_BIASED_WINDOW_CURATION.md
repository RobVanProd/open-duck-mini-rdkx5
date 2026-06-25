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
- min_source_mode_pairs: `2`

## Counts

- mined_windows: `16`
- pass_curated_seed_windows: `5`
- review_motion_hints: `11`
- rejected_dataset_seeds: `0`
- curated_source_files: `1`
- curated_modes: `5`
- curated_source_mode_pairs: `5`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0449 | 0.0853 | 0.1321 | 0.1557 | 0.4196 | 0.0566 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0718 | 0.0647 | 0.2081 | 0.1525 | 0.4196 | 0.0640 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0510 | 0.0919 | 0.1558 | 0.1553 | 0.3454 | 0.0604 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0775 | 0.0702 | 0.2394 | 0.1515 | 0.3454 | 0.0654 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 5-29 | 0.0493 | 0.0515 | 0.1621 | 0.1531 | 0.3473 | 0.0563 | None | 92.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0480 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0735 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0434 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 0-24 | 0.0450 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p7_hbm0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0437 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0499 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0746 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0565 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 0-24 | 0.0543 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p9_hbm0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0474 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p9_hbm0p06_h0p05_kb0p03_k0p08_abm0p04_am0p025_ph0` | 50-74 | 0.0414 | `single_contact_pattern_dominates` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
