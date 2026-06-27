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

- mined_windows: `89`
- pass_curated_seed_windows: `23`
- review_motion_hints: `66`
- rejected_dataset_seeds: `0`
- curated_source_files: `1`
- curated_modes: `14`
- curated_source_mode_pairs: `14`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p55_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963` | 0-49 | 0.0494 | 0.1007 | 0.3396 | 0.1455 | 0.5365 | 0.0915 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963` | 5-54 | 0.0424 | 0.0910 | 0.3396 | 0.1455 | 0.5836 | 0.0833 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0p01_hb0p06_h0p05_kb0p03_k0p08_ab0p08_a0p015_ph0p3927` | 0-49 | 0.0435 | 0.1171 | 0.2682 | 0.1499 | 0.5605 | 0.0806 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p04_kb0p03_k0p1_ab0p08_a0_ph0p7854` | 0-49 | 0.0409 | 0.1087 | 0.2768 | 0.1478 | 0.5520 | 0.0808 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p05_kb0p03_k0p1_ab0p08_a0_ph0p3927` | 0-49 | 0.0432 | 0.1127 | 0.2814 | 0.1481 | 0.6266 | 0.0828 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963` | 0-49 | 0.0458 | 0.1000 | 0.3196 | 0.1463 | 0.6768 | 0.0942 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0p01_hb0p06_h0p04_kb0p03_k0p12_ab0p08_a0p012_ph0p589` | 0-49 | 0.0530 | 0.1104 | 0.3206 | 0.1470 | 0.6666 | 0.0901 | 52 | 90.0000 |
| seed_000.jsonl | `primitive_p0p5_hrbm0p01_hb0p06_h0p04_kb0p03_k0p12_ab0p08_a0_ph0p1963` | 0-49 | 0.0526 | 0.1136 | 0.3130 | 0.1461 | 0.6768 | 0.0902 | 79 | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrbm0p01_hb0p06_h0p04_kb0p03_k0p12_ab0p08_a0_ph0p1963` | 5-54 | 0.0522 | 0.0762 | 0.3197 | 0.1461 | 0.7142 | 0.0798 | 74 | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrbm0p01_hb0p06_h0p04_kb0p03_k0p1_ab0p08_a0p012_ph0p589` | 0-49 | 0.0471 | 0.1158 | 0.2946 | 0.1469 | 0.5586 | 0.0875 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p5_hrbm0p01_hb0p06_h0p04_kb0p03_k0p1_ab0p08_a0p012_ph0p589` | 5-54 | 0.0434 | 0.0752 | 0.2953 | 0.1467 | 0.5778 | 0.0776 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927` | 5-54 | 0.0565 | 0.0636 | 0.3313 | 0.1462 | 0.4800 | 0.0687 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927` | 0-49 | 0.0532 | 0.1089 | 0.3173 | 0.1471 | 0.5400 | 0.0843 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p01_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p589` | 5-54 | 0.0467 | 0.0678 | 0.2832 | 0.1475 | 0.5323 | 0.0682 | 110 | 94.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p01_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p589` | 0-49 | 0.0452 | 0.1101 | 0.2641 | 0.1479 | 0.5548 | 0.0772 | 115 | 90.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p1963` | 5-54 | 0.0537 | 0.0635 | 0.3299 | 0.1462 | 0.4481 | 0.0616 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p1963` | 0-49 | 0.0472 | 0.1097 | 0.3058 | 0.1462 | 0.4481 | 0.0718 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p05_kb0p06_k0p1_ab0p04_am0p015_ph0p589` | 5-54 | 0.0429 | 0.0678 | 0.2855 | 0.1473 | 0.4536 | 0.0701 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p05_kb0p06_k0p1_ab0p04_am0p015_ph0p589` | 0-49 | 0.0421 | 0.0969 | 0.2855 | 0.1473 | 0.4478 | 0.0748 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p1963` | 5-54 | 0.0503 | 0.0570 | 0.3001 | 0.1482 | 0.3657 | 0.0674 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p1963` | 0-49 | 0.0431 | 0.1136 | 0.2572 | 0.1482 | 0.3657 | 0.0731 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p01_hb0p08_h0p05_kb0p06_k0p12_ab0p04_a0_ph0p589` | 5-54 | 0.0543 | 0.0588 | 0.3190 | 0.1462 | 0.5280 | 0.0700 | 62 | 92.0000 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p01_hb0p08_h0p05_kb0p06_k0p12_ab0p04_a0_ph0p589` | 0-49 | 0.0467 | 0.1105 | 0.2944 | 0.1462 | 0.4694 | 0.0752 | 67 | 88.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_002.jsonl | `primitive_p0p55_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963` | 0-49 | 0.0467 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0p01_hb0p06_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p7854` | 0-49 | 0.0446 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0p01_hb0p06_h0p05_kb0p03_k0p08_ab0p08_a0p015_ph0p3927` | 0-49 | 0.0565 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0p01_hb0p06_h0p05_kb0p03_k0p08_ab0p08_a0p015_ph0p3927` | 5-54 | 0.0468 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrbm0p01_hb0p06_h0p04_kb0p06_k0p08_ab0p08_am0p012_ph0p3927` | 0-49 | 0.0623 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrbm0p01_hb0p08_h0p04_kb0p03_k0p12_ab0p04_am0p012_ph0p1963` | 0-49 | 0.0564 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrbm0p01_hb0p08_h0p04_kb0p03_k0p12_ab0p04_am0p012_ph0p1963` | 10-59 | 0.0525 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrbm0p01_hb0p08_h0p04_kb0p03_k0p12_ab0p04_am0p012_ph0p1963` | 5-54 | 0.0500 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrbm0p01_hb0p08_h0p04_kb0p03_k0p12_ab0p04_am0p012_ph0p1963` | 15-64 | 0.0489 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrbm0p01_hb0p08_h0p04_kb0p03_k0p12_ab0p04_am0p012_ph0p1963` | 20-69 | 0.0463 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p5_hrb0_hb0p04_h0p04_kb0p06_k0p1_ab0p08_am0p012_ph0p3927` | 0-49 | 0.0498 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p03_kb0p03_k0p1_ab0p08_a0_ph0p1963` | 0-49 | 0.0403 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p03_kb0p03_k0p1_ab0p08_a0_ph0p1963` | 0-49 | 0.0532 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p03_kb0p03_k0p1_ab0p08_a0_ph0p1963` | 5-54 | 0.0413 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p03_kb0p03_k0p1_ab0p08_a0_ph0p1963` | 10-59 | 0.0408 | `single_contact_pattern_dominates` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
