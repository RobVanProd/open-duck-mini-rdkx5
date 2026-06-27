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

- mined_windows: `264`
- pass_curated_seed_windows: `42`
- review_motion_hints: `222`
- rejected_dataset_seeds: `0`
- curated_source_files: `2`
- curated_modes: `36`
- curated_source_mode_pairs: `36`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 0-49 | 0.0447 | 0.1110 | 0.2827 | 0.1481 | 0.5073 | 0.0827 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 0-49 | 0.0458 | 0.1126 | 0.2921 | 0.1479 | 0.5386 | 0.0807 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 5-54 | 0.0412 | 0.0721 | 0.2921 | 0.1477 | 0.5550 | 0.0666 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 0-49 | 0.0497 | 0.1184 | 0.3287 | 0.1458 | 0.4217 | 0.0879 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 5-54 | 0.0458 | 0.0916 | 0.3287 | 0.1458 | 0.5381 | 0.0798 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p22_ls0p65` | 0-49 | 0.0428 | 0.1162 | 0.2770 | 0.1482 | 0.5073 | 0.0824 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 5-54 | 0.0419 | 0.0844 | 0.3107 | 0.1472 | 0.4215 | 0.0733 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p3_ls1` | 5-54 | 0.0487 | 0.1001 | 0.3275 | 0.1457 | 0.4934 | 0.0783 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 5-54 | 0.0416 | 0.0812 | 0.2847 | 0.1472 | 0.3575 | 0.0728 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 5-54 | 0.0448 | 0.0960 | 0.3283 | 0.1454 | 0.4794 | 0.0809 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 5-54 | 0.0466 | 0.0850 | 0.3431 | 0.1458 | 0.6601 | 0.0661 | None | 86.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 5-54 | 0.0407 | 0.0785 | 0.3198 | 0.1464 | 0.4821 | 0.0663 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p32_ld0p22_ls0p65` | 5-54 | 0.0413 | 0.0753 | 0.2772 | 0.1478 | 0.4807 | 0.0648 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65` | 5-54 | 0.0417 | 0.1110 | 0.2699 | 0.1471 | 0.5134 | 0.0725 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 0-49 | 0.0436 | 0.1178 | 0.2775 | 0.1473 | 0.5893 | 0.0821 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 5-54 | 0.0444 | 0.0880 | 0.3165 | 0.1468 | 0.3767 | 0.0728 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 5-54 | 0.0421 | 0.0767 | 0.3000 | 0.1474 | 0.2641 | 0.0697 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 0-49 | 0.0434 | 0.1170 | 0.2716 | 0.1489 | 0.3567 | 0.0774 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 5-54 | 0.0406 | 0.0625 | 0.2716 | 0.1489 | 0.3475 | 0.0654 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p32_ld0p22_ls0p65` | 0-49 | 0.0463 | 0.1185 | 0.2809 | 0.1483 | 0.4423 | 0.0787 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p32_ld0p22_ls0p65` | 5-54 | 0.0437 | 0.0612 | 0.2809 | 0.1482 | 0.3893 | 0.0655 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 5-54 | 0.0475 | 0.0931 | 0.3352 | 0.1461 | 0.3767 | 0.0754 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 5-54 | 0.0529 | 0.0933 | 0.3448 | 0.1454 | 0.3767 | 0.0749 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p22_ls1` | 5-54 | 0.0416 | 0.0786 | 0.3014 | 0.1473 | 0.3708 | 0.0712 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 5-54 | 0.0405 | 0.0578 | 0.2679 | 0.1484 | 0.3893 | 0.0674 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls1` | 5-54 | 0.0479 | 0.0999 | 0.3425 | 0.1458 | 0.3698 | 0.0753 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p32_ld0p3_ls0p65` | 5-54 | 0.0457 | 0.0624 | 0.2792 | 0.1482 | 0.3924 | 0.0629 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 0-49 | 0.0543 | 0.1127 | 0.3289 | 0.1462 | 0.5142 | 0.0741 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 5-54 | 0.0543 | 0.0746 | 0.3289 | 0.1462 | 0.4952 | 0.0656 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 5-54 | 0.0428 | 0.0584 | 0.2694 | 0.1483 | 0.3924 | 0.0634 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p22_ls1` | 5-54 | 0.0401 | 0.0683 | 0.2922 | 0.1474 | 0.2413 | 0.0698 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 5-54 | 0.0453 | 0.0606 | 0.2772 | 0.1480 | 0.3885 | 0.0671 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 0-49 | 0.0438 | 0.1198 | 0.2758 | 0.1480 | 0.4162 | 0.0708 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 5-54 | 0.0470 | 0.0690 | 0.3009 | 0.1470 | 0.3924 | 0.0682 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls1` | 5-54 | 0.0431 | 0.0751 | 0.3125 | 0.1472 | 0.3414 | 0.0700 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrphm1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p3_ls0p65` | 5-54 | 0.0412 | 0.0561 | 0.2591 | 0.1485 | 0.3851 | 0.0616 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 5-54 | 0.0439 | 0.0755 | 0.3089 | 0.1468 | 0.2926 | 0.0692 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 5-54 | 0.0477 | 0.0839 | 0.3245 | 0.1460 | 0.2940 | 0.0692 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p22_ls0p65` | 5-54 | 0.0405 | 0.0559 | 0.2619 | 0.1481 | 0.3860 | 0.0659 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls1` | 5-54 | 0.0493 | 0.0941 | 0.3322 | 0.1458 | 0.3905 | 0.0718 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p3_ls1` | 5-54 | 0.0459 | 0.0843 | 0.3190 | 0.1457 | 0.3902 | 0.0728 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 5-54 | 0.0402 | 0.0631 | 0.2684 | 0.1483 | 0.3919 | 0.0662 | None | 94.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 0-49 | 0.0432 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 0-49 | 0.0510 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 5-54 | 0.0420 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 10-59 | 0.0415 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 0-49 | 0.0504 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 5-54 | 0.0414 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 10-59 | 0.0408 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 0-49 | 0.0408 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 0-49 | 0.0487 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 5-54 | 0.0428 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 10-59 | 0.0407 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 0-49 | 0.0495 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 5-54 | 0.0416 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 10-59 | 0.0415 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 0-49 | 0.0517 | `high_lateral_velocity` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
