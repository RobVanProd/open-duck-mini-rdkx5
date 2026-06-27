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

- mined_windows: `675`
- pass_curated_seed_windows: `82`
- review_motion_hints: `593`
- rejected_dataset_seeds: `0`
- curated_source_files: `1`
- curated_modes: `82`
- curated_source_mode_pairs: `82`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0025_ph0p32` | 5-29 | 0.0789 | 0.0750 | 0.2527 | 0.1486 | 0.6062 | 0.0579 | 55 | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 5-29 | 0.0773 | 0.0748 | 0.2434 | 0.1495 | 0.6159 | 0.0554 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927` | 5-29 | 0.0634 | 0.0670 | 0.2001 | 0.1503 | 0.5839 | 0.0576 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p47` | 5-29 | 0.0646 | 0.0670 | 0.2074 | 0.1498 | 0.5863 | 0.0558 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p003_ph0p3927` | 5-29 | 0.0638 | 0.0902 | 0.2014 | 0.1501 | 0.6813 | 0.0567 | 79 | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p0025_ph0p52` | 5-29 | 0.0588 | 0.0713 | 0.1916 | 0.1504 | 0.7155 | 0.0577 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p04_am0p007_ph0p32` | 5-29 | 0.0632 | 0.0792 | 0.1928 | 0.1509 | 0.8083 | 0.0534 | 66 | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p47` | 5-29 | 0.0716 | 0.0657 | 0.2227 | 0.1503 | 0.5863 | 0.0551 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p009_ph0p32` | 5-29 | 0.0907 | 0.0745 | 0.2743 | 0.1484 | 0.7073 | 0.0559 | 53 | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0_ph0p3927` | 5-29 | 0.0573 | 0.0621 | 0.1802 | 0.1509 | 0.7786 | 0.0560 | 109 | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p006_ph0p3927` | 5-29 | 0.0799 | 0.0675 | 0.2499 | 0.1491 | 0.4866 | 0.0563 | 56 | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p005_ph0p36` | 5-29 | 0.0616 | 0.0814 | 0.2009 | 0.1498 | 0.5535 | 0.0572 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p005_ph0p52` | 5-29 | 0.0815 | 0.0664 | 0.2617 | 0.1483 | 0.6132 | 0.0547 | 52 | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0075_ph0p47` | 5-29 | 0.0867 | 0.0652 | 0.2765 | 0.1478 | 0.5863 | 0.0567 | 54 | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p47` | 5-29 | 0.0655 | 0.0638 | 0.2117 | 0.1497 | 0.5863 | 0.0589 | 65 | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p47` | 5-29 | 0.0786 | 0.0932 | 0.2402 | 0.1494 | 0.6840 | 0.0563 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0105_ph0p36` | 5-29 | 0.0905 | 0.0665 | 0.2890 | 0.1480 | 0.4612 | 0.0629 | 58 | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p43` | 5-29 | 0.0732 | 0.0714 | 0.2315 | 0.1495 | 0.6159 | 0.0551 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p009_ph0p43` | 5-29 | 0.0817 | 0.0789 | 0.2580 | 0.1484 | 0.7185 | 0.0544 | 51 | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p009_ph0p47` | 5-29 | 0.0803 | 0.0764 | 0.2568 | 0.1484 | 0.6840 | 0.0545 | 50 | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p06_am0p012_ph0p52` | 5-29 | 0.1020 | 0.0839 | 0.3072 | 0.1475 | 0.8177 | 0.0584 | 50 | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p32` | 5-29 | 0.0668 | 0.0583 | 0.2179 | 0.1492 | 0.5052 | 0.0601 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p025_kb0p06_k0p16_ab0p04_am0p01_ph0p36` | 5-29 | 0.0736 | 0.0948 | 0.2237 | 0.1496 | 0.6344 | 0.0530 | 86 | 88.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p52` | 5-29 | 0.0659 | 0.0821 | 0.1983 | 0.1502 | 0.6218 | 0.0564 | 66 | 88.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p36` | 5-29 | 0.0948 | 0.0705 | 0.2867 | 0.1481 | 0.3965 | 0.0651 | 56 | 88.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927` | 5-29 | 0.0666 | 0.0810 | 0.2070 | 0.1501 | 0.5234 | 0.0583 | 83 | 88.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p006_ph0p36` | 5-29 | 0.0662 | 0.0618 | 0.2056 | 0.1501 | 0.3965 | 0.0575 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p007_ph0p43` | 5-29 | 0.0654 | 0.0670 | 0.1987 | 0.1509 | 0.4852 | 0.0567 | 70 | 88.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p36` | 5-29 | 0.0906 | 0.0634 | 0.2650 | 0.1494 | 0.4758 | 0.0563 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p43` | 5-29 | 0.0600 | 0.0744 | 0.1825 | 0.1508 | 0.5660 | 0.0559 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p04_am0p007_ph0p32` | 5-29 | 0.0695 | 0.0774 | 0.2096 | 0.1504 | 0.6122 | 0.0530 | 62 | 88.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p06_am0p0105_ph0p47` | 5-29 | 0.0995 | 0.0768 | 0.2891 | 0.1487 | 0.6857 | 0.0537 | 50 | 84.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p003_ph0p52` | 5-29 | 0.0938 | 0.0662 | 0.2835 | 0.1482 | 0.5330 | 0.0640 | 54 | 88.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p009_ph0p36` | 5-29 | 0.0929 | 0.0688 | 0.2804 | 0.1486 | 0.3965 | 0.0575 | 58 | 84.0000 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0075_ph0p52` | 5-29 | 0.0803 | 0.0661 | 0.2563 | 0.1482 | 0.5330 | 0.0548 | 55 | 84.0000 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p32` | 5-29 | 0.1009 | 0.0772 | 0.3029 | 0.1477 | 0.4591 | 0.0574 | 54 | 84.0000 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p005_ph0p3927` | 5-29 | 0.0645 | 0.0647 | 0.2065 | 0.1498 | 0.4362 | 0.0585 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p06_a0_ph0p3927` | 5-29 | 0.0861 | 0.0777 | 0.2745 | 0.1478 | 0.4362 | 0.0590 | 57 | 84.0000 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p52` | 5-29 | 0.0826 | 0.0944 | 0.2446 | 0.1491 | 0.6218 | 0.0555 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p009_ph0p3927` | 5-29 | 0.0690 | 0.0746 | 0.2169 | 0.1498 | 0.4362 | 0.0583 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p009_ph0p52` | 5-29 | 0.0875 | 0.0667 | 0.2754 | 0.1481 | 0.4442 | 0.0604 | 64 | 84.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p52` | 5-29 | 0.0633 | 0.0638 | 0.1978 | 0.1500 | 0.4449 | 0.0572 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p005_ph0p3927` | 5-29 | 0.0853 | 0.0720 | 0.2698 | 0.1480 | 0.3897 | 0.0595 | 64 | 88.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p01_ph0p32` | 5-29 | 0.0999 | 0.0711 | 0.3020 | 0.1478 | 0.2953 | 0.0594 | 63 | 92.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p32` | 5-29 | 0.0888 | 0.0779 | 0.2712 | 0.1481 | 0.3543 | 0.0614 | 55 | 84.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0_ph0p47` | 5-29 | 0.0646 | 0.0661 | 0.1985 | 0.1500 | 0.4016 | 0.0581 | 90 | 88.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p012_ph0p43` | 5-29 | 0.0791 | 0.0891 | 0.2335 | 0.1495 | 0.4936 | 0.0535 | 102 | 88.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p009_ph0p43` | 5-29 | 0.0998 | 0.0676 | 0.3001 | 0.1478 | 0.3526 | 0.0651 | 62 | 88.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p0075_ph0p47` | 5-29 | 0.0691 | 0.0737 | 0.2135 | 0.1502 | 0.4685 | 0.0541 | 69 | 88.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p01_ph0p36` | 5-29 | 0.1030 | 0.0686 | 0.3025 | 0.1484 | 0.3729 | 0.0573 | 59 | 88.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p0035_ph0p36` | 5-29 | 0.0708 | 0.0803 | 0.2062 | 0.1503 | 0.5221 | 0.0542 | 64 | 88.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p06_am0p0035_ph0p43` | 5-29 | 0.0840 | 0.0738 | 0.2542 | 0.1487 | 0.5641 | 0.0534 | 50 | 84.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p014_ph0p3927` | 5-29 | 0.0990 | 0.0665 | 0.2851 | 0.1493 | 0.3897 | 0.0609 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p007_ph0p3927` | 5-29 | 0.0869 | 0.0682 | 0.2606 | 0.1488 | 0.3897 | 0.0585 | 60 | 84.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p003_ph0p32` | 5-29 | 0.0681 | 0.0864 | 0.2052 | 0.1505 | 0.4134 | 0.0563 | 68 | 88.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p04_am0p003_ph0p47` | 5-29 | 0.0685 | 0.0825 | 0.2074 | 0.1504 | 0.5354 | 0.0525 | 62 | 88.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p006_ph0p43` | 5-29 | 0.0927 | 0.0705 | 0.2799 | 0.1483 | 0.3526 | 0.0614 | 62 | 84.0000 |
| seed_000.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p3927` | 5-29 | 0.0680 | 0.0677 | 0.2238 | 0.1490 | 0.4676 | 0.0588 | 79 | 92.0000 |
| seed_000.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p01_ph0p43` | 5-29 | 0.0994 | 0.0784 | 0.2987 | 0.1474 | 0.4936 | 0.0540 | 57 | 84.0000 |
| seed_000.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p025_kb0p06_k0p16_ab0p04_am0p01_ph0p36` | 5-29 | 0.0738 | 0.0968 | 0.2192 | 0.1495 | 0.5967 | 0.0518 | 75 | 88.0000 |
| seed_000.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p0025_ph0p47` | 5-29 | 0.0794 | 0.0717 | 0.2527 | 0.1482 | 0.3346 | 0.0567 | 60 | 84.0000 |
| seed_000.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p006_ph0p3927` | 5-29 | 0.0873 | 0.0748 | 0.2732 | 0.1479 | 0.3897 | 0.0603 | 64 | 84.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0025_ph0p3927` | 5-29 | 0.0794 | 0.0766 | 0.2561 | 0.1483 | 0.4950 | 0.0586 | 52 | 84.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p01_ph0p36` | 5-29 | 0.0914 | 0.0669 | 0.2770 | 0.1482 | 0.5549 | 0.0523 | 53 | 84.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p16_ab0p04_am0p0075_ph0p36` | 5-29 | 0.0667 | 0.0812 | 0.2127 | 0.1497 | 0.6341 | 0.0549 | 71 | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p04_a0_ph0p47` | 5-29 | 0.0596 | 0.0714 | 0.1955 | 0.1500 | 0.4734 | 0.0588 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p01_ph0p3927` | 5-29 | 0.0651 | 0.0591 | 0.2079 | 0.1502 | 0.4125 | 0.0579 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p007_ph0p36` | 5-29 | 0.0849 | 0.0708 | 0.2643 | 0.1483 | 0.4756 | 0.0591 | 53 | 84.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0105_ph0p32` | 5-29 | 0.0876 | 0.0656 | 0.2712 | 0.1482 | 0.5994 | 0.0607 | 57 | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p16_ab0p04_am0p0035_ph0p32` | 5-29 | 0.0647 | 0.0877 | 0.1981 | 0.1502 | 0.7992 | 0.0539 | 74 | 84.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p006_ph0p47` | 5-29 | 0.0890 | 0.0770 | 0.2717 | 0.1482 | 0.6628 | 0.0550 | 50 | 84.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p47` | 5-29 | 0.0835 | 0.0630 | 0.2559 | 0.1497 | 0.5681 | 0.0550 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p006_ph0p36` | 5-29 | 0.0719 | 0.0682 | 0.2194 | 0.1502 | 0.4756 | 0.0562 | 73 | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p52` | 5-29 | 0.0727 | 0.0657 | 0.2234 | 0.1502 | 0.6233 | 0.0547 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p012_ph0p52` | 5-29 | 0.0738 | 0.0564 | 0.2298 | 0.1500 | 0.5194 | 0.0556 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0025_ph0p36` | 5-29 | 0.0811 | 0.0774 | 0.2594 | 0.1481 | 0.4756 | 0.0573 | 53 | 84.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p0025_ph0p3927` | 5-29 | 0.0640 | 0.0959 | 0.2009 | 0.1498 | 0.5775 | 0.0548 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p04_am0p014_ph0p36` | 5-29 | 0.0772 | 0.0936 | 0.2330 | 0.1494 | 0.6341 | 0.0540 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p06_am0p007_ph0p36` | 5-29 | 0.0834 | 0.0946 | 0.2583 | 0.1483 | 0.6341 | 0.0546 | 50 | 84.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0_ph0p36` | 5-29 | 0.0637 | 0.0699 | 0.2077 | 0.1496 | 0.4756 | 0.0608 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p04_am0p012_ph0p32` | 5-29 | 0.0790 | 0.0934 | 0.2382 | 0.1491 | 0.7992 | 0.0531 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p06_am0p012_ph0p36` | 5-29 | 0.0941 | 0.0826 | 0.2861 | 0.1480 | 0.6341 | 0.0541 | 53 | 84.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0025_ph0p32` | 0-24 | 0.0769 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0025_ph0p32` | 10-34 | 0.0642 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0025_ph0p32` | 0-24 | 0.0602 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p16_ab0p06_am0p0075_ph0p52` | 0-24 | 0.0777 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 0-24 | 0.0783 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 10-34 | 0.0602 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 15-39 | 0.0476 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 0-24 | 0.0538 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 25-49 | 0.0518 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 20-44 | 0.0517 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 10-34 | 0.0510 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 30-54 | 0.0501 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 15-39 | 0.0488 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 5-29 | 0.0463 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 35-59 | 0.0406 | `single_contact_pattern_dominates` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
