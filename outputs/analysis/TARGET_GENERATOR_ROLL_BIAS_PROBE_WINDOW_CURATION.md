# Realized Target Window Curation

status: `PASS_CURATED_DATASET_SEED_READY`

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

- mined_windows: `64`
- pass_curated_seed_windows: `12`
- review_motion_hints: `52`
- rejected_dataset_seeds: `0`
- curated_source_files: `1`
- curated_modes: `12`
- curated_source_mode_pairs: `12`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0449 | 0.0853 | 0.1321 | 0.1557 | 0.4196 | 0.0566 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0718 | 0.0647 | 0.2081 | 0.1525 | 0.4196 | 0.0640 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0716 | 0.0777 | 0.2014 | 0.1547 | 0.4196 | 0.0629 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0606 | 0.0708 | 0.1936 | 0.1509 | 0.4196 | 0.0614 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 5-29 | 0.0474 | 0.0596 | 0.1795 | 0.1507 | 0.4538 | 0.0616 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0510 | 0.0919 | 0.1558 | 0.1553 | 0.3454 | 0.0604 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0775 | 0.0702 | 0.2394 | 0.1515 | 0.3454 | 0.0654 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 5-29 | 0.0493 | 0.0515 | 0.1621 | 0.1531 | 0.3473 | 0.0563 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p9_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0757 | 0.0831 | 0.2368 | 0.1534 | 0.3454 | 0.0662 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0418 | 0.1108 | 0.1402 | 0.1536 | 0.3454 | 0.0568 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0742 | 0.0759 | 0.2335 | 0.1497 | 0.3454 | 0.0642 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 5-29 | 0.0592 | 0.0563 | 0.1907 | 0.1502 | 0.3473 | 0.0612 | None | 88.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0480 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0402 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0735 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0434 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0646 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0527 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0467 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 0-24 | 0.0450 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0557 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0735 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0440 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0669 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0540 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0471 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 0-24 | 0.0404 | `high_lateral_velocity` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
