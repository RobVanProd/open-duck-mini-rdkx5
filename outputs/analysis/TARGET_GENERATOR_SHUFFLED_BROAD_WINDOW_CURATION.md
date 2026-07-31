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
- min_source_files: `2`
- min_source_mode_pairs: `2`

## Counts

- mined_windows: `137`
- pass_curated_seed_windows: `11`
- review_motion_hints: `91`
- rejected_dataset_seeds: `35`
- curated_source_files: `2`
- curated_modes: `11`
- curated_source_mode_pairs: `11`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p015_ph1p1781` | 5-29 | 0.0443 | 0.0487 | 0.2106 | 0.1490 | 0.4388 | 0.0635 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p07_kb0p06_k0p12_ab0p04_am0p021_ph0` | 5-29 | 0.1077 | 0.0778 | 0.3013 | 0.1497 | 0.7888 | 0.0709 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p03_kb0p03_k0p04_ab0p04_am0p009_ph0` | 5-29 | 0.0417 | 0.0847 | 0.1316 | 0.1550 | 0.3338 | 0.0605 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0p04_hb0p04_h0p05_kb0_k0p04_ab0p08_am0p015_ph0p7854` | 5-29 | 0.0533 | 0.0747 | 0.1777 | 0.1570 | 0.3684 | 0.0642 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p85_hrb0_hb0p04_h0p03_kb0_k0p04_ab0p08_am0p024_ph0` | 5-29 | 0.0666 | 0.0695 | 0.2267 | 0.1530 | 0.2142 | 0.0678 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p85_hrb0_hb0p06_h0p07_kb0p06_k0p04_ab0p04_am0p035_ph1p1781` | 5-29 | 0.0911 | 0.0829 | 0.2561 | 0.1510 | 0.4196 | 0.0708 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p85_hrb0p04_hb0p06_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p3927` | 5-29 | 0.0783 | 0.0676 | 0.2519 | 0.1509 | 0.2239 | 0.0707 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p85_hrbm0p04_hb0p06_h0p07_kb0_k0p04_ab0p08_am0p021_ph0p7854` | 5-29 | 0.0823 | 0.0684 | 0.2267 | 0.1527 | 0.4097 | 0.0671 | None | 84.0000 |
| seed_000.jsonl | `primitive_p1_hrb0_hb0p04_h0p03_kb0p03_k0p04_ab0p08_am0p015_ph1p1781` | 5-29 | 0.0773 | 0.0728 | 0.2503 | 0.1515 | 0.1838 | 0.0686 | None | 88.0000 |
| seed_000.jsonl | `primitive_p1_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p04_am0p024_ph1p5708` | 5-29 | 0.0747 | 0.0521 | 0.2354 | 0.1497 | 0.2232 | 0.0549 | None | 92.0000 |
| seed_002.jsonl | `primitive_p1_hrbm0p08_hb0p08_h0p05_kb0p03_k0p12_ab0p08_am0p015_ph0p3927` | 5-29 | 0.0726 | 0.0910 | 0.1825 | 0.1484 | 0.3233 | 0.0552 | 73 | 92.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p015_ph1p1781` | 0-24 | 0.0535 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p015_ph1p1781` | 0-24 | 0.0617 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p015_ph1p1781` | 5-29 | 0.0506 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p015_ph1p1781` | 10-34 | 0.0452 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p05_kb0_k0p12_ab0p04_am0p015_ph0p3927` | 0-24 | 0.0458 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p05_kb0_k0p12_ab0p04_am0p015_ph0p3927` | 0-24 | 0.0433 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p07_kb0p06_k0p12_ab0p04_am0p021_ph0` | 0-24 | 0.1028 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p07_kb0p06_k0p12_ab0p04_am0p021_ph0` | 10-34 | 0.0870 | `high_body_pitch, single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p07_kb0p06_k0p12_ab0p04_am0p021_ph0` | 0-24 | 0.0767 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p07_kb0p06_k0p12_ab0p04_am0p021_ph0` | 5-29 | 0.0584 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p07_kb0p06_k0p12_ab0p04_am0p021_ph0` | 10-34 | 0.0492 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p03_kb0p03_k0p04_ab0p04_am0p009_ph0` | 0-24 | 0.0441 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p55_hrb0p04_hb0p04_h0p03_kb0_k0p08_ab0p08_am0p024_ph1p5708` | 0-24 | 0.0446 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p55_hrb0p04_hb0p04_h0p03_kb0_k0p08_ab0p08_am0p024_ph1p5708` | 5-29 | 0.0411 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0p04_hb0p04_h0p03_kb0_k0p08_ab0p08_am0p024_ph1p5708` | 0-24 | 0.0634 | `high_lateral_velocity` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
