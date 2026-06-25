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

- mined_windows: `230`
- pass_curated_seed_windows: `25`
- review_motion_hints: `205`
- rejected_dataset_seeds: `0`
- curated_source_files: `1`
- curated_modes: `25`
- curated_source_mode_pairs: `25`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0` | 5-29 | 0.0699 | 0.0688 | 0.2531 | 0.1483 | 0.3905 | 0.0743 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 5-29 | 0.1036 | 0.0754 | 0.3310 | 0.1465 | 0.4681 | 0.0710 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p08_a0p009_ph0` | 5-29 | 0.0691 | 0.0797 | 0.2305 | 0.1496 | 0.3905 | 0.0619 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p3927` | 5-29 | 0.0766 | 0.0601 | 0.2448 | 0.1506 | 0.5672 | 0.0615 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p7854` | 5-29 | 0.0817 | 0.0684 | 0.2636 | 0.1508 | 0.5694 | 0.0634 | 75 | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p12_ab0p04_a0_ph0p3927` | 5-29 | 0.0453 | 0.0715 | 0.1550 | 0.1518 | 0.7022 | 0.0606 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p06_h0p03_kb0p03_k0p12_ab0p04_a0p009_ph0p3927` | 5-29 | 0.0416 | 0.0803 | 0.1529 | 0.1523 | 0.7022 | 0.0604 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0p3927` | 5-29 | 0.0516 | 0.0726 | 0.1892 | 0.1506 | 0.7022 | 0.0594 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p7854` | 5-29 | 0.0684 | 0.0609 | 0.2343 | 0.1505 | 0.7393 | 0.0655 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p04_h0p03_kb0p03_k0p12_ab0p04_a0p009_ph0` | 5-29 | 0.0438 | 0.0765 | 0.1727 | 0.1493 | 0.5858 | 0.0637 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p04_h0p05_kb0p03_k0p12_ab0p04_a0p015_ph0` | 5-29 | 0.0408 | 0.0757 | 0.1548 | 0.1500 | 0.5871 | 0.0654 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p04_h0p05_kb0p06_k0p08_ab0p04_a0p015_ph0` | 5-29 | 0.0528 | 0.0845 | 0.2143 | 0.1480 | 0.5616 | 0.0738 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p08_ab0p04_a0p009_ph0` | 5-29 | 0.0508 | 0.0690 | 0.1722 | 0.1493 | 0.3905 | 0.0639 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p3927` | 5-29 | 0.0496 | 0.0650 | 0.1800 | 0.1487 | 0.7022 | 0.0592 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p05_kb0p03_k0p08_ab0p08_a0_ph0p3927` | 5-29 | 0.0801 | 0.0773 | 0.2534 | 0.1494 | 0.5672 | 0.0611 | 54 | 84.0000 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p05_kb0p03_k0p12_ab0p04_am0p015_ph0` | 5-29 | 0.0506 | 0.0724 | 0.1638 | 0.1510 | 0.5871 | 0.0599 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p04_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p7854` | 5-29 | 0.0872 | 0.0700 | 0.2796 | 0.1478 | 0.4557 | 0.0686 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p03_kb0p03_k0p12_ab0p04_am0p009_ph0p7854` | 5-29 | 0.0482 | 0.0685 | 0.1798 | 0.1505 | 0.4557 | 0.0586 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0p7854` | 5-29 | 0.0558 | 0.0677 | 0.1985 | 0.1495 | 0.4575 | 0.0595 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0p08_am0p009_ph0p3927` | 5-29 | 0.0915 | 0.0733 | 0.2728 | 0.1489 | 0.2688 | 0.0633 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p12_ab0p08_am0p009_ph0p3927` | 5-29 | 0.0985 | 0.0822 | 0.2898 | 0.1486 | 0.3440 | 0.0597 | 50 | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p3927` | 5-29 | 0.0726 | 0.0647 | 0.2232 | 0.1498 | 0.2688 | 0.0594 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p04_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p3927` | 5-29 | 0.0738 | 0.0656 | 0.2536 | 0.1470 | 0.3440 | 0.0697 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0` | 5-29 | 0.0717 | 0.0868 | 0.2247 | 0.1480 | 0.4428 | 0.0622 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p08_a0_ph0p7854` | 5-29 | 0.0774 | 0.0817 | 0.2409 | 0.1485 | 0.3038 | 0.0589 | 79 | 84.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0` | 0-24 | 0.0802 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0` | 0-24 | 0.0676 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0` | 5-29 | 0.0497 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 0-24 | 0.0986 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 0-24 | 0.0908 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 5-29 | 0.0761 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 10-34 | 0.0665 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 15-39 | 0.0435 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p05_kb0p03_k0p12_ab0p04_a0p015_ph0p3927` | 0-24 | 0.0478 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p05_kb0p03_k0p12_ab0p04_a0p015_ph0p3927` | 0-24 | 0.0544 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p05_kb0p03_k0p12_ab0p04_a0p015_ph0p3927` | 10-34 | 0.0442 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p05_kb0p03_k0p12_ab0p04_a0p015_ph0p3927` | 5-29 | 0.0411 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p04_a0_ph0p3927` | 0-24 | 0.0459 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p04_a0_ph0p3927` | 0-24 | 0.0478 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p04_a0_ph0p3927` | 10-34 | 0.0452 | `single_contact_pattern_dominates` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
