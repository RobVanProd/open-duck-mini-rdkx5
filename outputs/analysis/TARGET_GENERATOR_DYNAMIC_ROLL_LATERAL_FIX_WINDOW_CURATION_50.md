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

- mined_windows: `481`
- pass_curated_seed_windows: `70`
- review_motion_hints: `411`
- rejected_dataset_seeds: `0`
- curated_source_files: `2`
- curated_modes: `63`
- curated_source_mode_pairs: `66`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p42_ld0p3_ls1` | 5-54 | 0.0417 | 0.0868 | 0.3144 | 0.1463 | 0.4573 | 0.0783 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p34_ld0p36_ls1` | 5-54 | 0.0449 | 0.0939 | 0.3359 | 0.1456 | 0.3856 | 0.0810 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0p7854_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p42_ld0p24_ls0p75` | 5-54 | 0.0406 | 0.0845 | 0.3018 | 0.1464 | 0.4650 | 0.0673 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p24_ls0p75` | 5-54 | 0.0400 | 0.0879 | 0.3280 | 0.1463 | 0.4579 | 0.0651 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p36_ls1` | 5-54 | 0.0444 | 0.0966 | 0.3453 | 0.1453 | 0.5062 | 0.0818 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p36_ls1` | 5-54 | 0.0477 | 0.0990 | 0.3387 | 0.1450 | 0.5601 | 0.0798 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p47_ld0p36_ls1` | 5-54 | 0.0465 | 0.0932 | 0.3254 | 0.1451 | 1.3607 | 0.0811 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p75` | 0-49 | 0.0439 | 0.1186 | 0.3117 | 0.1464 | 0.5263 | 0.0817 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p36_ls0p55` | 5-54 | 0.0408 | 0.0919 | 0.3116 | 0.1462 | 0.5274 | 0.0679 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p34_ld0p24_ls0p55` | 5-54 | 0.0430 | 0.0755 | 0.3111 | 0.1461 | 0.5635 | 0.0693 | None | 86.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p75` | 5-54 | 0.0401 | 0.0881 | 0.3167 | 0.1455 | 0.5296 | 0.0719 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p75` | 5-54 | 0.0435 | 0.0910 | 0.2782 | 0.1458 | 0.5296 | 0.0735 | None | 94.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p75` | 10-59 | 0.0417 | 0.0586 | 0.2950 | 0.1455 | 0.5296 | 0.0762 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p42_ld0p3_ls1` | 5-54 | 0.0407 | 0.0894 | 0.3092 | 0.1462 | 0.5302 | 0.0759 | None | 94.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p42_ld0p36_ls0p65` | 5-54 | 0.0410 | 0.0641 | 0.2704 | 0.1458 | 0.5784 | 0.0737 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p37_ld0p36_ls0p55` | 5-54 | 0.0462 | 0.0814 | 0.3126 | 0.1454 | 0.5754 | 0.0730 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p34_ld0p3_ls1` | 5-54 | 0.0438 | 0.0834 | 0.3254 | 0.1457 | 0.4813 | 0.0786 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p34_ld0p3_ls0p55` | 5-54 | 0.0429 | 0.0672 | 0.3015 | 0.1467 | 0.4413 | 0.0690 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p47_ld0p24_ls0p55` | 5-54 | 0.0406 | 0.0695 | 0.3174 | 0.1468 | 0.4947 | 0.0676 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p0048_ph0p3927_ld0p36_ls0p65` | 5-54 | 0.0418 | 0.0736 | 0.2992 | 0.1463 | 0.5757 | 0.0681 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p36_ls0p75` | 5-54 | 0.0407 | 0.0847 | 0.3028 | 0.1463 | 0.5285 | 0.0704 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0057_ph0p34_ld0p36_ls0p65` | 5-54 | 0.0431 | 0.0805 | 0.3015 | 0.1464 | 0.5617 | 0.0701 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p36_ls0p75` | 5-54 | 0.0400 | 0.0780 | 0.2841 | 0.1467 | 0.5159 | 0.0709 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrphm0p68_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55` | 0-49 | 0.0405 | 0.1176 | 0.2805 | 0.1478 | 0.4854 | 0.0796 | None | 86.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p36_ls0p65` | 5-54 | 0.0441 | 0.0737 | 0.3094 | 0.1459 | 0.5581 | 0.0677 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p34_ld0p3_ls0p75` | 5-54 | 0.0540 | 0.0819 | 0.3440 | 0.1452 | 0.5537 | 0.0684 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0063_ph0p37_ld0p3_ls0p65` | 5-54 | 0.0469 | 0.0956 | 0.3324 | 0.1455 | 0.5600 | 0.0670 | None | 86.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p3_ls0p65` | 5-54 | 0.0409 | 0.0720 | 0.3009 | 0.1461 | 0.6147 | 0.0676 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p37_ld0p36_ls0p75` | 5-54 | 0.0422 | 0.0896 | 0.3069 | 0.1455 | 0.5564 | 0.0696 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0_ph0p42_ld0p36_ls0p75` | 5-54 | 0.0411 | 0.0837 | 0.3265 | 0.1459 | 0.5144 | 0.0681 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p36_ls0p75` | 5-54 | 0.0446 | 0.0921 | 0.3431 | 0.1455 | 0.4871 | 0.0705 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p36_ls1` | 5-54 | 0.0488 | 0.0909 | 0.3408 | 0.1454 | 0.7265 | 0.0788 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p42_ld0p24_ls0p55` | 0-49 | 0.0424 | 0.1186 | 0.2713 | 0.1475 | 0.5405 | 0.0817 | None | 86.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p47_ld0p36_ls0p55` | 0-49 | 0.0410 | 0.1193 | 0.2717 | 0.1481 | 0.4611 | 0.0788 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrph0_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0084_ph0p34_ld0p3_ls0p55` | 5-54 | 0.0419 | 0.0703 | 0.2919 | 0.1472 | 0.4442 | 0.0666 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p0048_ph0p34_ld0p36_ls1` | 5-54 | 0.0433 | 0.0854 | 0.3253 | 0.1460 | 0.3459 | 0.0756 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 0-49 | 0.0435 | 0.1161 | 0.2776 | 0.1475 | 0.4650 | 0.0793 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 5-54 | 0.0405 | 0.0727 | 0.2776 | 0.1475 | 0.4258 | 0.0682 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p47_ld0p3_ls0p55` | 5-54 | 0.0410 | 0.0583 | 0.2727 | 0.1481 | 0.3737 | 0.0669 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p3927_ld0p3_ls0p65` | 5-54 | 0.0421 | 0.0773 | 0.3148 | 0.1471 | 0.3888 | 0.0680 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrph0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p24_ls0p65` | 5-54 | 0.0426 | 0.0758 | 0.3088 | 0.1467 | 0.4521 | 0.0640 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrphm0p52_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p42_ld0p24_ls0p75` | 0-49 | 0.0422 | 0.1176 | 0.2827 | 0.1483 | 0.4421 | 0.0777 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p42_ld0p3_ls0p55` | 0-49 | 0.0436 | 0.1182 | 0.2696 | 0.1478 | 0.4517 | 0.0786 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrphm1p05_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p3927_ld0p36_ls0p65` | 5-54 | 0.0424 | 0.0743 | 0.2829 | 0.1469 | 0.4574 | 0.0699 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p47_ld0p36_ls0p75` | 5-54 | 0.0447 | 0.0862 | 0.2982 | 0.1457 | 0.4800 | 0.0680 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p9_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p42_ld0p36_ls1` | 5-54 | 0.0416 | 0.0900 | 0.3226 | 0.1455 | 0.4752 | 0.0742 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p37_ld0p24_ls0p55` | 5-54 | 0.0417 | 0.0832 | 0.3021 | 0.1462 | 0.5059 | 0.0675 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p37_ld0p24_ls1` | 5-54 | 0.0461 | 0.0837 | 0.3279 | 0.1459 | 0.5113 | 0.0725 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p65` | 5-54 | 0.0521 | 0.0996 | 0.3456 | 0.1451 | 0.5228 | 0.0686 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p24_ls0p65` | 5-54 | 0.0423 | 0.0889 | 0.3294 | 0.1469 | 0.5025 | 0.0697 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p24_ls0p65` | 10-59 | 0.0411 | 0.0431 | 0.2476 | 0.1478 | 0.5085 | 0.0707 | None | 94.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p24_ls0p65` | 5-54 | 0.0410 | 0.0643 | 0.2417 | 0.1488 | 0.5025 | 0.0676 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p007_ph0p47_ld0p24_ls0p75` | 0-49 | 0.0437 | 0.1186 | 0.2827 | 0.1467 | 0.5118 | 0.0794 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p42_ld0p24_ls0p55` | 0-49 | 0.0434 | 0.1193 | 0.2747 | 0.1475 | 0.5580 | 0.0791 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55` | 5-54 | 0.0416 | 0.0716 | 0.2789 | 0.1466 | 0.5022 | 0.0692 | None | 90.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55` | 5-54 | 0.0437 | 0.0736 | 0.2592 | 0.1475 | 0.5022 | 0.0717 | None | 94.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55` | 10-59 | 0.0403 | 0.0522 | 0.2596 | 0.1467 | 0.5134 | 0.0717 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p3927_ld0p36_ls0p55` | 5-54 | 0.0480 | 0.0738 | 0.2953 | 0.1460 | 0.5155 | 0.0722 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p42_ld0p36_ls0p75` | 5-54 | 0.0426 | 0.0776 | 0.3124 | 0.1460 | 0.4324 | 0.0687 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p68_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p36_ls0p55` | 5-54 | 0.0429 | 0.0695 | 0.2837 | 0.1466 | 0.4314 | 0.0679 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p37_ld0p36_ls0p75` | 5-54 | 0.0450 | 0.0856 | 0.3153 | 0.1455 | 0.4659 | 0.0707 | None | 94.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 5-54 | 0.0452 | 0.1086 | 0.2758 | 0.1473 | 0.4501 | 0.0700 | None | 94.0000 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p3_ls0p55` | 5-54 | 0.0415 | 0.1061 | 0.2554 | 0.1482 | 0.4194 | 0.0684 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p37_ld0p3_ls0p75` | 5-54 | 0.0405 | 0.0735 | 0.2781 | 0.1467 | 0.4304 | 0.0682 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 5-54 | 0.0413 | 0.0792 | 0.3278 | 0.1464 | 0.5707 | 0.0679 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p47_ld0p36_ls0p75` | 5-54 | 0.0435 | 0.0805 | 0.3092 | 0.1457 | 0.4894 | 0.0723 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p36_ls1` | 5-54 | 0.0430 | 0.0873 | 0.3328 | 0.1462 | 0.4934 | 0.0801 | None | 94.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p42_ld0p3_ls0p75` | 5-54 | 0.0416 | 0.1119 | 0.2896 | 0.1461 | 0.5479 | 0.0741 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p42_ld0p24_ls0p75` | 5-54 | 0.0411 | 0.0974 | 0.3425 | 0.1457 | 0.5246 | 0.0698 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p36_ls1` | 5-54 | 0.0423 | 0.0996 | 0.3134 | 0.1455 | 0.8750 | 0.0800 | None | 94.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p47_ld0p36_ls0p55` | 0-49 | 0.0466 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p47_ld0p36_ls0p55` | 0-49 | 0.0520 | `high_lateral_velocity, single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p47_ld0p36_ls0p55` | 5-54 | 0.0426 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p47_ld0p36_ls0p55` | 10-59 | 0.0412 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p37_ld0p24_ls0p75` | 0-49 | 0.0404 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p37_ld0p24_ls0p75` | 0-49 | 0.0455 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p75` | 0-49 | 0.0416 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p75` | 0-49 | 0.0475 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p42_ld0p3_ls1` | 0-49 | 0.0461 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p42_ld0p3_ls1` | 0-49 | 0.0494 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p42_ld0p3_ls1` | 5-54 | 0.0411 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p34_ld0p36_ls1` | 0-49 | 0.0511 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p34_ld0p36_ls1` | 0-49 | 0.0485 | `high_lateral_velocity, single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p34_ld0p36_ls1` | 5-54 | 0.0409 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p3_ls0p55` | 0-49 | 0.0417 | `high_lateral_velocity` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
