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

- mined_windows: `338`
- pass_curated_seed_windows: `59`
- review_motion_hints: `279`
- rejected_dataset_seeds: `0`
- curated_source_files: `1`
- curated_modes: `46`
- curated_source_mode_pairs: `46`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p47_ld0p3_ls0p35` | 5-54 | 0.0564 | 0.0662 | 0.3388 | 0.1462 | 0.3898 | 0.0725 | 81 | 92.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927_ld0p3_ls0p35` | 0-49 | 0.0451 | 0.1188 | 0.2740 | 0.1477 | 0.4071 | 0.0789 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927_ld0p3_ls0p35` | 5-54 | 0.0426 | 0.0528 | 0.2743 | 0.1475 | 0.3546 | 0.0714 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p38_ls1` | 5-54 | 0.0424 | 0.0911 | 0.3027 | 0.1472 | 0.9367 | 0.0701 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_a0_ph0p3927_ld0p22_ls1` | 5-54 | 0.0454 | 0.0784 | 0.3173 | 0.1476 | 0.3311 | 0.0679 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p0075_ph0p3927_ld0p22_ls0p65` | 5-54 | 0.0472 | 0.0754 | 0.3176 | 0.1476 | 0.3354 | 0.0649 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p38_ls0p35` | 0-49 | 0.0494 | 0.1190 | 0.2974 | 0.1467 | 0.4605 | 0.0797 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p38_ls0p35` | 5-54 | 0.0474 | 0.0616 | 0.2999 | 0.1467 | 0.4605 | 0.0722 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p00875_ph0p32_ld0p38_ls0p35` | 5-54 | 0.0575 | 0.0772 | 0.3449 | 0.1463 | 0.3918 | 0.0710 | 91 | 92.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p014_ph0p3927_ld0p3_ls0p35` | 0-49 | 0.0433 | 0.1120 | 0.2714 | 0.1490 | 0.3911 | 0.0777 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p014_ph0p3927_ld0p3_ls0p35` | 5-54 | 0.0406 | 0.0611 | 0.2714 | 0.1490 | 0.3863 | 0.0673 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p54_ld0p22_ls0p35` | 5-54 | 0.0498 | 0.0652 | 0.3201 | 0.1473 | 0.3838 | 0.0713 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p003_ph0p3927_ld0p38_ls0p65` | 5-54 | 0.0501 | 0.0786 | 0.3327 | 0.1465 | 0.3515 | 0.0739 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p003_ph0p54_ld0p3_ls0p65` | 5-54 | 0.0410 | 0.0627 | 0.2651 | 0.1488 | 0.3510 | 0.0638 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p00875_ph0p47_ld0p22_ls0p35` | 0-49 | 0.0432 | 0.1183 | 0.2753 | 0.1478 | 0.3903 | 0.0790 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p00875_ph0p47_ld0p22_ls0p35` | 5-54 | 0.0403 | 0.0627 | 0.2753 | 0.1476 | 0.3903 | 0.0708 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p3927_ld0p22_ls0p35` | 5-54 | 0.0550 | 0.0633 | 0.3344 | 0.1460 | 0.3913 | 0.0742 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p0075_ph0p32_ld0p38_ls0p65` | 5-54 | 0.0403 | 0.0717 | 0.2747 | 0.1480 | 0.3499 | 0.0688 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p0075_ph0p54_ld0p22_ls0p35` | 0-49 | 0.0424 | 0.1153 | 0.2691 | 0.1475 | 0.3623 | 0.0794 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p38_ls0p65` | 5-54 | 0.0433 | 0.0763 | 0.2876 | 0.1473 | 0.4083 | 0.0676 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p3927_ld0p22_ls0p35` | 5-54 | 0.0440 | 0.0478 | 0.2735 | 0.1478 | 0.3102 | 0.0665 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p01_ph0p47_ld0p38_ls0p35` | 5-54 | 0.0458 | 0.0574 | 0.2797 | 0.1478 | 0.3454 | 0.0656 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p01_ph0p47_ld0p38_ls0p35` | 0-49 | 0.0440 | 0.1186 | 0.2741 | 0.1485 | 0.3454 | 0.0725 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p54_ld0p38_ls1` | 5-54 | 0.0444 | 0.0830 | 0.3253 | 0.1461 | 0.4938 | 0.0756 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p0035_ph0p47_ld0p3_ls0p35` | 5-54 | 0.0508 | 0.0633 | 0.3048 | 0.1468 | 0.3606 | 0.0670 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p0035_ph0p47_ld0p3_ls0p35` | 0-49 | 0.0485 | 0.1155 | 0.2995 | 0.1476 | 0.3760 | 0.0748 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p32_ld0p38_ls0p35` | 5-54 | 0.0461 | 0.0634 | 0.2861 | 0.1479 | 0.3454 | 0.0662 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p32_ld0p38_ls0p35` | 0-49 | 0.0441 | 0.1174 | 0.2776 | 0.1487 | 0.3454 | 0.0718 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p0075_ph0p32_ld0p3_ls0p65` | 5-54 | 0.0437 | 0.0660 | 0.2745 | 0.1488 | 0.3364 | 0.0657 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p00625_ph0p54_ld0p22_ls0p35` | 5-54 | 0.0441 | 0.0537 | 0.2745 | 0.1475 | 0.3930 | 0.0672 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p00625_ph0p54_ld0p22_ls0p35` | 0-49 | 0.0422 | 0.1183 | 0.2687 | 0.1484 | 0.4022 | 0.0745 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p54_ld0p22_ls0p65` | 5-54 | 0.0422 | 0.0632 | 0.2687 | 0.1483 | 0.3426 | 0.0651 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p54_ld0p22_ls0p35` | 5-54 | 0.0469 | 0.0535 | 0.2920 | 0.1470 | 0.4585 | 0.0666 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p54_ld0p22_ls0p35` | 0-49 | 0.0449 | 0.1154 | 0.2920 | 0.1474 | 0.4693 | 0.0746 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p68_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p38_ls0p65` | 5-54 | 0.0466 | 0.0750 | 0.3149 | 0.1461 | 0.3575 | 0.0685 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p68_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p32_ld0p38_ls0p35` | 5-54 | 0.0458 | 0.0677 | 0.2834 | 0.1481 | 0.3251 | 0.0689 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_a0_ph0p54_ld0p22_ls0p35` | 5-54 | 0.0577 | 0.0590 | 0.3439 | 0.1467 | 0.3700 | 0.0643 | 65 | 94.0000 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_a0_ph0p3927_ld0p38_ls0p65` | 5-54 | 0.0456 | 0.0677 | 0.2881 | 0.1486 | 0.3187 | 0.0655 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p00625_ph0p3927_ld0p38_ls0p35` | 5-54 | 0.0442 | 0.0619 | 0.2819 | 0.1478 | 0.3251 | 0.0677 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p54_ld0p3_ls0p35` | 5-54 | 0.0552 | 0.0630 | 0.3400 | 0.1461 | 0.3609 | 0.0711 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p54_ld0p38_ls0p35` | 5-54 | 0.0489 | 0.0556 | 0.3013 | 0.1468 | 0.3793 | 0.0648 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p54_ld0p38_ls0p35` | 0-49 | 0.0448 | 0.1171 | 0.2851 | 0.1473 | 0.3793 | 0.0729 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_a0_ph0p32_ld0p38_ls1` | 5-54 | 0.0433 | 0.0845 | 0.3431 | 0.1456 | 0.3585 | 0.0770 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p00875_ph0p47_ld0p38_ls0p35` | 5-54 | 0.0430 | 0.0665 | 0.2748 | 0.1482 | 0.3170 | 0.0673 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p32_ld0p38_ls0p35` | 5-54 | 0.0451 | 0.0672 | 0.2851 | 0.1476 | 0.3251 | 0.0690 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_a0_ph0p3927_ld0p22_ls0p65` | 5-54 | 0.0515 | 0.0629 | 0.3254 | 0.1468 | 0.3038 | 0.0660 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p012_ph0p3927_ld0p22_ls0p65` | 5-54 | 0.0512 | 0.0684 | 0.3270 | 0.1460 | 0.3544 | 0.0659 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p47_ld0p22_ls0p35` | 0-49 | 0.0430 | 0.1183 | 0.2694 | 0.1484 | 0.2931 | 0.0777 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p47_ld0p22_ls0p35` | 5-54 | 0.0428 | 0.0495 | 0.2724 | 0.1474 | 0.2921 | 0.0679 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p00875_ph0p47_ld0p3_ls0p65` | 5-54 | 0.0439 | 0.0688 | 0.2787 | 0.1482 | 0.3653 | 0.0654 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p47_ld0p22_ls0p65` | 5-54 | 0.0494 | 0.0746 | 0.3380 | 0.1472 | 0.3533 | 0.0641 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p0075_ph0p54_ld0p38_ls0p65` | 5-54 | 0.0400 | 0.0641 | 0.2611 | 0.1491 | 0.3121 | 0.0649 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p54_ld0p22_ls0p65` | 5-54 | 0.0497 | 0.0774 | 0.3273 | 0.1476 | 0.3566 | 0.0676 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p012_ph0p32_ld0p3_ls0p35` | 0-49 | 0.0421 | 0.1176 | 0.2619 | 0.1493 | 0.3425 | 0.0755 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p012_ph0p32_ld0p3_ls0p35` | 5-54 | 0.0416 | 0.0588 | 0.2619 | 0.1493 | 0.3323 | 0.0654 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p47_ld0p38_ls0p65` | 5-54 | 0.0505 | 0.0798 | 0.3327 | 0.1457 | 0.3355 | 0.0716 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p0035_ph0p54_ld0p38_ls0p35` | 0-49 | 0.0423 | 0.1175 | 0.2659 | 0.1485 | 0.3566 | 0.0759 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p0035_ph0p54_ld0p38_ls0p35` | 5-54 | 0.0413 | 0.0527 | 0.2659 | 0.1483 | 0.3566 | 0.0685 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p0075_ph0p32_ld0p22_ls1` | 5-54 | 0.0454 | 0.0816 | 0.3282 | 0.1471 | 0.3063 | 0.0723 | None | 92.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p3927_ld0p38_ls1` | 0-49 | 0.0422 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p3927_ld0p38_ls1` | 0-49 | 0.0492 | `high_lateral_velocity, single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p3927_ld0p38_ls1` | 5-54 | 0.0435 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p3927_ld0p38_ls1` | 10-59 | 0.0416 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p47_ld0p3_ls0p35` | 0-49 | 0.0564 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p47_ld0p3_ls0p35` | 0-49 | 0.0618 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_am0p014_ph0p47_ld0p38_ls0p65` | 0-49 | 0.0594 | `high_lateral_velocity, single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_am0p014_ph0p47_ld0p38_ls0p65` | 5-54 | 0.0530 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927_ld0p3_ls0p35` | 0-49 | 0.0543 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927_ld0p3_ls0p35` | 5-54 | 0.0474 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927_ld0p3_ls0p35` | 10-59 | 0.0468 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927_ld0p3_ls0p35` | 15-64 | 0.0404 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p38_ls1` | 0-49 | 0.0458 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p38_ls1` | 0-49 | 0.0496 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p38_ls1` | 5-54 | 0.0448 | `single_contact_pattern_dominates` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
