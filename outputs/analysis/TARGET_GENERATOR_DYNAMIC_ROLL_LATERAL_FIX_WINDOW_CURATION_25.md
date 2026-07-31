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

- mined_windows: `1456`
- pass_curated_seed_windows: `318`
- review_motion_hints: `1138`
- rejected_dataset_seeds: `0`
- curated_source_files: `2`
- curated_modes: `156`
- curated_source_mode_pairs: `177`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p47_ld0p36_ls0p55` | 5-29 | 0.0806 | 0.0849 | 0.2774 | 0.1465 | 0.5841 | 0.0611 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p37_ld0p24_ls0p75` | 5-29 | 0.0744 | 0.0890 | 0.2535 | 0.1483 | 0.3857 | 0.0593 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p75` | 5-29 | 0.0755 | 0.0867 | 0.2672 | 0.1474 | 0.4505 | 0.0606 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p42_ld0p3_ls1` | 5-29 | 0.0838 | 0.0992 | 0.2867 | 0.1470 | 0.4573 | 0.0782 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p34_ld0p36_ls1` | 5-29 | 0.0915 | 0.0992 | 0.3092 | 0.1462 | 0.3913 | 0.0764 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p34_ld0p36_ls1` | 10-34 | 0.0748 | 0.0890 | 0.3364 | 0.1462 | 0.3856 | 0.0774 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p34_ld0p36_ls1` | 15-39 | 0.0600 | 0.0778 | 0.3364 | 0.1456 | 0.3856 | 0.0759 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p3_ls0p55` | 5-29 | 0.0733 | 0.0830 | 0.2530 | 0.1480 | 0.5060 | 0.0600 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p42_ld0p3_ls0p65` | 5-29 | 0.0732 | 0.0908 | 0.2588 | 0.1473 | 0.6510 | 0.0618 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p55` | 5-29 | 0.0806 | 0.0820 | 0.2769 | 0.1469 | 0.5571 | 0.0619 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p55` | 10-34 | 0.0676 | 0.0652 | 0.3029 | 0.1466 | 0.5433 | 0.0620 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p55` | 15-39 | 0.0534 | 0.0611 | 0.3085 | 0.1466 | 0.5332 | 0.0686 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p24_ls0p75` | 5-29 | 0.0741 | 0.0877 | 0.2609 | 0.1473 | 0.5017 | 0.0609 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p24_ls0p75` | 10-34 | 0.0609 | 0.0623 | 0.2906 | 0.1472 | 0.5017 | 0.0622 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p24_ls0p75` | 15-39 | 0.0517 | 0.0470 | 0.2918 | 0.1472 | 0.5017 | 0.0713 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0p7854_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p42_ld0p24_ls0p75` | 5-29 | 0.0802 | 0.0899 | 0.2787 | 0.1469 | 0.4650 | 0.0586 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p24_ls0p75` | 5-29 | 0.0894 | 0.0936 | 0.3033 | 0.1464 | 0.4579 | 0.0627 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p37_ld0p24_ls1` | 5-29 | 0.0767 | 0.1023 | 0.2653 | 0.1479 | 0.4242 | 0.0716 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p36_ls1` | 5-29 | 0.0922 | 0.1042 | 0.3113 | 0.1461 | 0.5062 | 0.0770 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p42_ld0p3_ls1` | 5-29 | 0.0831 | 0.1025 | 0.2885 | 0.1467 | 0.4317 | 0.0783 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p42_ld0p3_ls1` | 10-34 | 0.0669 | 0.0801 | 0.3130 | 0.1467 | 0.4317 | 0.0819 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p42_ld0p3_ls1` | 15-39 | 0.0537 | 0.0706 | 0.3130 | 0.1467 | 0.4297 | 0.0740 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p34_ld0p24_ls0p55` | 5-29 | 0.0656 | 0.0839 | 0.2332 | 0.1481 | 0.5089 | 0.0612 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p36_ls1` | 5-29 | 0.0922 | 0.1063 | 0.3087 | 0.1462 | 0.5865 | 0.0742 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p47_ld0p36_ls1` | 5-29 | 0.0891 | 0.1035 | 0.3038 | 0.1463 | 1.4137 | 0.0766 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p47_ld0p36_ls1` | 10-34 | 0.0724 | 0.0868 | 0.3251 | 0.1463 | 1.2017 | 0.0796 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p47_ld0p36_ls1` | 15-39 | 0.0607 | 0.0881 | 0.3257 | 0.1455 | 1.2017 | 0.0718 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p9_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55` | 5-29 | 0.0624 | 0.0812 | 0.2215 | 0.1488 | 0.5062 | 0.0612 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm1p05_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0_ph0p47_ld0p3_ls0p55` | 5-29 | 0.0628 | 0.0798 | 0.2306 | 0.1480 | 0.4338 | 0.0596 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm1p05_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p37_ld0p3_ls0p65` | 5-29 | 0.0704 | 0.0914 | 0.2480 | 0.1480 | 0.5062 | 0.0618 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p36_ls0p65` | 5-29 | 0.0827 | 0.0953 | 0.2787 | 0.1470 | 0.5159 | 0.0689 | None | 68.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p36_ls0p65` | 10-34 | 0.0681 | 0.0733 | 0.3079 | 0.1467 | 0.5159 | 0.0691 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p36_ls0p65` | 15-39 | 0.0540 | 0.0422 | 0.3123 | 0.1467 | 0.5140 | 0.0693 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p75` | 5-29 | 0.0834 | 0.0861 | 0.2907 | 0.1465 | 0.5267 | 0.0619 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p75` | 10-34 | 0.0674 | 0.0827 | 0.3123 | 0.1464 | 0.5263 | 0.0634 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p36_ls0p55` | 5-29 | 0.0853 | 0.0947 | 0.2822 | 0.1464 | 0.5291 | 0.0606 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p42_ld0p3_ls0p65` | 5-29 | 0.0821 | 0.0967 | 0.2895 | 0.1462 | 0.5787 | 0.0632 | None | 76.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p42_ld0p3_ls0p65` | 10-34 | 0.0682 | 0.0896 | 0.3145 | 0.1461 | 0.5267 | 0.0634 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p34_ld0p24_ls0p55` | 5-29 | 0.0815 | 0.0856 | 0.2701 | 0.1465 | 0.5726 | 0.0598 | None | 72.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p34_ld0p24_ls0p55` | 10-34 | 0.0696 | 0.0683 | 0.2976 | 0.1463 | 0.5455 | 0.0607 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p34_ld0p24_ls0p55` | 15-39 | 0.0585 | 0.0661 | 0.3114 | 0.1463 | 0.5300 | 0.0666 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p34_ld0p24_ls0p55` | 10-34 | 0.0637 | 0.0666 | 0.2263 | 0.1477 | 0.5455 | 0.0650 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p52_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p3_ls0p65` | 5-29 | 0.0766 | 0.1031 | 0.2702 | 0.1467 | 0.5294 | 0.0594 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p52_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p3_ls0p65` | 10-34 | 0.0631 | 0.0726 | 0.2956 | 0.1465 | 0.5294 | 0.0620 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p52_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p3_ls0p65` | 15-39 | 0.0508 | 0.0569 | 0.2983 | 0.1465 | 0.5234 | 0.0670 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls1` | 5-29 | 0.0801 | 0.1040 | 0.2786 | 0.1468 | 0.5242 | 0.0770 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p75` | 5-29 | 0.0854 | 0.1019 | 0.3010 | 0.1456 | 0.5296 | 0.0662 | None | 84.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p75` | 15-39 | 0.0627 | 0.0636 | 0.2513 | 0.1467 | 0.5257 | 0.0790 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p75` | 10-34 | 0.0623 | 0.0579 | 0.2209 | 0.1482 | 0.5296 | 0.0607 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p75` | 20-44 | 0.0588 | 0.0636 | 0.2632 | 0.1466 | 0.5296 | 0.0825 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p3927_ld0p24_ls0p65` | 5-29 | 0.0676 | 0.0906 | 0.2458 | 0.1473 | 0.5879 | 0.0590 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p3927_ld0p24_ls0p65` | 10-34 | 0.0553 | 0.0654 | 0.2669 | 0.1472 | 0.5301 | 0.0616 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p3927_ld0p24_ls0p65` | 15-39 | 0.0440 | 0.0530 | 0.2719 | 0.1472 | 0.5214 | 0.0704 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p36_ls0p65` | 5-29 | 0.0740 | 0.0932 | 0.2635 | 0.1465 | 0.5298 | 0.0619 | None | 84.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p36_ls0p65` | 10-34 | 0.0610 | 0.0576 | 0.2176 | 0.1481 | 0.5298 | 0.0613 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p36_ls0p65` | 15-39 | 0.0565 | 0.0576 | 0.2419 | 0.1476 | 0.5229 | 0.0775 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p36_ls0p65` | 5-29 | 0.0536 | 0.1150 | 0.1786 | 0.1486 | 0.5298 | 0.0614 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p36_ls0p65` | 20-44 | 0.0475 | 0.0576 | 0.2517 | 0.1476 | 0.5298 | 0.0792 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p24_ls0p55` | 5-29 | 0.0634 | 0.0889 | 0.2293 | 0.1486 | 0.5270 | 0.0620 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p34_ld0p3_ls1` | 5-29 | 0.0735 | 0.0929 | 0.2680 | 0.1467 | 0.5274 | 0.0756 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p34_ld0p3_ls1` | 10-34 | 0.0573 | 0.0898 | 0.2890 | 0.1466 | 0.5274 | 0.0809 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p34_ld0p3_ls1` | 15-39 | 0.0442 | 0.0799 | 0.2890 | 0.1466 | 0.5274 | 0.0757 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p42_ld0p3_ls1` | 5-29 | 0.0832 | 0.1075 | 0.2869 | 0.1465 | 0.5302 | 0.0774 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p42_ld0p36_ls0p65` | 10-34 | 0.0631 | 0.0553 | 0.2341 | 0.1476 | 0.5779 | 0.0654 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p42_ld0p36_ls0p65` | 15-39 | 0.0576 | 0.0553 | 0.2515 | 0.1472 | 0.5776 | 0.0772 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p42_ld0p36_ls0p65` | 5-29 | 0.0551 | 0.1150 | 0.1978 | 0.1478 | 0.5787 | 0.0649 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p34_ld0p36_ls1` | 5-29 | 0.0981 | 0.1136 | 0.3278 | 0.1453 | 0.5784 | 0.0788 | 50 | 76.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p24_ls0p55` | 5-29 | 0.0721 | 0.0893 | 0.2553 | 0.1472 | 0.5841 | 0.0612 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p24_ls0p55` | 10-34 | 0.0612 | 0.0619 | 0.2803 | 0.1469 | 0.5752 | 0.0653 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p24_ls0p55` | 10-34 | 0.0648 | 0.0668 | 0.2305 | 0.1478 | 0.5752 | 0.0681 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p24_ls0p55` | 15-39 | 0.0608 | 0.0668 | 0.2560 | 0.1477 | 0.5752 | 0.0787 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0063_ph0p42_ld0p36_ls1` | 10-34 | 0.0730 | 0.0702 | 0.2702 | 0.1472 | 0.5746 | 0.0751 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p52_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p24_ls0p55` | 5-29 | 0.0705 | 0.0911 | 0.2467 | 0.1480 | 0.5690 | 0.0591 | None | 76.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p52_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p24_ls0p55` | 10-34 | 0.0595 | 0.0630 | 0.2751 | 0.1475 | 0.5690 | 0.0640 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p52_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p24_ls0p55` | 15-39 | 0.0468 | 0.0515 | 0.2832 | 0.1475 | 0.5273 | 0.0668 | None | 84.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p52_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p24_ls0p55` | 10-34 | 0.0586 | 0.0485 | 0.2067 | 0.1483 | 0.5690 | 0.0652 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p52_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p24_ls0p55` | 15-39 | 0.0559 | 0.0485 | 0.2352 | 0.1482 | 0.5273 | 0.0780 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p52_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p24_ls0p55` | 20-44 | 0.0505 | 0.0485 | 0.2372 | 0.1482 | 0.5690 | 0.0783 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p52_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p24_ls0p55` | 5-29 | 0.0429 | 0.1137 | 0.1483 | 0.1499 | 0.5690 | 0.0606 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p37_ld0p36_ls0p75` | 5-29 | 0.0826 | 0.0975 | 0.2884 | 0.1459 | 0.5778 | 0.0645 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p75` | 5-29 | 0.0700 | 0.0955 | 0.2552 | 0.1468 | 0.5719 | 0.0621 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p75` | 10-34 | 0.0575 | 0.0700 | 0.2778 | 0.1468 | 0.5719 | 0.0665 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p75` | 15-39 | 0.0482 | 0.0497 | 0.2800 | 0.1468 | 0.5472 | 0.0733 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p37_ld0p36_ls0p55` | 5-29 | 0.0756 | 0.1070 | 0.2710 | 0.1457 | 0.5778 | 0.0623 | None | 84.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p37_ld0p36_ls0p55` | 10-34 | 0.0653 | 0.0650 | 0.2335 | 0.1466 | 0.5778 | 0.0658 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p37_ld0p36_ls0p55` | 15-39 | 0.0649 | 0.0650 | 0.2699 | 0.1465 | 0.5537 | 0.0818 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p37_ld0p36_ls0p55` | 20-44 | 0.0588 | 0.0650 | 0.2838 | 0.1465 | 0.5778 | 0.0842 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p37_ld0p36_ls0p55` | 5-29 | 0.0519 | 0.1126 | 0.1776 | 0.1479 | 0.5778 | 0.0650 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p34_ld0p3_ls1` | 5-29 | 0.0883 | 0.0969 | 0.2971 | 0.1462 | 0.4813 | 0.0768 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p37_ld0p24_ls0p65` | 5-29 | 0.0720 | 0.0883 | 0.2492 | 0.1481 | 0.4819 | 0.0580 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p3_ls0p75` | 5-29 | 0.0698 | 0.0890 | 0.2489 | 0.1481 | 0.4816 | 0.0614 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p3_ls0p75` | 15-39 | 0.0620 | 0.0525 | 0.2311 | 0.1485 | 0.4730 | 0.0762 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p3_ls0p75` | 20-44 | 0.0603 | 0.0525 | 0.2364 | 0.1485 | 0.4816 | 0.0808 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p3_ls0p75` | 10-34 | 0.0590 | 0.0525 | 0.1955 | 0.1498 | 0.4816 | 0.0630 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0048_ph0p42_ld0p3_ls1` | 5-29 | 0.0793 | 0.1043 | 0.2767 | 0.1469 | 0.4788 | 0.0777 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0048_ph0p42_ld0p3_ls1` | 10-34 | 0.0628 | 0.0796 | 0.2993 | 0.1468 | 0.4788 | 0.0810 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0048_ph0p42_ld0p3_ls1` | 15-39 | 0.0503 | 0.0700 | 0.2993 | 0.1468 | 0.4784 | 0.0738 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p3_ls0p75` | 5-29 | 0.0754 | 0.0902 | 0.2656 | 0.1468 | 0.5097 | 0.0615 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p34_ld0p3_ls0p55` | 5-29 | 0.0780 | 0.0823 | 0.2645 | 0.1470 | 0.4563 | 0.0568 | None | 76.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p34_ld0p3_ls0p55` | 10-34 | 0.0629 | 0.0649 | 0.2848 | 0.1467 | 0.4850 | 0.0568 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p34_ld0p3_ls0p55` | 15-39 | 0.0526 | 0.0637 | 0.2973 | 0.1467 | 0.4076 | 0.0664 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p47_ld0p24_ls0p55` | 5-29 | 0.0878 | 0.0746 | 0.2927 | 0.1468 | 0.5126 | 0.0622 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p37_ld0p24_ls0p75` | 5-29 | 0.0750 | 0.0929 | 0.2520 | 0.1487 | 0.4025 | 0.0603 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p47_ld0p36_ls0p55` | 5-29 | 0.0738 | 0.0911 | 0.2561 | 0.1472 | 0.4350 | 0.0591 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p0048_ph0p3927_ld0p36_ls0p65` | 5-29 | 0.0809 | 0.0935 | 0.2751 | 0.1467 | 0.6006 | 0.0599 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p0048_ph0p3927_ld0p36_ls0p65` | 10-34 | 0.0623 | 0.0714 | 0.2922 | 0.1463 | 0.5527 | 0.0583 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p0048_ph0p3927_ld0p36_ls0p65` | 15-39 | 0.0501 | 0.0562 | 0.2951 | 0.1463 | 0.5029 | 0.0653 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0048_ph0p3927_ld0p3_ls1` | 5-29 | 0.0816 | 0.1003 | 0.2745 | 0.1472 | 0.3810 | 0.0742 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p36_ls0p75` | 5-29 | 0.0837 | 0.0878 | 0.2855 | 0.1466 | 0.5707 | 0.0636 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0057_ph0p34_ld0p36_ls0p65` | 5-29 | 0.0812 | 0.0906 | 0.2740 | 0.1470 | 0.6009 | 0.0626 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p9_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 5-29 | 0.0749 | 0.0841 | 0.2475 | 0.1489 | 0.4836 | 0.0595 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 5-29 | 0.0695 | 0.0840 | 0.2401 | 0.1481 | 0.6479 | 0.0606 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p36_ls0p75` | 5-29 | 0.0760 | 0.0879 | 0.2631 | 0.1471 | 0.5953 | 0.0618 | None | 76.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p36_ls0p75` | 10-34 | 0.0571 | 0.0753 | 0.2839 | 0.1468 | 0.4945 | 0.0607 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p36_ls0p75` | 15-39 | 0.0436 | 0.0612 | 0.2839 | 0.1468 | 0.4770 | 0.0682 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrph0_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p0048_ph0p3927_ld0p36_ls0p65` | 5-29 | 0.0863 | 0.0919 | 0.2828 | 0.1472 | 0.4175 | 0.0633 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p36_ls1` | 5-29 | 0.1006 | 0.1085 | 0.3290 | 0.1454 | 0.8260 | 0.0802 | 50 | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrphm0p68_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55` | 5-29 | 0.0709 | 0.0850 | 0.2455 | 0.1483 | 0.4883 | 0.0589 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrphm0p68_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55` | 10-34 | 0.0568 | 0.0667 | 0.2700 | 0.1478 | 0.4875 | 0.0593 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrphm0p68_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55` | 15-39 | 0.0425 | 0.0475 | 0.2812 | 0.1478 | 0.4741 | 0.0698 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrphm1p05_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p24_ls0p65` | 5-29 | 0.0667 | 0.0883 | 0.2240 | 0.1495 | 0.4179 | 0.0592 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrphm1p05_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p34_ld0p24_ls1` | 5-29 | 0.0751 | 0.0954 | 0.2466 | 0.1488 | 0.4379 | 0.0671 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p42_ld0p36_ls0p75` | 5-29 | 0.0833 | 0.0948 | 0.2844 | 0.1461 | 0.5483 | 0.0657 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p36_ls0p65` | 5-29 | 0.0802 | 0.0942 | 0.2774 | 0.1462 | 0.5954 | 0.0606 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p36_ls0p65` | 10-34 | 0.0647 | 0.0713 | 0.2989 | 0.1459 | 0.5663 | 0.0612 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p36_ls0p65` | 15-39 | 0.0539 | 0.0596 | 0.3059 | 0.1459 | 0.5086 | 0.0659 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p36_ls0p65` | 10-34 | 0.0614 | 0.0600 | 0.2194 | 0.1477 | 0.5663 | 0.0586 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p36_ls0p65` | 15-39 | 0.0583 | 0.0600 | 0.2487 | 0.1471 | 0.5086 | 0.0779 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p36_ls0p65` | 20-44 | 0.0528 | 0.0600 | 0.2685 | 0.1468 | 0.6172 | 0.0777 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p34_ld0p24_ls1` | 5-29 | 0.0808 | 0.0997 | 0.2686 | 0.1467 | 0.5071 | 0.0704 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p34_ld0p24_ls1` | 10-34 | 0.0649 | 0.0824 | 0.3140 | 0.1461 | 0.5068 | 0.0797 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p34_ld0p24_ls1` | 15-39 | 0.0488 | 0.0740 | 0.3141 | 0.1461 | 0.4961 | 0.0740 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p34_ld0p3_ls0p75` | 5-29 | 0.0935 | 0.1020 | 0.3088 | 0.1453 | 0.5540 | 0.0623 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p34_ld0p3_ls0p75` | 10-34 | 0.0783 | 0.0801 | 0.3351 | 0.1452 | 0.5532 | 0.0679 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p34_ld0p3_ls0p75` | 15-39 | 0.0669 | 0.0622 | 0.3399 | 0.1452 | 0.5434 | 0.0662 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p34_ld0p3_ls0p75` | 10-34 | 0.0645 | 0.0561 | 0.2325 | 0.1476 | 0.5532 | 0.0608 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p34_ld0p3_ls0p75` | 15-39 | 0.0560 | 0.0528 | 0.2440 | 0.1476 | 0.5434 | 0.0730 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p24_ls0p75` | 5-29 | 0.0750 | 0.0965 | 0.2573 | 0.1475 | 0.5515 | 0.0603 | None | 76.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p24_ls0p75` | 10-34 | 0.0611 | 0.0670 | 0.2872 | 0.1473 | 0.5501 | 0.0632 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p24_ls0p75` | 15-39 | 0.0496 | 0.0405 | 0.2907 | 0.1473 | 0.5361 | 0.0634 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0063_ph0p37_ld0p3_ls0p65` | 5-29 | 0.0902 | 0.1006 | 0.2924 | 0.1460 | 0.6135 | 0.0641 | None | 72.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0063_ph0p37_ld0p3_ls0p65` | 10-34 | 0.0736 | 0.0926 | 0.3227 | 0.1457 | 0.5706 | 0.0648 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0063_ph0p37_ld0p3_ls0p65` | 15-39 | 0.0605 | 0.0573 | 0.3325 | 0.1457 | 0.5540 | 0.0666 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p3_ls0p65` | 5-29 | 0.0787 | 0.1009 | 0.2730 | 0.1462 | 0.6648 | 0.0586 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p3_ls0p65` | 10-34 | 0.0622 | 0.0702 | 0.2918 | 0.1461 | 0.6251 | 0.0660 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p3_ls0p65` | 15-39 | 0.0504 | 0.0544 | 0.2975 | 0.1461 | 0.5510 | 0.0664 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p3_ls0p65` | 10-34 | 0.0573 | 0.0563 | 0.2087 | 0.1479 | 0.6251 | 0.0626 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p3_ls0p65` | 15-39 | 0.0516 | 0.0563 | 0.2328 | 0.1477 | 0.5510 | 0.0766 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p3_ls0p65` | 5-29 | 0.0498 | 0.1147 | 0.1707 | 0.1486 | 0.6648 | 0.0585 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p3_ls0p65` | 5-29 | 0.0662 | 0.0918 | 0.2394 | 0.1471 | 0.6026 | 0.0601 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p3_ls0p65` | 10-34 | 0.0606 | 0.0587 | 0.2140 | 0.1481 | 0.5626 | 0.0618 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p3_ls0p65` | 15-39 | 0.0563 | 0.0587 | 0.2433 | 0.1477 | 0.5510 | 0.0803 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p37_ld0p36_ls0p75` | 5-29 | 0.0837 | 0.1010 | 0.2886 | 0.1459 | 0.5836 | 0.0653 | None | 76.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p37_ld0p36_ls0p75` | 10-34 | 0.0651 | 0.0874 | 0.3070 | 0.1455 | 0.5562 | 0.0658 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p37_ld0p36_ls0p75` | 15-39 | 0.0508 | 0.0661 | 0.3070 | 0.1455 | 0.5562 | 0.0669 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0_ph0p42_ld0p36_ls0p75` | 5-29 | 0.0901 | 0.0991 | 0.3063 | 0.1460 | 0.5483 | 0.0671 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0_ph0p42_ld0p36_ls0p75` | 10-34 | 0.0726 | 0.0818 | 0.3274 | 0.1459 | 0.4639 | 0.0671 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0_ph0p42_ld0p36_ls0p75` | 15-39 | 0.0567 | 0.0455 | 0.3274 | 0.1459 | 0.4639 | 0.0662 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p36_ls0p75` | 5-29 | 0.0974 | 0.0959 | 0.3172 | 0.1456 | 0.5174 | 0.0696 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p36_ls0p75` | 10-34 | 0.0775 | 0.0901 | 0.3437 | 0.1455 | 0.4865 | 0.0696 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p36_ls0p75` | 15-39 | 0.0602 | 0.0503 | 0.3437 | 0.1455 | 0.4865 | 0.0689 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p36_ls0p65` | 5-29 | 0.0847 | 0.0980 | 0.2849 | 0.1464 | 0.4652 | 0.0643 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p36_ls0p65` | 10-34 | 0.0665 | 0.0775 | 0.3071 | 0.1460 | 0.4641 | 0.0650 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p36_ls0p65` | 15-39 | 0.0505 | 0.0561 | 0.3074 | 0.1460 | 0.4496 | 0.0667 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p36_ls1` | 5-29 | 0.0919 | 0.1051 | 0.3063 | 0.1457 | 0.8165 | 0.0776 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p65` | 5-29 | 0.0800 | 0.0893 | 0.2738 | 0.1466 | 0.4665 | 0.0616 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p24_ls0p75` | 5-29 | 0.0692 | 0.0883 | 0.2376 | 0.1488 | 0.4554 | 0.0596 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0_ph0p42_ld0p24_ls1` | 5-29 | 0.0795 | 0.0997 | 0.2667 | 0.1471 | 0.4604 | 0.0782 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p42_ld0p24_ls0p55` | 5-29 | 0.0625 | 0.0855 | 0.2258 | 0.1479 | 0.6326 | 0.0585 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p42_ld0p24_ls0p55` | 10-34 | 0.0498 | 0.0599 | 0.2481 | 0.1475 | 0.6057 | 0.0603 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p42_ld0p24_ls0p55` | 15-39 | 0.0411 | 0.0584 | 0.2676 | 0.1475 | 0.4920 | 0.0743 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p42_ld0p24_ls0p55` | 15-39 | 0.0618 | 0.0615 | 0.2553 | 0.1475 | 0.4920 | 0.0768 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p42_ld0p24_ls0p55` | 10-34 | 0.0612 | 0.0615 | 0.2173 | 0.1475 | 0.6057 | 0.0607 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p42_ld0p24_ls0p55` | 20-44 | 0.0583 | 0.0615 | 0.2746 | 0.1474 | 0.6326 | 0.0786 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p47_ld0p36_ls0p55` | 5-29 | 0.0659 | 0.0828 | 0.2293 | 0.1484 | 0.4611 | 0.0586 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p42_ld0p24_ls0p55` | 5-29 | 0.0773 | 0.0861 | 0.2473 | 0.1489 | 0.3784 | 0.0587 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p42_ld0p24_ls0p55` | 10-34 | 0.0597 | 0.0630 | 0.2673 | 0.1484 | 0.3873 | 0.0600 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p42_ld0p24_ls0p55` | 15-39 | 0.0431 | 0.0404 | 0.2784 | 0.1484 | 0.3756 | 0.0618 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrph0_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0084_ph0p34_ld0p3_ls0p55` | 5-29 | 0.0813 | 0.0818 | 0.2585 | 0.1478 | 0.4449 | 0.0632 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p0048_ph0p34_ld0p36_ls1` | 5-29 | 0.0906 | 0.0976 | 0.2798 | 0.1478 | 0.3459 | 0.0721 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 5-29 | 0.0731 | 0.0744 | 0.2375 | 0.1485 | 0.4468 | 0.0593 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm1p05_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p0048_ph0p37_ld0p24_ls0p55` | 5-29 | 0.0650 | 0.0771 | 0.2118 | 0.1499 | 0.3466 | 0.0588 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p47_ld0p3_ls0p55` | 5-29 | 0.0669 | 0.0841 | 0.2253 | 0.1488 | 0.3713 | 0.0590 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p37_ld0p24_ls1` | 5-29 | 0.0791 | 0.0929 | 0.2414 | 0.1493 | 0.4499 | 0.0653 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p3927_ld0p3_ls0p65` | 5-29 | 0.0888 | 0.0943 | 0.2835 | 0.1477 | 0.3892 | 0.0652 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrph0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p24_ls0p65` | 5-29 | 0.0847 | 0.0903 | 0.2714 | 0.1474 | 0.4533 | 0.0621 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrph0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p24_ls0p65` | 10-34 | 0.0667 | 0.0691 | 0.3016 | 0.1467 | 0.4748 | 0.0622 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrphm0p52_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p42_ld0p24_ls0p75` | 5-29 | 0.0735 | 0.0812 | 0.2278 | 0.1496 | 0.4462 | 0.0593 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p42_ld0p3_ls0p55` | 5-29 | 0.0653 | 0.0789 | 0.2182 | 0.1486 | 0.4511 | 0.0599 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrphm1p05_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p3927_ld0p36_ls0p65` | 5-29 | 0.0768 | 0.0920 | 0.2546 | 0.1477 | 0.4657 | 0.0632 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p3927_ld0p3_ls0p55` | 5-29 | 0.0736 | 0.0909 | 0.2423 | 0.1485 | 0.4689 | 0.0582 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p3927_ld0p3_ls0p55` | 10-34 | 0.0577 | 0.0621 | 0.2687 | 0.1477 | 0.4733 | 0.0585 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p3927_ld0p3_ls0p55` | 15-39 | 0.0442 | 0.0431 | 0.2825 | 0.1476 | 0.4443 | 0.0589 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p3_ls0p75` | 5-29 | 0.0774 | 0.0961 | 0.2464 | 0.1484 | 0.4713 | 0.0612 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p3_ls0p75` | 10-34 | 0.0617 | 0.0693 | 0.2860 | 0.1472 | 0.4749 | 0.0612 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p3_ls0p75` | 15-39 | 0.0477 | 0.0397 | 0.2946 | 0.1472 | 0.4595 | 0.0612 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p47_ld0p24_ls0p55` | 5-29 | 0.0749 | 0.0882 | 0.2472 | 0.1474 | 0.4745 | 0.0615 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p75` | 5-29 | 0.0749 | 0.0946 | 0.2401 | 0.1487 | 0.4599 | 0.0592 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0_ph0p34_ld0p24_ls0p75` | 5-29 | 0.0729 | 0.0911 | 0.2301 | 0.1494 | 0.4633 | 0.0594 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p47_ld0p36_ls0p75` | 5-29 | 0.0830 | 0.0957 | 0.2752 | 0.1467 | 0.5108 | 0.0647 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p47_ld0p36_ls0p75` | 10-34 | 0.0630 | 0.0845 | 0.2988 | 0.1457 | 0.5108 | 0.0658 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p47_ld0p36_ls0p75` | 15-39 | 0.0450 | 0.0615 | 0.2990 | 0.1457 | 0.4757 | 0.0660 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p9_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p42_ld0p36_ls1` | 5-29 | 0.0862 | 0.0991 | 0.2705 | 0.1472 | 0.5456 | 0.0735 | None | 76.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p9_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p42_ld0p36_ls1` | 10-34 | 0.0681 | 0.0883 | 0.3212 | 0.1455 | 0.5810 | 0.0749 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p9_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p42_ld0p36_ls1` | 15-39 | 0.0466 | 0.0725 | 0.3244 | 0.1455 | 0.4752 | 0.0766 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p37_ld0p24_ls0p55` | 5-29 | 0.0835 | 0.1005 | 0.2706 | 0.1467 | 0.5113 | 0.0626 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p37_ld0p24_ls0p55` | 10-34 | 0.0659 | 0.0736 | 0.2903 | 0.1462 | 0.5179 | 0.0656 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p37_ld0p24_ls0p55` | 15-39 | 0.0498 | 0.0712 | 0.3003 | 0.1462 | 0.4805 | 0.0687 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p37_ld0p24_ls1` | 5-29 | 0.0878 | 0.1040 | 0.2672 | 0.1473 | 0.5141 | 0.0673 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p65` | 5-29 | 0.0954 | 0.1059 | 0.2972 | 0.1464 | 0.5194 | 0.0666 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p24_ls0p65` | 5-29 | 0.0930 | 0.1030 | 0.2872 | 0.1474 | 0.5105 | 0.0685 | None | 76.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p24_ls0p65` | 10-34 | 0.0744 | 0.0885 | 0.3176 | 0.1469 | 0.5025 | 0.0710 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p24_ls0p65` | 15-39 | 0.0546 | 0.0451 | 0.3299 | 0.1469 | 0.5025 | 0.0720 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p24_ls0p65` | 10-34 | 0.0521 | 0.0437 | 0.1839 | 0.1496 | 0.5025 | 0.0603 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p24_ls0p65` | 15-39 | 0.0446 | 0.0448 | 0.2148 | 0.1494 | 0.5025 | 0.0627 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p007_ph0p47_ld0p24_ls0p75` | 5-29 | 0.0745 | 0.0897 | 0.2408 | 0.1476 | 0.5120 | 0.0587 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00525_ph0p37_ld0p36_ls0p65` | 5-29 | 0.0857 | 0.1063 | 0.2848 | 0.1461 | 0.5188 | 0.0654 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p42_ld0p24_ls0p55` | 5-29 | 0.0650 | 0.0814 | 0.2257 | 0.1477 | 0.5543 | 0.0582 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p42_ld0p24_ls0p55` | 5-29 | 0.0485 | 0.1112 | 0.1530 | 0.1491 | 0.5543 | 0.0594 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55` | 5-29 | 0.0717 | 0.0919 | 0.2402 | 0.1475 | 0.4883 | 0.0631 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55` | 10-34 | 0.0535 | 0.0705 | 0.2643 | 0.1466 | 0.5179 | 0.0643 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55` | 10-34 | 0.0568 | 0.0523 | 0.1961 | 0.1477 | 0.5179 | 0.0593 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55` | 15-39 | 0.0521 | 0.0551 | 0.2322 | 0.1476 | 0.5114 | 0.0686 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55` | 20-44 | 0.0485 | 0.0551 | 0.2553 | 0.1475 | 0.5022 | 0.0726 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p3927_ld0p36_ls0p55` | 5-29 | 0.0742 | 0.0905 | 0.2475 | 0.1470 | 0.5064 | 0.0640 | None | 76.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p3927_ld0p36_ls0p55` | 10-34 | 0.0546 | 0.0729 | 0.2662 | 0.1460 | 0.6101 | 0.0651 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p3927_ld0p36_ls0p55` | 15-39 | 0.0401 | 0.0581 | 0.2805 | 0.1460 | 0.5170 | 0.0676 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p3927_ld0p36_ls0p55` | 20-44 | 0.0700 | 0.0667 | 0.2936 | 0.1461 | 0.5155 | 0.0747 | 55 | 92.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p3927_ld0p36_ls0p55` | 15-39 | 0.0654 | 0.0667 | 0.2558 | 0.1463 | 0.5170 | 0.0700 | 60 | 92.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p3927_ld0p36_ls0p55` | 10-34 | 0.0629 | 0.0609 | 0.2049 | 0.1466 | 0.6101 | 0.0563 | 65 | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p42_ld0p36_ls0p75` | 5-29 | 0.0869 | 0.0992 | 0.2816 | 0.1466 | 0.4467 | 0.0673 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p34_ld0p36_ls1` | 5-29 | 0.0979 | 0.1174 | 0.2989 | 0.1461 | 0.4321 | 0.0749 | 65 | 72.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p52_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p47_ld0p24_ls0p75` | 5-29 | 0.0763 | 0.0937 | 0.2457 | 0.1482 | 0.4266 | 0.0580 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p52_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p47_ld0p24_ls0p75` | 10-34 | 0.0600 | 0.0697 | 0.2796 | 0.1473 | 0.4317 | 0.0586 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p52_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p47_ld0p24_ls0p75` | 15-39 | 0.0435 | 0.0445 | 0.2849 | 0.1473 | 0.4162 | 0.0591 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p68_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p36_ls0p55` | 5-29 | 0.0772 | 0.0855 | 0.2574 | 0.1475 | 0.4279 | 0.0598 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p37_ld0p36_ls0p75` | 5-29 | 0.0897 | 0.1013 | 0.2888 | 0.1466 | 0.4727 | 0.0688 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 5-29 | 0.0735 | 0.0851 | 0.2413 | 0.1478 | 0.4919 | 0.0603 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 10-34 | 0.0551 | 0.0684 | 0.2663 | 0.1470 | 0.5648 | 0.0608 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 20-44 | 0.0630 | 0.0591 | 0.2669 | 0.1473 | 0.5381 | 0.0707 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 15-39 | 0.0601 | 0.0591 | 0.2379 | 0.1480 | 0.4381 | 0.0644 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 10-34 | 0.0588 | 0.0560 | 0.1928 | 0.1483 | 0.5648 | 0.0556 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p47_ld0p3_ls0p75` | 5-29 | 0.0718 | 0.0905 | 0.2334 | 0.1488 | 0.4227 | 0.0609 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p47_ld0p3_ls0p75` | 10-34 | 0.0568 | 0.0687 | 0.2702 | 0.1477 | 0.4301 | 0.0618 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p47_ld0p3_ls0p75` | 15-39 | 0.0414 | 0.0491 | 0.2781 | 0.1477 | 0.4245 | 0.0618 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p3_ls0p55` | 5-29 | 0.0682 | 0.0851 | 0.2211 | 0.1493 | 0.4071 | 0.0582 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p3_ls0p55` | 20-44 | 0.0574 | 0.0515 | 0.2522 | 0.1482 | 0.4138 | 0.0688 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p3_ls0p55` | 15-39 | 0.0571 | 0.0515 | 0.2257 | 0.1484 | 0.4258 | 0.0625 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p3_ls0p55` | 10-34 | 0.0563 | 0.0464 | 0.1802 | 0.1490 | 0.4314 | 0.0594 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p37_ld0p3_ls0p75` | 5-29 | 0.0756 | 0.0912 | 0.2449 | 0.1477 | 0.4286 | 0.0620 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p37_ld0p3_ls0p75` | 10-34 | 0.0568 | 0.0717 | 0.2762 | 0.1467 | 0.4323 | 0.0627 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p34_ld0p24_ls0p55` | 5-29 | 0.0689 | 0.0796 | 0.2433 | 0.1484 | 0.4864 | 0.0603 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0063_ph0p42_ld0p36_ls0p55` | 5-29 | 0.0819 | 0.0828 | 0.2874 | 0.1463 | 0.5306 | 0.0605 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p3927_ld0p24_ls0p75` | 5-29 | 0.0725 | 0.0905 | 0.2586 | 0.1486 | 0.4343 | 0.0611 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 5-29 | 0.0910 | 0.0832 | 0.3070 | 0.1464 | 0.5824 | 0.0612 | None | 76.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 10-34 | 0.0760 | 0.0805 | 0.3272 | 0.1464 | 0.5610 | 0.0608 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p47_ld0p36_ls0p75` | 5-29 | 0.0840 | 0.0851 | 0.2904 | 0.1466 | 0.5766 | 0.0624 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p0064_ph0p37_ld0p24_ls1` | 5-29 | 0.0778 | 0.0976 | 0.2737 | 0.1475 | 0.4002 | 0.0769 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p0064_ph0p37_ld0p24_ls1` | 10-34 | 0.0602 | 0.0774 | 0.2915 | 0.1475 | 0.3987 | 0.0821 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p0064_ph0p37_ld0p24_ls1` | 15-39 | 0.0504 | 0.0711 | 0.2915 | 0.1474 | 0.4002 | 0.0768 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p68_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p36_ls0p55` | 5-29 | 0.0728 | 0.0844 | 0.2566 | 0.1482 | 0.5220 | 0.0621 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p68_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p36_ls0p55` | 10-34 | 0.0610 | 0.0642 | 0.2850 | 0.1478 | 0.5220 | 0.0632 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p68_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p36_ls0p55` | 15-39 | 0.0480 | 0.0457 | 0.2885 | 0.1478 | 0.5218 | 0.0720 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p24_ls0p75` | 5-29 | 0.0672 | 0.0834 | 0.2431 | 0.1481 | 0.4436 | 0.0611 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p24_ls0p55` | 5-29 | 0.0680 | 0.0844 | 0.2466 | 0.1478 | 0.6254 | 0.0588 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p24_ls0p75` | 5-29 | 0.0671 | 0.0851 | 0.2416 | 0.1484 | 0.4096 | 0.0613 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm1p05_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0057_ph0p37_ld0p36_ls1` | 5-29 | 0.0875 | 0.1006 | 0.3071 | 0.1466 | 0.9722 | 0.0785 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm1p05_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0063_ph0p37_ld0p3_ls0p75` | 5-29 | 0.0748 | 0.0846 | 0.2665 | 0.1472 | 0.5227 | 0.0643 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p36_ls1` | 5-29 | 0.0911 | 0.0995 | 0.3133 | 0.1464 | 0.5801 | 0.0723 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls1` | 5-29 | 0.0818 | 0.0917 | 0.2903 | 0.1472 | 0.4708 | 0.0788 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p34_ld0p24_ls1` | 5-29 | 0.0783 | 0.1017 | 0.2753 | 0.1476 | 0.4475 | 0.0770 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p34_ld0p24_ls1` | 10-34 | 0.0597 | 0.0973 | 0.2953 | 0.1476 | 0.4473 | 0.0821 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0p7854_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p34_ld0p24_ls0p65` | 5-29 | 0.0759 | 0.0928 | 0.2689 | 0.1482 | 0.5156 | 0.0606 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0p7854_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p34_ld0p24_ls0p65` | 10-34 | 0.0626 | 0.0808 | 0.2974 | 0.1478 | 0.5144 | 0.0608 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p65` | 5-29 | 0.0721 | 0.0857 | 0.2656 | 0.1473 | 0.5404 | 0.0609 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p52_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p65` | 5-29 | 0.0741 | 0.0864 | 0.2664 | 0.1472 | 0.5524 | 0.0605 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p3927_ld0p24_ls0p75` | 5-29 | 0.0705 | 0.0903 | 0.2576 | 0.1477 | 0.4511 | 0.0601 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p3927_ld0p24_ls0p75` | 10-34 | 0.0579 | 0.0673 | 0.2750 | 0.1477 | 0.4491 | 0.0617 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p3927_ld0p24_ls0p75` | 15-39 | 0.0472 | 0.0485 | 0.2753 | 0.1477 | 0.4511 | 0.0684 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00525_ph0p47_ld0p3_ls0p75` | 5-29 | 0.0698 | 0.0866 | 0.2556 | 0.1475 | 0.5099 | 0.0646 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55` | 5-29 | 0.0611 | 0.0804 | 0.2239 | 0.1487 | 0.5024 | 0.0616 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p65` | 5-29 | 0.0681 | 0.0865 | 0.2460 | 0.1480 | 0.5017 | 0.0615 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p24_ls0p65` | 5-29 | 0.0651 | 0.0875 | 0.2342 | 0.1487 | 0.4759 | 0.0600 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p37_ld0p36_ls0p75` | 5-29 | 0.0785 | 0.0866 | 0.2793 | 0.1466 | 0.6084 | 0.0652 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0084_ph0p47_ld0p24_ls0p75` | 5-29 | 0.0676 | 0.0901 | 0.2474 | 0.1485 | 0.5154 | 0.0634 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm1p05_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p42_ld0p24_ls0p55` | 5-29 | 0.0617 | 0.0902 | 0.2260 | 0.1487 | 0.4852 | 0.0630 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p42_ld0p3_ls0p75` | 5-29 | 0.0732 | 0.0933 | 0.2661 | 0.1467 | 0.5488 | 0.0643 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p42_ld0p3_ls0p75` | 15-39 | 0.0736 | 0.0652 | 0.2562 | 0.1473 | 0.5479 | 0.0775 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p42_ld0p3_ls0p75` | 10-34 | 0.0673 | 0.0652 | 0.2194 | 0.1485 | 0.5479 | 0.0650 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p3_ls1` | 5-29 | 0.0814 | 0.1037 | 0.2893 | 0.1464 | 0.5503 | 0.0786 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p3_ls1` | 10-34 | 0.0656 | 0.0829 | 0.3127 | 0.1464 | 0.5502 | 0.0831 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p3_ls1` | 15-39 | 0.0550 | 0.0725 | 0.3127 | 0.1464 | 0.5441 | 0.0757 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p3_ls1` | 10-34 | 0.0740 | 0.0662 | 0.2631 | 0.1475 | 0.5502 | 0.0796 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p3_ls1` | 15-39 | 0.0646 | 0.0719 | 0.2631 | 0.1473 | 0.5441 | 0.0796 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p37_ld0p36_ls0p65` | 5-29 | 0.0762 | 0.1035 | 0.2785 | 0.1460 | 0.5932 | 0.0632 | None | 72.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p37_ld0p36_ls0p65` | 10-34 | 0.0635 | 0.0705 | 0.3010 | 0.1460 | 0.5932 | 0.0681 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p37_ld0p36_ls0p65` | 15-39 | 0.0530 | 0.0500 | 0.3031 | 0.1460 | 0.5878 | 0.0735 | None | 80.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p37_ld0p36_ls0p65` | 10-34 | 0.0635 | 0.0561 | 0.2330 | 0.1479 | 0.5932 | 0.0654 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p37_ld0p36_ls0p65` | 15-39 | 0.0573 | 0.0561 | 0.2451 | 0.1477 | 0.5878 | 0.0799 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p37_ld0p36_ls0p65` | 20-44 | 0.0442 | 0.0561 | 0.2451 | 0.1477 | 0.5878 | 0.0837 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm0p9_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0105_ph0p3927_ld0p24_ls0p55` | 5-29 | 0.0603 | 0.0931 | 0.2286 | 0.1480 | 0.5883 | 0.0630 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm0p9_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0105_ph0p3927_ld0p24_ls0p55` | 10-34 | 0.0516 | 0.0557 | 0.2548 | 0.1478 | 0.5883 | 0.0668 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm0p9_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0105_ph0p3927_ld0p24_ls0p55` | 15-39 | 0.0417 | 0.0535 | 0.2619 | 0.1478 | 0.5834 | 0.0759 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p34_ld0p3_ls0p75` | 5-29 | 0.0715 | 0.0990 | 0.2569 | 0.1472 | 0.5946 | 0.0628 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrph0_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p008_ph0p42_ld0p24_ls0p75` | 5-29 | 0.0699 | 0.0910 | 0.2502 | 0.1485 | 0.4942 | 0.0627 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p42_ld0p24_ls0p75` | 5-29 | 0.0920 | 0.1075 | 0.3200 | 0.1458 | 0.5249 | 0.0651 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p3_ls0p75` | 5-29 | 0.0743 | 0.0974 | 0.2707 | 0.1471 | 0.4999 | 0.0633 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p3_ls0p75` | 10-34 | 0.0613 | 0.0695 | 0.2871 | 0.1471 | 0.4996 | 0.0648 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p3_ls0p75` | 15-39 | 0.0500 | 0.0464 | 0.2871 | 0.1471 | 0.4996 | 0.0697 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p34_ld0p36_ls0p65` | 5-29 | 0.0789 | 0.0943 | 0.2829 | 0.1460 | 0.6591 | 0.0607 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p34_ld0p36_ls0p65` | 10-34 | 0.0656 | 0.0755 | 0.2996 | 0.1460 | 0.6591 | 0.0656 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p34_ld0p36_ls0p65` | 15-39 | 0.0560 | 0.0604 | 0.3065 | 0.1460 | 0.6308 | 0.0705 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p47_ld0p36_ls0p65` | 5-29 | 0.0766 | 0.0930 | 0.2795 | 0.1466 | 0.5129 | 0.0615 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p42_ld0p3_ls1` | 5-29 | 0.0823 | 0.1038 | 0.2883 | 0.1467 | 0.5013 | 0.0786 | None | 76.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p42_ld0p3_ls1` | 10-34 | 0.0657 | 0.0867 | 0.3063 | 0.1467 | 0.4989 | 0.0828 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p42_ld0p3_ls1` | 15-39 | 0.0575 | 0.0834 | 0.3063 | 0.1461 | 0.4989 | 0.0778 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p3927_ld0p24_ls1` | 5-29 | 0.0737 | 0.0984 | 0.2615 | 0.1483 | 0.4953 | 0.0754 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p36_ls1` | 5-29 | 0.0860 | 0.1014 | 0.2981 | 0.1466 | 0.9375 | 0.0784 | None | 88.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p47_ld0p36_ls0p55` | 0-24 | 0.0800 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p47_ld0p36_ls0p55` | 10-34 | 0.0673 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p47_ld0p36_ls0p55` | 15-39 | 0.0556 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p47_ld0p36_ls0p55` | 10-34 | 0.0644 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p47_ld0p36_ls0p55` | 15-39 | 0.0622 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p47_ld0p36_ls0p55` | 0-24 | 0.0574 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p47_ld0p36_ls0p55` | 20-44 | 0.0558 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p47_ld0p36_ls0p55` | 5-29 | 0.0527 | `high_lateral_velocity, single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p47_ld0p36_ls0p55` | 25-49 | 0.0467 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p37_ld0p24_ls0p75` | 0-24 | 0.0705 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p37_ld0p24_ls0p75` | 10-34 | 0.0606 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p37_ld0p24_ls0p75` | 15-39 | 0.0483 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p37_ld0p24_ls0p75` | 15-39 | 0.0605 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p37_ld0p24_ls0p75` | 10-34 | 0.0593 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p37_ld0p24_ls0p75` | 20-44 | 0.0579 | `single_contact_pattern_dominates` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
