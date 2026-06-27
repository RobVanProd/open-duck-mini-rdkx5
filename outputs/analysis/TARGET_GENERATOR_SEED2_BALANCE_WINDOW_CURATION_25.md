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

- mined_windows: `386`
- pass_curated_seed_windows: `45`
- review_motion_hints: `341`
- rejected_dataset_seeds: `0`
- curated_source_files: `1`
- curated_modes: `45`
- curated_source_mode_pairs: `45`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p03_k0p1_ab0p04_am0p015_ph0p589` | 5-29 | 0.0510 | 0.0549 | 0.1913 | 0.1514 | 0.6111 | 0.0652 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963` | 5-29 | 0.1005 | 0.0665 | 0.3001 | 0.1490 | 0.5652 | 0.0723 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0p01_hb0p06_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p7854` | 5-29 | 0.0699 | 0.0643 | 0.2438 | 0.1496 | 0.7393 | 0.0606 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0p01_hb0p06_h0p05_kb0p03_k0p08_ab0p08_a0p015_ph0p3927` | 5-29 | 0.0657 | 0.0723 | 0.2149 | 0.1506 | 0.5672 | 0.0650 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrb0p01_hb0p06_h0p05_kb0p03_k0p1_ab0p04_a0_ph0p1963` | 5-29 | 0.0413 | 0.0607 | 0.1595 | 0.1520 | 0.5697 | 0.0604 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p01_hb0p04_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927` | 5-29 | 0.0745 | 0.0630 | 0.2594 | 0.1481 | 0.7022 | 0.0687 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p04_a0_ph0p1963` | 5-29 | 0.0444 | 0.0729 | 0.1890 | 0.1497 | 0.5652 | 0.0687 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p01_hb0p04_h0p04_kb0p06_k0p08_ab0p04_am0p012_ph0p3927` | 5-29 | 0.0626 | 0.0682 | 0.2427 | 0.1483 | 0.4681 | 0.0748 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p01_hb0p04_h0p04_kb0p06_k0p1_ab0p04_a0_ph0p1963` | 5-29 | 0.0638 | 0.0657 | 0.2394 | 0.1482 | 0.4828 | 0.0736 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p01_hb0p06_h0p05_kb0p06_k0p08_ab0p04_a0_ph0p589` | 5-29 | 0.0525 | 0.0606 | 0.1928 | 0.1496 | 0.5684 | 0.0694 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p01_hb0p08_h0p04_kb0p03_k0p12_ab0p04_am0p012_ph0p1963` | 5-29 | 0.0480 | 0.0692 | 0.1637 | 0.1513 | 0.5652 | 0.0606 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p01_hb0p08_h0p04_kb0p06_k0p1_ab0p04_a0p012_ph0p3927` | 5-29 | 0.0469 | 0.0732 | 0.1644 | 0.1501 | 0.5851 | 0.0615 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hb0p04_h0p05_kb0p06_k0p1_ab0p04_a0p015_ph0p589` | 5-29 | 0.0449 | 0.0635 | 0.1931 | 0.1494 | 0.6270 | 0.0706 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p03_kb0p03_k0p1_ab0p08_a0_ph0p1963` | 5-29 | 0.0661 | 0.0706 | 0.2315 | 0.1490 | 0.5995 | 0.0666 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p04_kb0p03_k0p1_ab0p08_a0_ph0p7854` | 5-29 | 0.0581 | 0.0634 | 0.2143 | 0.1500 | 0.5862 | 0.0620 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p05_kb0p03_k0p1_ab0p08_a0_ph0p3927` | 5-29 | 0.0692 | 0.0635 | 0.2396 | 0.1497 | 0.6337 | 0.0691 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963` | 5-29 | 0.0922 | 0.0728 | 0.2953 | 0.1493 | 0.7194 | 0.0704 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0p01_hb0p06_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p1963` | 5-29 | 0.0713 | 0.0608 | 0.2443 | 0.1498 | 0.4796 | 0.0621 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0p01_hb0p06_h0p04_kb0p03_k0p12_ab0p08_a0p012_ph0p589` | 5-29 | 0.0674 | 0.0874 | 0.2387 | 0.1498 | 0.7089 | 0.0689 | 72 | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0p01_hb0p08_h0p05_kb0p06_k0p08_ab0p04_a0p015_ph0p589` | 5-29 | 0.0536 | 0.0724 | 0.1985 | 0.1511 | 0.6243 | 0.0611 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrbm0p01_hb0p06_h0p04_kb0p03_k0p12_ab0p08_a0_ph0p1963` | 5-29 | 0.0721 | 0.0761 | 0.2433 | 0.1488 | 0.7194 | 0.0688 | 99 | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrbm0p01_hb0p06_h0p04_kb0p03_k0p1_ab0p08_a0p012_ph0p589` | 5-29 | 0.0666 | 0.0709 | 0.2357 | 0.1487 | 0.5907 | 0.0648 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p04_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p589` | 5-29 | 0.0599 | 0.0714 | 0.2364 | 0.1485 | 0.5903 | 0.0671 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p03_k0p1_ab0p08_am0p009_ph0p7854` | 5-29 | 0.0768 | 0.0691 | 0.2418 | 0.1496 | 0.5693 | 0.0596 | 54 | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927` | 5-29 | 0.0684 | 0.0645 | 0.2144 | 0.1500 | 0.4950 | 0.0579 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p04_kb0p03_k0p1_ab0p08_am0p012_ph0p589` | 5-29 | 0.0844 | 0.0806 | 0.2622 | 0.1496 | 0.4919 | 0.0582 | 53 | 92.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p01_hb0p04_h0p04_kb0p03_k0p08_ab0p08_a0_ph0` | 5-29 | 0.0724 | 0.0711 | 0.2421 | 0.1498 | 0.4158 | 0.0786 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p01_hb0p06_h0p04_kb0p06_k0p08_ab0p04_a0p012_ph0p589` | 5-29 | 0.0482 | 0.0647 | 0.1889 | 0.1502 | 0.4291 | 0.0594 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p01_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p589` | 5-29 | 0.0555 | 0.0713 | 0.1816 | 0.1507 | 0.5903 | 0.0577 | 135 | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p01_hb0p08_h0p04_kb0p03_k0p1_ab0p04_a0_ph0p1963` | 5-29 | 0.0498 | 0.0700 | 0.1585 | 0.1520 | 0.4164 | 0.0641 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p04_a0_ph0p3927` | 5-29 | 0.0418 | 0.0702 | 0.1729 | 0.1500 | 0.4950 | 0.0737 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p01_hb0p04_h0p04_kb0p06_k0p08_ab0p04_a0p012_ph0p3927` | 5-29 | 0.0550 | 0.0693 | 0.2266 | 0.1482 | 0.4168 | 0.0720 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p04_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p589` | 5-29 | 0.0739 | 0.0667 | 0.2564 | 0.1480 | 0.4030 | 0.0700 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p04_kb0p03_k0p12_ab0p08_a0_ph0p1963` | 5-29 | 0.0951 | 0.0755 | 0.2798 | 0.1479 | 0.3704 | 0.0724 | 70 | 84.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p04_kb0p06_k0p12_ab0p04_a0_ph0` | 5-29 | 0.0774 | 0.0706 | 0.2422 | 0.1488 | 0.3746 | 0.0670 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p1963` | 5-29 | 0.0920 | 0.0834 | 0.2557 | 0.1495 | 0.4423 | 0.0582 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p03_kb0p03_k0p08_ab0p04_a0p009_ph0` | 5-29 | 0.0475 | 0.0726 | 0.1543 | 0.1526 | 0.2721 | 0.0635 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p04_kb0p03_k0p12_ab0p04_a0_ph0p7854` | 5-29 | 0.0510 | 0.0667 | 0.1878 | 0.1511 | 0.4557 | 0.0573 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p04_kb0p03_k0p1_ab0p04_a0p012_ph0p3927` | 5-29 | 0.0442 | 0.0648 | 0.1490 | 0.1517 | 0.3584 | 0.0631 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p05_kb0p06_k0p1_ab0p04_am0p015_ph0p589` | 5-29 | 0.0969 | 0.0705 | 0.2754 | 0.1494 | 0.4453 | 0.0700 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p1963` | 5-29 | 0.0713 | 0.0730 | 0.2160 | 0.1503 | 0.3031 | 0.0607 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p01_hb0p04_h0p04_kb0p06_k0p08_ab0p04_a0_ph0p7854` | 5-29 | 0.0575 | 0.0714 | 0.2315 | 0.1482 | 0.3577 | 0.0724 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p01_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p015_ph0` | 5-29 | 0.0623 | 0.0644 | 0.1891 | 0.1520 | 0.4196 | 0.0615 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p01_hb0p08_h0p04_kb0p06_k0p08_ab0p04_a0p012_ph0p589` | 5-29 | 0.0553 | 0.0724 | 0.1729 | 0.1499 | 0.3562 | 0.0599 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p01_hb0p08_h0p05_kb0p06_k0p12_ab0p04_a0_ph0p589` | 5-29 | 0.0695 | 0.0869 | 0.2021 | 0.1498 | 0.4510 | 0.0569 | 87 | 84.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p1_ab0p04_am0p009_ph0p3927` | 0-24 | 0.0474 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p1_ab0p04_am0p009_ph0p3927` | 0-24 | 0.0510 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p1_ab0p04_am0p009_ph0p3927` | 10-34 | 0.0448 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p1_ab0p04_am0p009_ph0p3927` | 15-39 | 0.0418 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p1_ab0p04_am0p009_ph0p3927` | 5-29 | 0.0401 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p03_k0p1_ab0p04_am0p015_ph0p589` | 0-24 | 0.0637 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p03_k0p1_ab0p04_am0p015_ph0p589` | 0-24 | 0.0493 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p03_k0p1_ab0p04_am0p015_ph0p589` | 10-34 | 0.0411 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p08_ab0p04_a0p015_ph0` | 20-44 | 0.0537 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p08_ab0p04_a0p015_ph0` | 15-39 | 0.0474 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p08_ab0p04_a0p015_ph0` | 10-34 | 0.0464 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p08_ab0p04_a0p015_ph0` | 25-49 | 0.0443 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p55_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963` | 0-24 | 0.0973 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p55_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963` | 10-34 | 0.0745 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p55_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963` | 15-39 | 0.0426 | `single_contact_pattern_dominates` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
