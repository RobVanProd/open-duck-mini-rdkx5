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

- mined_windows: `624`
- pass_curated_seed_windows: `80`
- review_motion_hints: `544`
- rejected_dataset_seeds: `0`
- curated_source_files: `2`
- curated_modes: `70`
- curated_source_mode_pairs: `71`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 5-29 | 0.0677 | 0.0760 | 0.2351 | 0.1489 | 0.4807 | 0.0585 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 5-29 | 0.0735 | 0.0738 | 0.2505 | 0.1487 | 0.6307 | 0.0590 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 5-29 | 0.0770 | 0.0882 | 0.2647 | 0.1479 | 0.3012 | 0.0729 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 5-29 | 0.0816 | 0.0749 | 0.2718 | 0.1479 | 0.5550 | 0.0586 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 5-29 | 0.0912 | 0.0957 | 0.3042 | 0.1471 | 0.5769 | 0.0739 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p3_ls1` | 5-29 | 0.0811 | 0.0849 | 0.2769 | 0.1475 | 0.4487 | 0.0773 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p3927_ld0p3_ls1` | 5-29 | 0.0774 | 0.0900 | 0.2650 | 0.1479 | 0.4487 | 0.0769 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 5-29 | 0.0675 | 0.0787 | 0.2365 | 0.1491 | 0.4215 | 0.0602 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 5-29 | 0.0630 | 0.0848 | 0.2254 | 0.1493 | 0.4215 | 0.0606 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 5-29 | 0.0746 | 0.0939 | 0.2583 | 0.1480 | 0.4215 | 0.0771 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p22_ls0p65` | 5-29 | 0.0716 | 0.0802 | 0.2495 | 0.1483 | 0.6307 | 0.0582 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 5-29 | 0.0865 | 0.0892 | 0.2819 | 0.1475 | 0.4215 | 0.0732 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p02_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p3_ls1` | 5-29 | 0.0774 | 0.0972 | 0.2678 | 0.1479 | 0.2996 | 0.0760 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p3_ls1` | 5-29 | 0.0914 | 0.1081 | 0.2957 | 0.1468 | 0.5173 | 0.0751 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 5-29 | 0.0811 | 0.0904 | 0.2700 | 0.1475 | 0.3575 | 0.0734 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p47_ld0p22_ls1` | 5-29 | 0.0824 | 0.0930 | 0.2803 | 0.1476 | 0.4181 | 0.0715 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 5-29 | 0.0638 | 0.0797 | 0.2258 | 0.1487 | 0.4575 | 0.0583 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p47_ld0p3_ls0p65` | 5-29 | 0.0641 | 0.0753 | 0.2271 | 0.1487 | 0.5550 | 0.0600 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p32_ld0p3_ls0p65` | 5-29 | 0.0809 | 0.0941 | 0.2809 | 0.1469 | 0.5342 | 0.0592 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 5-29 | 0.0881 | 0.1058 | 0.3007 | 0.1467 | 0.4794 | 0.0765 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 5-29 | 0.0928 | 0.0879 | 0.3115 | 0.1461 | 0.6601 | 0.0626 | None | 72.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 10-34 | 0.0790 | 0.0817 | 0.3367 | 0.1458 | 0.5529 | 0.0629 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 5-29 | 0.0864 | 0.0881 | 0.2918 | 0.1465 | 0.4821 | 0.0596 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 10-34 | 0.0727 | 0.0701 | 0.3149 | 0.1464 | 0.4731 | 0.0604 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p32_ld0p22_ls0p65` | 5-29 | 0.0768 | 0.0808 | 0.2542 | 0.1479 | 0.4807 | 0.0590 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65` | 5-29 | 0.0731 | 0.0886 | 0.2540 | 0.1475 | 0.5134 | 0.0596 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65` | 15-39 | 0.0706 | 0.0602 | 0.2538 | 0.1478 | 0.4740 | 0.0756 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65` | 20-44 | 0.0703 | 0.0602 | 0.2657 | 0.1478 | 0.5134 | 0.0779 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65` | 10-34 | 0.0659 | 0.0602 | 0.2154 | 0.1485 | 0.4819 | 0.0620 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 5-29 | 0.0678 | 0.0770 | 0.2373 | 0.1480 | 0.6868 | 0.0631 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 5-29 | 0.0757 | 0.0982 | 0.2354 | 0.1495 | 0.2673 | 0.0642 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 5-29 | 0.0886 | 0.0925 | 0.2718 | 0.1476 | 0.3777 | 0.0714 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 5-29 | 0.0861 | 0.0818 | 0.2594 | 0.1486 | 0.2686 | 0.0686 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls0p65` | 5-29 | 0.0700 | 0.0786 | 0.2258 | 0.1498 | 0.3777 | 0.0582 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p22_ls0p65` | 5-29 | 0.0670 | 0.0797 | 0.2188 | 0.1498 | 0.3777 | 0.0585 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 5-29 | 0.0772 | 0.0803 | 0.2454 | 0.1493 | 0.3706 | 0.0580 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p32_ld0p22_ls0p65` | 5-29 | 0.0776 | 0.0780 | 0.2497 | 0.1485 | 0.3865 | 0.0591 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 5-29 | 0.0941 | 0.0955 | 0.2880 | 0.1472 | 0.3777 | 0.0741 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 5-29 | 0.0963 | 0.0936 | 0.2928 | 0.1469 | 0.3777 | 0.0734 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p22_ls1` | 5-29 | 0.0830 | 0.0901 | 0.2550 | 0.1482 | 0.3752 | 0.0696 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 5-29 | 0.0677 | 0.0853 | 0.2252 | 0.1492 | 0.3865 | 0.0606 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls1` | 5-29 | 0.0748 | 0.0933 | 0.2294 | 0.1499 | 0.3742 | 0.0634 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrphm1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p3_ls1` | 5-29 | 0.0781 | 0.0967 | 0.2585 | 0.1478 | 0.2701 | 0.0694 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p47_ld0p22_ls0p65` | 5-29 | 0.0731 | 0.0870 | 0.2366 | 0.1490 | 0.3861 | 0.0582 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls1` | 5-29 | 0.0919 | 0.1030 | 0.2796 | 0.1479 | 0.3760 | 0.0729 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p22_ls1` | 5-29 | 0.0849 | 0.0952 | 0.2632 | 0.1483 | 0.3752 | 0.0679 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p03_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls1` | 5-29 | 0.0792 | 0.0980 | 0.2505 | 0.1484 | 0.3782 | 0.0682 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 5-29 | 0.0965 | 0.1117 | 0.2907 | 0.1466 | 0.4310 | 0.0707 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 5-29 | 0.0975 | 0.1151 | 0.2943 | 0.1462 | 0.4310 | 0.0739 | None | 76.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 10-34 | 0.0814 | 0.1015 | 0.3449 | 0.1456 | 0.4324 | 0.0792 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 5-29 | 0.0718 | 0.0891 | 0.2371 | 0.1482 | 0.4323 | 0.0597 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 5-29 | 0.0625 | 0.0775 | 0.2084 | 0.1498 | 0.4317 | 0.0634 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p22_ls0p65` | 5-29 | 0.0594 | 0.0822 | 0.2021 | 0.1497 | 0.4305 | 0.0635 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p32_ld0p3_ls0p65` | 5-29 | 0.0797 | 0.0831 | 0.2370 | 0.1501 | 0.3393 | 0.0616 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 5-29 | 0.1011 | 0.0754 | 0.2900 | 0.1481 | 0.3767 | 0.0654 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 5-29 | 0.0764 | 0.0820 | 0.2403 | 0.1498 | 0.2680 | 0.0605 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p22_ls1` | 5-29 | 0.0807 | 0.0932 | 0.2396 | 0.1513 | 0.2393 | 0.0652 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 5-29 | 0.0819 | 0.0823 | 0.2489 | 0.1493 | 0.3429 | 0.0665 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 5-29 | 0.0928 | 0.0778 | 0.2791 | 0.1489 | 0.2680 | 0.0682 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls1` | 5-29 | 0.0876 | 0.0906 | 0.2476 | 0.1511 | 0.3283 | 0.0669 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrphm1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls1` | 5-29 | 0.0710 | 0.0935 | 0.2241 | 0.1501 | 0.2313 | 0.0674 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrphm1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p3_ls0p65` | 5-29 | 0.0682 | 0.0715 | 0.2189 | 0.1497 | 0.2930 | 0.0581 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 5-29 | 0.0852 | 0.0959 | 0.2486 | 0.1510 | 0.2926 | 0.0646 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 5-29 | 0.0912 | 0.0953 | 0.2694 | 0.1488 | 0.2940 | 0.0658 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 5-29 | 0.0772 | 0.0905 | 0.2290 | 0.1502 | 0.2775 | 0.0674 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls1` | 5-29 | 0.0741 | 0.0912 | 0.2219 | 0.1497 | 0.3350 | 0.0683 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p22_ls0p65` | 5-29 | 0.0728 | 0.0875 | 0.2315 | 0.1492 | 0.3829 | 0.0585 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p22_ls0p65` | 10-34 | 0.0576 | 0.0552 | 0.2507 | 0.1481 | 0.4048 | 0.0577 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p22_ls0p65` | 15-39 | 0.0422 | 0.0428 | 0.2564 | 0.1481 | 0.3837 | 0.0577 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 5-29 | 0.0999 | 0.1014 | 0.2908 | 0.1488 | 0.3902 | 0.0715 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 10-34 | 0.0819 | 0.0898 | 0.3431 | 0.1450 | 1.5000 | 0.0764 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 5-29 | 0.0975 | 0.1099 | 0.2945 | 0.1476 | 0.3920 | 0.0686 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 10-34 | 0.0826 | 0.1005 | 0.3410 | 0.1451 | 0.3987 | 0.0750 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls1` | 5-29 | 0.0928 | 0.0958 | 0.2738 | 0.1488 | 0.3875 | 0.0681 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls1` | 5-29 | 0.0739 | 0.0960 | 0.2235 | 0.1511 | 0.3752 | 0.0651 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p3_ls1` | 5-29 | 0.0876 | 0.1013 | 0.2655 | 0.1495 | 0.3902 | 0.0699 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p47_ld0p22_ls0p65` | 5-29 | 0.0678 | 0.0818 | 0.2233 | 0.1490 | 0.3875 | 0.0590 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 5-29 | 0.0716 | 0.0929 | 0.2247 | 0.1501 | 0.3825 | 0.0621 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls1` | 5-29 | 0.0755 | 0.0986 | 0.2207 | 0.1507 | 0.3653 | 0.0697 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p22_ls1` | 5-29 | 0.0774 | 0.0866 | 0.2272 | 0.1494 | 0.3902 | 0.0711 | None | 84.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 0-24 | 0.0666 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 10-34 | 0.0551 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 15-39 | 0.0479 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 10-34 | 0.0644 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 15-39 | 0.0637 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 20-44 | 0.0589 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 0-24 | 0.0547 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 5-29 | 0.0504 | `high_lateral_velocity, single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 25-49 | 0.0472 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 0-24 | 0.0724 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 10-34 | 0.0591 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 15-39 | 0.0481 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 10-34 | 0.0622 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 15-39 | 0.0599 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 0-24 | 0.0572 | `high_lateral_velocity` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
