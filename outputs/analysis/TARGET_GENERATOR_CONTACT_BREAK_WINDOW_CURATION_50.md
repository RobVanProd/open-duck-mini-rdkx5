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

- mined_windows: `201`
- pass_curated_seed_windows: `70`
- review_motion_hints: `131`
- rejected_dataset_seeds: `0`
- curated_source_files: `1`
- curated_modes: `38`
- curated_source_mode_pairs: `38`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 0-49 | 0.0517 | 0.1058 | 0.3137 | 0.1468 | 0.6096 | 0.0831 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 5-54 | 0.0509 | 0.0636 | 0.3137 | 0.1468 | 0.6096 | 0.0659 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927` | 5-54 | 0.0543 | 0.0633 | 0.3215 | 0.1463 | 0.5527 | 0.0722 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927` | 0-49 | 0.0520 | 0.1115 | 0.3097 | 0.1463 | 0.5527 | 0.0847 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p47` | 5-54 | 0.0544 | 0.0656 | 0.3220 | 0.1462 | 0.5550 | 0.0712 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p47` | 0-49 | 0.0523 | 0.1085 | 0.3112 | 0.1462 | 0.5550 | 0.0853 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p003_ph0p3927` | 5-54 | 0.0572 | 0.0804 | 0.3282 | 0.1461 | 0.6448 | 0.0685 | 54 | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p003_ph0p3927` | 0-49 | 0.0532 | 0.1104 | 0.3109 | 0.1461 | 0.6448 | 0.0849 | 59 | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p0025_ph0p52` | 5-54 | 0.0531 | 0.0721 | 0.3174 | 0.1466 | 0.6614 | 0.0701 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p0025_ph0p52` | 0-49 | 0.0501 | 0.1088 | 0.3015 | 0.1466 | 0.6021 | 0.0842 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p47` | 5-54 | 0.0530 | 0.0627 | 0.3156 | 0.1468 | 0.5550 | 0.0698 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p47` | 0-49 | 0.0526 | 0.1020 | 0.3126 | 0.1468 | 0.5550 | 0.0842 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0_ph0p3927` | 5-54 | 0.0535 | 0.0675 | 0.3091 | 0.1469 | 0.7369 | 0.0655 | 84 | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0_ph0p3927` | 0-49 | 0.0494 | 0.1050 | 0.2844 | 0.1469 | 0.7369 | 0.0799 | 89 | 90.0000 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p005_ph0p36` | 5-54 | 0.0529 | 0.0678 | 0.3219 | 0.1460 | 0.5221 | 0.0716 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p005_ph0p36` | 0-49 | 0.0507 | 0.1090 | 0.3070 | 0.1460 | 0.5560 | 0.0836 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p47` | 5-54 | 0.0554 | 0.0688 | 0.3242 | 0.1460 | 0.6475 | 0.0667 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p47` | 0-49 | 0.0547 | 0.1075 | 0.3242 | 0.1460 | 0.6475 | 0.0872 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p43` | 0-49 | 0.0514 | 0.1044 | 0.3128 | 0.1463 | 0.6096 | 0.0826 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p43` | 5-54 | 0.0512 | 0.0646 | 0.3133 | 0.1463 | 0.6096 | 0.0677 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p32` | 0-49 | 0.0485 | 0.1130 | 0.2996 | 0.1468 | 0.5088 | 0.0822 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p025_kb0p06_k0p16_ab0p04_am0p01_ph0p36` | 5-54 | 0.0578 | 0.0768 | 0.3368 | 0.1456 | 0.6304 | 0.0604 | 61 | 94.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p025_kb0p06_k0p16_ab0p04_am0p01_ph0p36` | 0-49 | 0.0535 | 0.1075 | 0.3189 | 0.1471 | 0.7780 | 0.0846 | 66 | 90.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927` | 5-54 | 0.0562 | 0.0655 | 0.3290 | 0.1461 | 0.5287 | 0.0689 | 58 | 94.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927` | 0-49 | 0.0518 | 0.1122 | 0.3108 | 0.1473 | 0.5484 | 0.0822 | 63 | 90.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p006_ph0p36` | 5-54 | 0.0503 | 0.0537 | 0.3029 | 0.1467 | 0.3940 | 0.0685 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p006_ph0p36` | 0-49 | 0.0484 | 0.1117 | 0.2950 | 0.1478 | 0.4863 | 0.0822 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p007_ph0p43` | 0-49 | 0.0525 | 0.1072 | 0.3105 | 0.1476 | 0.5479 | 0.0827 | 50 | 90.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p36` | 5-54 | 0.0536 | 0.0640 | 0.3213 | 0.1470 | 0.4728 | 0.0601 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p36` | 0-49 | 0.0532 | 0.1044 | 0.3213 | 0.1473 | 0.5835 | 0.0818 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p43` | 5-54 | 0.0521 | 0.0681 | 0.3004 | 0.1468 | 0.5364 | 0.0675 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p43` | 0-49 | 0.0472 | 0.1063 | 0.2736 | 0.1486 | 0.6392 | 0.0798 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p005_ph0p3927` | 5-54 | 0.0489 | 0.0587 | 0.3006 | 0.1463 | 0.4406 | 0.0685 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p005_ph0p3927` | 0-49 | 0.0471 | 0.1139 | 0.2914 | 0.1476 | 0.4570 | 0.0808 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p52` | 5-54 | 0.0561 | 0.0695 | 0.3260 | 0.1461 | 0.6068 | 0.0623 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p52` | 0-49 | 0.0544 | 0.1073 | 0.3259 | 0.1464 | 0.6406 | 0.0852 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p009_ph0p3927` | 5-54 | 0.0490 | 0.0580 | 0.2987 | 0.1466 | 0.4406 | 0.0673 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p009_ph0p3927` | 0-49 | 0.0475 | 0.1102 | 0.2967 | 0.1472 | 0.4570 | 0.0807 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p52` | 5-54 | 0.0508 | 0.0615 | 0.2998 | 0.1464 | 0.5245 | 0.0681 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p52` | 0-49 | 0.0457 | 0.1129 | 0.2769 | 0.1479 | 0.4962 | 0.0796 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0_ph0p47` | 5-54 | 0.0545 | 0.0654 | 0.3141 | 0.1465 | 0.5569 | 0.0693 | 65 | 94.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0_ph0p47` | 0-49 | 0.0482 | 0.1140 | 0.2881 | 0.1476 | 0.5209 | 0.0771 | 70 | 90.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p012_ph0p43` | 5-54 | 0.0568 | 0.0692 | 0.3287 | 0.1462 | 0.6107 | 0.0616 | 77 | 94.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p012_ph0p43` | 0-49 | 0.0523 | 0.1049 | 0.3177 | 0.1468 | 0.6079 | 0.0749 | 82 | 90.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p014_ph0p3927` | 5-54 | 0.0531 | 0.0665 | 0.3338 | 0.1470 | 0.4160 | 0.0614 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p014_ph0p3927` | 0-49 | 0.0527 | 0.1092 | 0.3338 | 0.1470 | 0.4160 | 0.0787 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p3927` | 0-49 | 0.0478 | 0.1189 | 0.3056 | 0.1466 | 0.4992 | 0.0772 | 59 | 92.0000 |
| seed_000.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p025_kb0p06_k0p16_ab0p04_am0p01_ph0p36` | 5-54 | 0.0573 | 0.0763 | 0.3298 | 0.1455 | 0.6604 | 0.0620 | 50 | 94.0000 |
| seed_000.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p025_kb0p06_k0p16_ab0p04_am0p01_ph0p36` | 0-49 | 0.0513 | 0.1080 | 0.3088 | 0.1466 | 0.6461 | 0.0754 | 55 | 90.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p16_ab0p04_am0p0075_ph0p36` | 0-49 | 0.0528 | 0.1044 | 0.3158 | 0.1460 | 0.7690 | 0.0864 | 51 | 90.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p04_a0_ph0p47` | 5-54 | 0.0477 | 0.0613 | 0.2956 | 0.1467 | 0.4490 | 0.0705 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p04_a0_ph0p47` | 0-49 | 0.0470 | 0.1172 | 0.2845 | 0.1478 | 0.4734 | 0.0797 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p01_ph0p3927` | 5-54 | 0.0484 | 0.0524 | 0.2974 | 0.1469 | 0.4000 | 0.0682 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p01_ph0p3927` | 0-49 | 0.0476 | 0.1099 | 0.2896 | 0.1480 | 0.4500 | 0.0801 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p16_ab0p04_am0p0035_ph0p32` | 0-49 | 0.0519 | 0.1080 | 0.3012 | 0.1466 | 0.8278 | 0.0830 | 54 | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p47` | 0-49 | 0.0525 | 0.1053 | 0.3173 | 0.1473 | 0.5681 | 0.0843 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p47` | 5-54 | 0.0520 | 0.0626 | 0.3173 | 0.1471 | 0.5388 | 0.0626 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p006_ph0p36` | 0-49 | 0.0548 | 0.1079 | 0.3211 | 0.1474 | 0.5767 | 0.0852 | 53 | 90.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p52` | 5-54 | 0.0559 | 0.0616 | 0.3270 | 0.1466 | 0.6189 | 0.0688 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p52` | 0-49 | 0.0539 | 0.1028 | 0.3181 | 0.1471 | 0.6233 | 0.0858 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p012_ph0p52` | 0-49 | 0.0489 | 0.1060 | 0.2951 | 0.1478 | 0.5194 | 0.0787 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p012_ph0p52` | 5-54 | 0.0478 | 0.0543 | 0.2952 | 0.1474 | 0.5157 | 0.0665 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p0025_ph0p3927` | 5-54 | 0.0542 | 0.0778 | 0.3184 | 0.1459 | 0.5600 | 0.0654 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p0025_ph0p3927` | 0-49 | 0.0503 | 0.1111 | 0.2973 | 0.1465 | 0.6300 | 0.0848 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p04_am0p014_ph0p36` | 5-54 | 0.0575 | 0.0767 | 0.3290 | 0.1458 | 0.5892 | 0.0615 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p04_am0p014_ph0p36` | 0-49 | 0.0547 | 0.1035 | 0.3261 | 0.1459 | 0.7690 | 0.0868 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0_ph0p36` | 5-54 | 0.0532 | 0.0653 | 0.3229 | 0.1459 | 0.4419 | 0.0697 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0_ph0p36` | 0-49 | 0.0502 | 0.1191 | 0.3085 | 0.1468 | 0.5767 | 0.0838 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p04_am0p012_ph0p32` | 5-54 | 0.0564 | 0.0779 | 0.3272 | 0.1457 | 0.7897 | 0.0608 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p04_am0p012_ph0p32` | 0-49 | 0.0542 | 0.1043 | 0.3228 | 0.1460 | 0.8278 | 0.0851 | None | 90.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 0-49 | 0.0528 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 5-54 | 0.0482 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 10-59 | 0.0458 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927` | 10-59 | 0.0457 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927` | 0-49 | 0.0568 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927` | 10-59 | 0.0539 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927` | 5-54 | 0.0527 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p47` | 10-59 | 0.0458 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p47` | 0-49 | 0.0570 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p47` | 10-59 | 0.0546 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p47` | 5-54 | 0.0530 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p0025_ph0p52` | 10-59 | 0.0457 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p47` | 10-59 | 0.0414 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p47` | 0-49 | 0.0560 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p47` | 10-59 | 0.0521 | `single_contact_pattern_dominates` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
