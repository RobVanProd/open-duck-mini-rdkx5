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

- mined_windows: `877`
- pass_curated_seed_windows: `207`
- review_motion_hints: `670`
- rejected_dataset_seeds: `0`
- curated_source_files: `2`
- curated_modes: `96`
- curated_source_mode_pairs: `111`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 5-29 | 0.0771 | 0.0931 | 0.2674 | 0.1474 | 0.4218 | 0.0598 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p45_ld0p3_ls0p55` | 5-29 | 0.0701 | 0.0791 | 0.2435 | 0.1484 | 0.4098 | 0.0584 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p45_ld0p3_ls0p55` | 10-34 | 0.0580 | 0.0599 | 0.2643 | 0.1483 | 0.4098 | 0.0587 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p45_ld0p3_ls0p55` | 15-39 | 0.0455 | 0.0496 | 0.2711 | 0.1483 | 0.3970 | 0.0641 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0045_ph0p45_ld0p34_ls0p65` | 5-29 | 0.0713 | 0.0875 | 0.2521 | 0.1475 | 0.5067 | 0.0593 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p45_ld0p3_ls0p65` | 5-29 | 0.0680 | 0.0899 | 0.2417 | 0.1486 | 0.4392 | 0.0600 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p45_ld0p3_ls0p65` | 10-34 | 0.0563 | 0.0590 | 0.2659 | 0.1485 | 0.4344 | 0.0600 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p45_ld0p3_ls0p65` | 15-39 | 0.0454 | 0.0431 | 0.2723 | 0.1485 | 0.4344 | 0.0641 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p34_ld0p26_ls0p65` | 5-29 | 0.0658 | 0.0857 | 0.2291 | 0.1493 | 0.4084 | 0.0583 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p45_ld0p3_ls0p65` | 5-29 | 0.0701 | 0.0869 | 0.2480 | 0.1477 | 0.5856 | 0.0579 | None | 84.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p45_ld0p3_ls0p65` | 10-34 | 0.0646 | 0.0629 | 0.2192 | 0.1487 | 0.5791 | 0.0602 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p45_ld0p3_ls0p65` | 15-39 | 0.0642 | 0.0629 | 0.2499 | 0.1479 | 0.5791 | 0.0719 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p45_ld0p3_ls0p65` | 20-44 | 0.0588 | 0.0629 | 0.2625 | 0.1479 | 0.5856 | 0.0739 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p45_ld0p3_ls0p65` | 5-29 | 0.0502 | 0.1159 | 0.1699 | 0.1494 | 0.5856 | 0.0579 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p58_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p37_ld0p26_ls0p75` | 5-29 | 0.0743 | 0.0932 | 0.2618 | 0.1471 | 0.4580 | 0.0592 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p58_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p3927_ld0p34_ls0p55` | 5-29 | 0.0708 | 0.0911 | 0.2508 | 0.1475 | 0.4740 | 0.0607 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p68_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00825_ph0p37_ld0p34_ls0p75` | 5-29 | 0.0768 | 0.0929 | 0.2672 | 0.1469 | 0.4574 | 0.0625 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p45_ld0p34_ls0p55` | 5-29 | 0.0714 | 0.0868 | 0.2509 | 0.1479 | 0.4553 | 0.0597 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p26_ls0p55` | 5-29 | 0.0667 | 0.0835 | 0.2362 | 0.1481 | 0.4740 | 0.0603 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p34_ld0p3_ls0p65` | 5-29 | 0.0733 | 0.0886 | 0.2559 | 0.1475 | 0.5290 | 0.0586 | None | 84.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p34_ld0p3_ls0p65` | 10-34 | 0.0608 | 0.0570 | 0.2144 | 0.1488 | 0.4579 | 0.0602 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p34_ld0p3_ls0p65` | 15-39 | 0.0557 | 0.0570 | 0.2373 | 0.1484 | 0.4579 | 0.0768 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p34_ld0p3_ls0p65` | 20-44 | 0.0463 | 0.0570 | 0.2407 | 0.1484 | 0.5290 | 0.0785 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p45_ld0p3_ls0p75` | 5-29 | 0.0722 | 0.0917 | 0.2533 | 0.1475 | 0.4563 | 0.0615 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm1_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p3927_ld0p34_ls0p75` | 5-29 | 0.0743 | 0.0929 | 0.2585 | 0.1479 | 0.4580 | 0.0639 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm1_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p3_ls0p75` | 5-29 | 0.0743 | 0.0915 | 0.2633 | 0.1470 | 0.4579 | 0.0626 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p34_ld0p26_ls0p75` | 5-29 | 0.0748 | 0.0925 | 0.2580 | 0.1477 | 0.4941 | 0.0593 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p0066_ph0p3927_ld0p26_ls0p65` | 5-29 | 0.0697 | 0.0879 | 0.2494 | 0.1473 | 0.5879 | 0.0581 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p45_ld0p3_ls0p55` | 5-29 | 0.0635 | 0.0880 | 0.2335 | 0.1476 | 0.5061 | 0.0598 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p26_ls0p55` | 5-29 | 0.0630 | 0.0893 | 0.2224 | 0.1489 | 0.4964 | 0.0591 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm1_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p45_ld0p34_ls0p75` | 5-29 | 0.0734 | 0.0886 | 0.2627 | 0.1467 | 0.7573 | 0.0654 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm1_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p34_ls0p65` | 5-29 | 0.0680 | 0.0932 | 0.2498 | 0.1472 | 0.5696 | 0.0578 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p42_ld0p3_ls0p55` | 5-29 | 0.0644 | 0.0895 | 0.2328 | 0.1480 | 0.5491 | 0.0606 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p42_ld0p3_ls0p55` | 10-34 | 0.0536 | 0.0585 | 0.2564 | 0.1479 | 0.5491 | 0.0632 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p42_ld0p3_ls0p55` | 15-39 | 0.0431 | 0.0482 | 0.2652 | 0.1479 | 0.5165 | 0.0686 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p3927_ld0p34_ls0p65` | 5-29 | 0.0735 | 0.0916 | 0.2620 | 0.1464 | 0.5696 | 0.0615 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p3927_ld0p34_ls0p65` | 20-44 | 0.0747 | 0.0656 | 0.2846 | 0.1467 | 0.5696 | 0.0807 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p3927_ld0p34_ls0p65` | 15-39 | 0.0733 | 0.0656 | 0.2684 | 0.1467 | 0.5489 | 0.0776 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p3927_ld0p34_ls0p65` | 10-34 | 0.0679 | 0.0656 | 0.2287 | 0.1475 | 0.5529 | 0.0646 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p3927_ld0p26_ls0p65` | 5-29 | 0.0668 | 0.0939 | 0.2359 | 0.1484 | 0.5468 | 0.0576 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p3927_ld0p26_ls0p65` | 10-34 | 0.0559 | 0.0582 | 0.2614 | 0.1483 | 0.5468 | 0.0621 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p3927_ld0p26_ls0p65` | 15-39 | 0.0454 | 0.0421 | 0.2691 | 0.1483 | 0.5269 | 0.0647 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p3927_ld0p26_ls0p65` | 10-34 | 0.0590 | 0.0485 | 0.1995 | 0.1490 | 0.5468 | 0.0615 | None | 84.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p3927_ld0p26_ls0p65` | 15-39 | 0.0565 | 0.0485 | 0.2255 | 0.1487 | 0.5269 | 0.0733 | None | 84.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p3927_ld0p26_ls0p65` | 20-44 | 0.0508 | 0.0485 | 0.2296 | 0.1487 | 0.5468 | 0.0738 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p3927_ld0p26_ls0p65` | 5-29 | 0.0431 | 0.1164 | 0.1456 | 0.1502 | 0.5468 | 0.0562 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p34_ld0p3_ls0p65` | 5-29 | 0.0652 | 0.0957 | 0.2373 | 0.1474 | 0.6046 | 0.0592 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p34_ld0p3_ls0p65` | 10-34 | 0.0527 | 0.0616 | 0.2577 | 0.1474 | 0.5536 | 0.0614 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p34_ld0p3_ls0p65` | 15-39 | 0.0442 | 0.0557 | 0.2675 | 0.1474 | 0.5536 | 0.0692 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p34_ld0p3_ls0p65` | 15-39 | 0.0711 | 0.0641 | 0.2602 | 0.1472 | 0.5536 | 0.0740 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p34_ld0p3_ls0p65` | 20-44 | 0.0705 | 0.0641 | 0.2779 | 0.1472 | 0.6046 | 0.0759 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p34_ld0p3_ls0p65` | 10-34 | 0.0678 | 0.0641 | 0.2240 | 0.1477 | 0.5536 | 0.0634 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 5-29 | 0.0696 | 0.0916 | 0.2451 | 0.1476 | 0.4815 | 0.0583 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 10-34 | 0.0569 | 0.0623 | 0.2724 | 0.1474 | 0.4815 | 0.0590 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 15-39 | 0.0480 | 0.0508 | 0.2787 | 0.1474 | 0.4645 | 0.0692 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p34_ls0p75` | 5-29 | 0.0798 | 0.0937 | 0.2774 | 0.1465 | 0.4805 | 0.0625 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p34_ls0p75` | 10-34 | 0.0632 | 0.0787 | 0.2992 | 0.1464 | 0.4805 | 0.0632 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p34_ls0p75` | 15-39 | 0.0498 | 0.0576 | 0.2992 | 0.1464 | 0.4761 | 0.0661 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p42_ld0p3_ls0p65` | 5-29 | 0.0688 | 0.0880 | 0.2449 | 0.1482 | 0.4821 | 0.0575 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p42_ld0p3_ls0p65` | 10-34 | 0.0570 | 0.0634 | 0.2683 | 0.1482 | 0.4821 | 0.0575 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p42_ld0p3_ls0p65` | 15-39 | 0.0456 | 0.0439 | 0.2750 | 0.1482 | 0.4685 | 0.0636 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p26_ls0p75` | 5-29 | 0.0708 | 0.0894 | 0.2512 | 0.1474 | 0.4819 | 0.0610 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p26_ls0p75` | 10-34 | 0.0578 | 0.0647 | 0.2731 | 0.1474 | 0.4714 | 0.0615 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p26_ls0p75` | 15-39 | 0.0480 | 0.0494 | 0.2753 | 0.1474 | 0.4714 | 0.0657 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p26_ls0p75` | 15-39 | 0.0667 | 0.0608 | 0.2414 | 0.1479 | 0.4714 | 0.0736 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p26_ls0p75` | 20-44 | 0.0660 | 0.0608 | 0.2563 | 0.1478 | 0.4819 | 0.0753 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p26_ls0p75` | 10-34 | 0.0624 | 0.0608 | 0.2056 | 0.1490 | 0.4714 | 0.0625 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00825_ph0p42_ld0p3_ls0p75` | 5-29 | 0.0711 | 0.0959 | 0.2494 | 0.1482 | 0.4788 | 0.0613 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p0066_ph0p34_ld0p26_ls0p65` | 5-29 | 0.0651 | 0.0878 | 0.2278 | 0.1490 | 0.4814 | 0.0584 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p0066_ph0p37_ld0p34_ls0p75` | 5-29 | 0.0732 | 0.0877 | 0.2580 | 0.1471 | 0.4820 | 0.0619 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p58_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p0066_ph0p37_ld0p3_ls0p75` | 5-29 | 0.0808 | 0.0898 | 0.2735 | 0.1470 | 0.4514 | 0.0610 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p42_ld0p34_ls0p75` | 5-29 | 0.0790 | 0.0938 | 0.2697 | 0.1472 | 0.4464 | 0.0629 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00825_ph0p34_ld0p34_ls0p55` | 5-29 | 0.0690 | 0.0878 | 0.2329 | 0.1488 | 0.3933 | 0.0592 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0075_ph0p42_ld0p26_ls0p75` | 5-29 | 0.0709 | 0.0922 | 0.2428 | 0.1483 | 0.3927 | 0.0592 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0075_ph0p42_ld0p26_ls0p75` | 10-34 | 0.0572 | 0.0639 | 0.2702 | 0.1480 | 0.3912 | 0.0610 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0075_ph0p42_ld0p26_ls0p75` | 15-39 | 0.0454 | 0.0449 | 0.2734 | 0.1480 | 0.3833 | 0.0616 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p9_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p3927_ld0p3_ls0p65` | 5-29 | 0.0714 | 0.0853 | 0.2455 | 0.1478 | 0.5759 | 0.0573 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p58_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p37_ld0p26_ls0p55` | 5-29 | 0.0682 | 0.0869 | 0.2324 | 0.1489 | 0.4375 | 0.0596 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p3927_ld0p3_ls0p75` | 5-29 | 0.0767 | 0.0924 | 0.2623 | 0.1470 | 0.4497 | 0.0604 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p75` | 5-29 | 0.0756 | 0.0930 | 0.2591 | 0.1471 | 0.4497 | 0.0600 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p75` | 10-34 | 0.0586 | 0.0703 | 0.2813 | 0.1470 | 0.4421 | 0.0614 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p75` | 15-39 | 0.0455 | 0.0495 | 0.2815 | 0.1470 | 0.4361 | 0.0661 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p42_ld0p34_ls0p55` | 5-29 | 0.0721 | 0.0905 | 0.2469 | 0.1482 | 0.4408 | 0.0596 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p42_ld0p34_ls0p55` | 10-34 | 0.0579 | 0.0681 | 0.2720 | 0.1478 | 0.4410 | 0.0580 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p42_ld0p34_ls0p55` | 15-39 | 0.0440 | 0.0471 | 0.2813 | 0.1478 | 0.4366 | 0.0674 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p37_ld0p34_ls0p75` | 5-29 | 0.0790 | 0.0896 | 0.2641 | 0.1476 | 0.4522 | 0.0624 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p45_ld0p34_ls0p65` | 5-29 | 0.0743 | 0.0913 | 0.2534 | 0.1479 | 0.4396 | 0.0595 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p26_ls0p65` | 5-29 | 0.0691 | 0.0850 | 0.2357 | 0.1484 | 0.4699 | 0.0584 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p9_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p34_ld0p26_ls0p75` | 5-29 | 0.0711 | 0.0891 | 0.2424 | 0.1483 | 0.4388 | 0.0620 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p9_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p34_ld0p26_ls0p75` | 10-34 | 0.0567 | 0.0679 | 0.2764 | 0.1478 | 0.4392 | 0.0623 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p9_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p34_ld0p26_ls0p75` | 15-39 | 0.0436 | 0.0449 | 0.2818 | 0.1478 | 0.4377 | 0.0655 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm1_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00495_ph0p34_ld0p26_ls0p65` | 5-29 | 0.0684 | 0.0844 | 0.2284 | 0.1492 | 0.4408 | 0.0590 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm1_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p45_ld0p26_ls0p55` | 5-29 | 0.0627 | 0.0827 | 0.2222 | 0.1486 | 0.4464 | 0.0602 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p26_ls0p65` | 5-29 | 0.0723 | 0.0895 | 0.2489 | 0.1477 | 0.4893 | 0.0566 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p26_ls0p65` | 10-34 | 0.0582 | 0.0659 | 0.2742 | 0.1475 | 0.4865 | 0.0593 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p26_ls0p65` | 15-39 | 0.0455 | 0.0471 | 0.2805 | 0.1475 | 0.4689 | 0.0651 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p3927_ld0p26_ls0p55` | 5-29 | 0.0683 | 0.0878 | 0.2333 | 0.1486 | 0.4812 | 0.0584 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p3927_ld0p26_ls0p55` | 10-34 | 0.0578 | 0.0484 | 0.2018 | 0.1488 | 0.4812 | 0.0613 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p3927_ld0p26_ls0p55` | 15-39 | 0.0539 | 0.0484 | 0.2332 | 0.1486 | 0.4446 | 0.0731 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p3927_ld0p26_ls0p55` | 20-44 | 0.0476 | 0.0484 | 0.2392 | 0.1486 | 0.4812 | 0.0771 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p3927_ld0p26_ls0p75` | 5-29 | 0.0716 | 0.0907 | 0.2429 | 0.1483 | 0.4864 | 0.0599 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p34_ld0p26_ls0p75` | 5-29 | 0.0719 | 0.0931 | 0.2435 | 0.1484 | 0.4841 | 0.0587 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p34_ld0p26_ls0p75` | 10-34 | 0.0586 | 0.0656 | 0.2732 | 0.1480 | 0.4839 | 0.0603 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p34_ld0p26_ls0p75` | 15-39 | 0.0459 | 0.0395 | 0.2774 | 0.1480 | 0.4594 | 0.0608 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p34_ld0p26_ls0p75` | 10-34 | 0.0542 | 0.0482 | 0.1762 | 0.1501 | 0.4839 | 0.0591 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p34_ld0p26_ls0p75` | 15-39 | 0.0535 | 0.0482 | 0.2109 | 0.1493 | 0.4594 | 0.0686 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p34_ld0p26_ls0p75` | 20-44 | 0.0515 | 0.0482 | 0.2243 | 0.1489 | 0.4841 | 0.0746 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p34_ld0p34_ls0p55` | 5-29 | 0.0692 | 0.0900 | 0.2358 | 0.1483 | 0.4784 | 0.0579 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p34_ld0p26_ls0p55` | 5-29 | 0.0668 | 0.0864 | 0.2299 | 0.1488 | 0.4784 | 0.0592 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p34_ld0p26_ls0p55` | 10-34 | 0.0576 | 0.0493 | 0.1992 | 0.1488 | 0.4833 | 0.0622 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p34_ld0p26_ls0p55` | 15-39 | 0.0529 | 0.0493 | 0.2301 | 0.1487 | 0.4564 | 0.0731 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p34_ld0p26_ls0p55` | 20-44 | 0.0458 | 0.0493 | 0.2369 | 0.1487 | 0.4833 | 0.0765 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p37_ld0p34_ls0p75` | 5-29 | 0.0788 | 0.0938 | 0.2713 | 0.1466 | 0.5273 | 0.0620 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p26_ls0p55` | 5-29 | 0.0652 | 0.0869 | 0.2333 | 0.1480 | 0.4844 | 0.0606 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p34_ls0p65` | 5-29 | 0.0769 | 0.0929 | 0.2646 | 0.1465 | 0.5484 | 0.0615 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p34_ls0p65` | 10-34 | 0.0599 | 0.0757 | 0.2867 | 0.1462 | 0.5371 | 0.0647 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p34_ls0p65` | 15-39 | 0.0471 | 0.0526 | 0.2906 | 0.1462 | 0.5255 | 0.0687 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0075_ph0p45_ld0p26_ls0p75` | 5-29 | 0.0707 | 0.0917 | 0.2482 | 0.1474 | 0.5303 | 0.0595 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0075_ph0p45_ld0p26_ls0p75` | 10-34 | 0.0570 | 0.0647 | 0.2728 | 0.1472 | 0.5225 | 0.0627 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0075_ph0p45_ld0p26_ls0p75` | 15-39 | 0.0453 | 0.0439 | 0.2744 | 0.1472 | 0.5023 | 0.0638 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p42_ld0p3_ls0p75` | 5-29 | 0.0744 | 0.0950 | 0.2551 | 0.1474 | 0.5320 | 0.0618 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p42_ld0p3_ls0p75` | 10-34 | 0.0596 | 0.0740 | 0.2835 | 0.1471 | 0.5298 | 0.0631 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p42_ld0p3_ls0p75` | 15-39 | 0.0453 | 0.0494 | 0.2851 | 0.1471 | 0.5216 | 0.0651 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p9_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p0066_ph0p42_ld0p3_ls0p65` | 5-29 | 0.0696 | 0.0905 | 0.2402 | 0.1482 | 0.5187 | 0.0595 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p9_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p37_ld0p3_ls0p65` | 5-29 | 0.0682 | 0.0937 | 0.2337 | 0.1483 | 0.5136 | 0.0588 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 5-29 | 0.0729 | 0.0922 | 0.2490 | 0.1475 | 0.4772 | 0.0565 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 10-34 | 0.0583 | 0.0655 | 0.2764 | 0.1472 | 0.4653 | 0.0577 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 15-39 | 0.0465 | 0.0496 | 0.2821 | 0.1472 | 0.4520 | 0.0669 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 10-34 | 0.0579 | 0.0552 | 0.2056 | 0.1489 | 0.4653 | 0.0571 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 15-39 | 0.0521 | 0.0552 | 0.2298 | 0.1486 | 0.4520 | 0.0738 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 20-44 | 0.0451 | 0.0552 | 0.2387 | 0.1484 | 0.5064 | 0.0756 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p42_ld0p34_ls0p55` | 5-29 | 0.0688 | 0.0878 | 0.2424 | 0.1476 | 0.4633 | 0.0597 | None | 76.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p42_ld0p34_ls0p55` | 10-34 | 0.0542 | 0.0628 | 0.2642 | 0.1473 | 0.4642 | 0.0597 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p42_ld0p34_ls0p55` | 15-39 | 0.0424 | 0.0534 | 0.2748 | 0.1473 | 0.4442 | 0.0704 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p3_ls0p75` | 5-29 | 0.0739 | 0.0934 | 0.2555 | 0.1470 | 0.4637 | 0.0601 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p45_ld0p3_ls0p55` | 5-29 | 0.0680 | 0.0870 | 0.2409 | 0.1477 | 0.4625 | 0.0598 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p45_ld0p3_ls0p55` | 10-34 | 0.0627 | 0.0599 | 0.2158 | 0.1481 | 0.4625 | 0.0603 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p45_ld0p3_ls0p55` | 15-39 | 0.0602 | 0.0599 | 0.2478 | 0.1480 | 0.4469 | 0.0737 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p45_ld0p3_ls0p55` | 20-44 | 0.0550 | 0.0599 | 0.2607 | 0.1480 | 0.4625 | 0.0750 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p34_ls0p65` | 5-29 | 0.0769 | 0.0927 | 0.2629 | 0.1469 | 0.5484 | 0.0612 | None | 76.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p34_ls0p65` | 10-34 | 0.0596 | 0.0733 | 0.2819 | 0.1467 | 0.5296 | 0.0618 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p34_ls0p65` | 15-39 | 0.0464 | 0.0539 | 0.2850 | 0.1467 | 0.4702 | 0.0666 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p58_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p3927_ld0p3_ls0p75` | 5-29 | 0.0727 | 0.0886 | 0.2544 | 0.1484 | 0.4734 | 0.0630 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p42_ld0p34_ls0p75` | 5-29 | 0.0784 | 0.0909 | 0.2809 | 0.1468 | 0.4994 | 0.0636 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p42_ld0p34_ls0p75` | 10-34 | 0.0634 | 0.0746 | 0.2909 | 0.1468 | 0.4834 | 0.0636 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p42_ld0p34_ls0p75` | 15-39 | 0.0527 | 0.0504 | 0.2921 | 0.1468 | 0.4834 | 0.0654 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p37_ld0p26_ls0p65` | 5-29 | 0.0700 | 0.0846 | 0.2501 | 0.1481 | 0.4628 | 0.0593 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p34_ld0p3_ls0p55` | 5-29 | 0.0661 | 0.0879 | 0.2358 | 0.1487 | 0.4251 | 0.0609 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p34_ld0p3_ls0p55` | 10-34 | 0.0557 | 0.0588 | 0.2589 | 0.1485 | 0.4251 | 0.0613 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p34_ld0p3_ls0p55` | 15-39 | 0.0446 | 0.0485 | 0.2660 | 0.1485 | 0.4181 | 0.0653 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p9_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p42_ld0p3_ls0p55` | 5-29 | 0.0680 | 0.0869 | 0.2480 | 0.1476 | 0.4795 | 0.0595 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p9_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p45_ld0p34_ls0p75` | 5-29 | 0.0715 | 0.0875 | 0.2615 | 0.1472 | 0.4979 | 0.0654 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p9_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p45_ld0p34_ls0p75` | 10-34 | 0.0587 | 0.0693 | 0.2791 | 0.1472 | 0.4796 | 0.0668 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p9_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p45_ld0p34_ls0p75` | 15-39 | 0.0504 | 0.0532 | 0.2807 | 0.1471 | 0.4796 | 0.0750 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm1_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p34_ld0p3_ls0p75` | 5-29 | 0.0698 | 0.0875 | 0.2512 | 0.1485 | 0.4373 | 0.0617 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm1_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p34_ld0p34_ls0p75` | 5-29 | 0.0756 | 0.0857 | 0.2692 | 0.1472 | 0.4441 | 0.0633 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p038_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p34_ld0p26_ls0p65` | 5-29 | 0.0665 | 0.0878 | 0.2443 | 0.1476 | 0.5425 | 0.0600 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p34_ls0p65` | 5-29 | 0.0739 | 0.0899 | 0.2666 | 0.1471 | 0.5214 | 0.0613 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p038_hrphm1_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p42_ld0p34_ls0p55` | 5-29 | 0.0649 | 0.0803 | 0.2420 | 0.1475 | 0.4930 | 0.0582 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p3927_ld0p34_ls0p65` | 5-29 | 0.0747 | 0.0907 | 0.2720 | 0.1465 | 0.5760 | 0.0617 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p042_hrphm0p9_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p34_ld0p26_ls0p75` | 5-29 | 0.0716 | 0.0903 | 0.2508 | 0.1485 | 0.5195 | 0.0611 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p58_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p34_ld0p26_ls0p75` | 5-29 | 0.0711 | 0.0964 | 0.2581 | 0.1468 | 0.5715 | 0.0596 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p58_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p34_ld0p26_ls0p75` | 10-34 | 0.0593 | 0.0609 | 0.2786 | 0.1468 | 0.5711 | 0.0652 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p58_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p34_ld0p26_ls0p75` | 15-39 | 0.0525 | 0.0537 | 0.2834 | 0.1468 | 0.5711 | 0.0669 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p58_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p34_ld0p26_ls0p75` | 10-34 | 0.0612 | 0.0573 | 0.2126 | 0.1488 | 0.5711 | 0.0628 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p58_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p34_ld0p26_ls0p75` | 15-39 | 0.0573 | 0.0573 | 0.2302 | 0.1483 | 0.5711 | 0.0753 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p42_ld0p3_ls0p65` | 5-29 | 0.0701 | 0.0920 | 0.2510 | 0.1478 | 0.5618 | 0.0614 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p42_ld0p3_ls0p65` | 10-34 | 0.0603 | 0.0583 | 0.2783 | 0.1476 | 0.5618 | 0.0636 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p42_ld0p3_ls0p65` | 15-39 | 0.0507 | 0.0466 | 0.2825 | 0.1476 | 0.5572 | 0.0685 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00525_ph0p37_ld0p3_ls0p75` | 5-29 | 0.0767 | 0.0997 | 0.2778 | 0.1463 | 0.5752 | 0.0633 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p34_ld0p34_ls0p55` | 5-29 | 0.0733 | 0.0943 | 0.2610 | 0.1475 | 0.5689 | 0.0615 | None | 76.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p34_ld0p34_ls0p55` | 10-34 | 0.0621 | 0.0645 | 0.2817 | 0.1475 | 0.5689 | 0.0615 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p34_ld0p34_ls0p55` | 15-39 | 0.0498 | 0.0492 | 0.2869 | 0.1475 | 0.5622 | 0.0647 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p45_ld0p3_ls0p55` | 5-29 | 0.0664 | 0.0897 | 0.2429 | 0.1474 | 0.5700 | 0.0593 | None | 80.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p45_ld0p3_ls0p55` | 10-34 | 0.0578 | 0.0625 | 0.2644 | 0.1473 | 0.5700 | 0.0634 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p45_ld0p3_ls0p55` | 15-39 | 0.0486 | 0.0625 | 0.2720 | 0.1473 | 0.5665 | 0.0695 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p34_ls0p55` | 5-29 | 0.0665 | 0.0907 | 0.2479 | 0.1473 | 0.5702 | 0.0602 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p34_ls0p55` | 10-34 | 0.0661 | 0.0601 | 0.2294 | 0.1479 | 0.5702 | 0.0649 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p34_ls0p55` | 15-39 | 0.0628 | 0.0601 | 0.2523 | 0.1478 | 0.5615 | 0.0762 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p34_ls0p55` | 20-44 | 0.0525 | 0.0601 | 0.2552 | 0.1478 | 0.5702 | 0.0794 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p34_ls0p55` | 5-29 | 0.0521 | 0.1101 | 0.1849 | 0.1483 | 0.5702 | 0.0627 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00495_ph0p34_ld0p34_ls0p65` | 5-29 | 0.0695 | 0.0979 | 0.2502 | 0.1478 | 0.5559 | 0.0604 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p37_ld0p26_ls0p55` | 5-29 | 0.0602 | 0.0897 | 0.2294 | 0.1479 | 0.5721 | 0.0593 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p37_ld0p26_ls0p55` | 10-34 | 0.0512 | 0.0595 | 0.2492 | 0.1478 | 0.5721 | 0.0637 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p37_ld0p26_ls0p55` | 15-39 | 0.0429 | 0.0595 | 0.2609 | 0.1478 | 0.5676 | 0.0722 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65` | 5-29 | 0.0672 | 0.0943 | 0.2470 | 0.1475 | 0.5741 | 0.0617 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65` | 10-34 | 0.0655 | 0.0574 | 0.2245 | 0.1482 | 0.5734 | 0.0629 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65` | 15-39 | 0.0628 | 0.0574 | 0.2465 | 0.1480 | 0.5703 | 0.0772 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65` | 20-44 | 0.0529 | 0.0574 | 0.2481 | 0.1480 | 0.5741 | 0.0788 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65` | 5-29 | 0.0514 | 0.1130 | 0.1779 | 0.1486 | 0.5741 | 0.0604 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p58_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p65` | 5-29 | 0.0729 | 0.0931 | 0.2596 | 0.1479 | 0.5003 | 0.0615 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p58_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p65` | 10-34 | 0.0618 | 0.0646 | 0.2839 | 0.1478 | 0.5003 | 0.0624 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p58_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p65` | 15-39 | 0.0500 | 0.0434 | 0.2869 | 0.1478 | 0.5003 | 0.0674 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p0066_ph0p45_ld0p26_ls0p65` | 5-29 | 0.0694 | 0.0884 | 0.2498 | 0.1481 | 0.5012 | 0.0609 | None | 88.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p0066_ph0p45_ld0p26_ls0p65` | 10-34 | 0.0633 | 0.0556 | 0.2188 | 0.1488 | 0.4993 | 0.0632 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p0066_ph0p45_ld0p26_ls0p65` | 15-39 | 0.0595 | 0.0556 | 0.2392 | 0.1485 | 0.5012 | 0.0745 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p0066_ph0p45_ld0p26_ls0p65` | 5-29 | 0.0501 | 0.1180 | 0.1741 | 0.1493 | 0.5012 | 0.0604 | None | 92.0000 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p0066_ph0p45_ld0p26_ls0p65` | 20-44 | 0.0489 | 0.0556 | 0.2396 | 0.1485 | 0.5012 | 0.0768 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p0066_ph0p3927_ld0p3_ls0p55` | 5-29 | 0.0649 | 0.0875 | 0.2407 | 0.1475 | 0.5022 | 0.0586 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p42_ld0p34_ls0p75` | 5-29 | 0.0761 | 0.0950 | 0.2699 | 0.1477 | 0.4989 | 0.0632 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00825_ph0p34_ld0p34_ls0p75` | 5-29 | 0.0767 | 0.0940 | 0.2772 | 0.1467 | 0.5005 | 0.0639 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00825_ph0p34_ld0p34_ls0p75` | 10-34 | 0.0620 | 0.0753 | 0.2932 | 0.1467 | 0.5003 | 0.0638 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00825_ph0p34_ld0p34_ls0p75` | 15-39 | 0.0497 | 0.0518 | 0.2932 | 0.1467 | 0.4948 | 0.0670 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p3927_ld0p26_ls0p55` | 5-29 | 0.0608 | 0.0879 | 0.2283 | 0.1480 | 0.5079 | 0.0593 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p34_ld0p3_ls0p55` | 5-29 | 0.0639 | 0.0887 | 0.2340 | 0.1481 | 0.4991 | 0.0607 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p45_ld0p34_ls0p55` | 5-29 | 0.0663 | 0.0858 | 0.2473 | 0.1474 | 0.5008 | 0.0572 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 5-29 | 0.0668 | 0.0852 | 0.2417 | 0.1479 | 0.5111 | 0.0605 | None | 88.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 0-24 | 0.0731 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 10-34 | 0.0623 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 15-39 | 0.0494 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 15-39 | 0.0644 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 20-44 | 0.0637 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 10-34 | 0.0617 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 25-49 | 0.0558 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 5-29 | 0.0423 | `high_lateral_velocity, single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 0-24 | 0.0410 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p45_ld0p3_ls0p55` | 0-24 | 0.0676 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p45_ld0p3_ls0p55` | 10-34 | 0.0604 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p45_ld0p3_ls0p55` | 15-39 | 0.0565 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p45_ld0p3_ls0p55` | 0-24 | 0.0525 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p45_ld0p3_ls0p55` | 20-44 | 0.0486 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p45_ld0p3_ls0p55` | 5-29 | 0.0478 | `high_lateral_velocity, single_contact_pattern_dominates` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
