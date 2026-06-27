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

- mined_windows: `785`
- pass_curated_seed_windows: `87`
- review_motion_hints: `698`
- rejected_dataset_seeds: `0`
- curated_source_files: `1`
- curated_modes: `87`
- curated_source_mode_pairs: `87`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p3927_ld0p38_ls1` | 5-29 | 0.0817 | 0.0967 | 0.2690 | 0.1478 | 0.6809 | 0.0712 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p47_ld0p3_ls0p35` | 5-29 | 0.0847 | 0.0765 | 0.2734 | 0.1481 | 0.3903 | 0.0649 | 106 | 84.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927_ld0p3_ls0p35` | 5-29 | 0.0642 | 0.0677 | 0.2101 | 0.1499 | 0.3763 | 0.0621 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p38_ls1` | 5-29 | 0.0858 | 0.0955 | 0.2785 | 0.1476 | 1.0672 | 0.0704 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_a0_ph0p3927_ld0p22_ls1` | 5-29 | 0.0887 | 0.0962 | 0.2797 | 0.1485 | 0.3322 | 0.0662 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p0075_ph0p3927_ld0p22_ls0p65` | 5-29 | 0.0891 | 0.0848 | 0.2780 | 0.1487 | 0.3373 | 0.0643 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p54_ld0p22_ls1` | 5-29 | 0.0702 | 0.0965 | 0.2330 | 0.1496 | 0.2798 | 0.0686 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_a0_ph0p54_ld0p3_ls1` | 5-29 | 0.0992 | 0.0879 | 0.3156 | 0.1464 | 0.2798 | 0.0750 | 76 | 88.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p38_ls0p35` | 5-29 | 0.0666 | 0.0682 | 0.2187 | 0.1496 | 0.4605 | 0.0617 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p00875_ph0p32_ld0p38_ls0p35` | 5-29 | 0.0936 | 0.0811 | 0.2949 | 0.1476 | 0.3918 | 0.0684 | 116 | 84.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p0035_ph0p3927_ld0p22_ls1` | 5-29 | 0.0698 | 0.0954 | 0.2251 | 0.1506 | 0.3876 | 0.0669 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p014_ph0p3927_ld0p3_ls0p35` | 5-29 | 0.0767 | 0.0645 | 0.2452 | 0.1498 | 0.3907 | 0.0609 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p54_ld0p22_ls0p35` | 5-29 | 0.0820 | 0.0758 | 0.2642 | 0.1491 | 0.3858 | 0.0614 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p003_ph0p3927_ld0p38_ls0p65` | 5-29 | 0.0944 | 0.0809 | 0.3055 | 0.1470 | 0.3667 | 0.0683 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p003_ph0p54_ld0p3_ls0p65` | 5-29 | 0.0696 | 0.0765 | 0.2298 | 0.1492 | 0.4518 | 0.0590 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p00875_ph0p47_ld0p22_ls0p35` | 5-29 | 0.0669 | 0.0716 | 0.2254 | 0.1496 | 0.4567 | 0.0621 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p3927_ld0p22_ls0p35` | 5-29 | 0.0833 | 0.0744 | 0.2696 | 0.1480 | 0.4224 | 0.0644 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 5-29 | 0.0697 | 0.0797 | 0.2296 | 0.1491 | 0.3918 | 0.0598 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p0035_ph0p47_ld0p3_ls1` | 5-29 | 0.0723 | 0.0942 | 0.2416 | 0.1482 | 0.4154 | 0.0717 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p0075_ph0p32_ld0p38_ls0p65` | 5-29 | 0.0753 | 0.0827 | 0.2485 | 0.1486 | 0.3499 | 0.0653 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p0075_ph0p54_ld0p22_ls0p35` | 5-29 | 0.0619 | 0.0660 | 0.2126 | 0.1497 | 0.3903 | 0.0616 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p38_ls0p65` | 5-29 | 0.0819 | 0.0804 | 0.2657 | 0.1478 | 0.4083 | 0.0618 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p3927_ld0p22_ls0p35` | 5-29 | 0.0670 | 0.0692 | 0.2164 | 0.1494 | 0.2439 | 0.0605 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p01_ph0p47_ld0p38_ls0p35` | 5-29 | 0.0759 | 0.0668 | 0.2385 | 0.1491 | 0.2863 | 0.0623 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p0025_ph0p47_ld0p38_ls0p35` | 5-29 | 0.0962 | 0.0833 | 0.2971 | 0.1472 | 0.3340 | 0.0678 | 66 | 84.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p54_ld0p38_ls1` | 5-29 | 0.0946 | 0.0841 | 0.2732 | 0.1493 | 0.5752 | 0.0742 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p0035_ph0p47_ld0p3_ls0p35` | 5-29 | 0.0740 | 0.0688 | 0.2276 | 0.1494 | 0.3430 | 0.0623 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_a0_ph0p54_ld0p22_ls1` | 5-29 | 0.0886 | 0.0969 | 0.2670 | 0.1501 | 0.2909 | 0.0655 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p32_ld0p38_ls0p35` | 5-29 | 0.0754 | 0.0682 | 0.2390 | 0.1491 | 0.2811 | 0.0647 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p0075_ph0p32_ld0p3_ls0p65` | 5-29 | 0.0824 | 0.0761 | 0.2488 | 0.1502 | 0.2908 | 0.0665 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p00625_ph0p54_ld0p22_ls0p35` | 5-29 | 0.0683 | 0.0689 | 0.2208 | 0.1492 | 0.2479 | 0.0608 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls1` | 5-29 | 0.0751 | 0.0916 | 0.2276 | 0.1503 | 0.2313 | 0.0648 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p00625_ph0p54_ld0p22_ls1` | 5-29 | 0.0927 | 0.0948 | 0.2776 | 0.1491 | 0.2424 | 0.0659 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p01_ph0p32_ld0p3_ls1` | 5-29 | 0.0761 | 0.0910 | 0.2307 | 0.1507 | 0.2415 | 0.0665 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p01_ph0p54_ld0p38_ls1` | 5-29 | 0.0741 | 0.0939 | 0.2298 | 0.1505 | 0.4793 | 0.0687 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p54_ld0p22_ls1` | 5-29 | 0.0723 | 0.0949 | 0.2160 | 0.1506 | 0.3393 | 0.0647 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p00875_ph0p54_ld0p22_ls0p65` | 5-29 | 0.0699 | 0.0782 | 0.2138 | 0.1505 | 0.3393 | 0.0611 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_a0_ph0p54_ld0p3_ls0p35` | 5-29 | 0.0953 | 0.0769 | 0.2929 | 0.1475 | 0.3344 | 0.0624 | 73 | 84.0000 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p54_ld0p22_ls0p65` | 5-29 | 0.0744 | 0.0785 | 0.2308 | 0.1498 | 0.3393 | 0.0589 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p54_ld0p22_ls0p35` | 5-29 | 0.0766 | 0.0645 | 0.2440 | 0.1488 | 0.3426 | 0.0605 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p3927_ld0p3_ls1` | 5-29 | 0.0782 | 0.0925 | 0.2348 | 0.1507 | 0.2926 | 0.0650 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p68_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p38_ls0p65` | 5-29 | 0.0979 | 0.0806 | 0.2819 | 0.1490 | 0.3245 | 0.0698 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p68_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p32_ld0p38_ls0p35` | 5-29 | 0.0873 | 0.0713 | 0.2632 | 0.1486 | 0.2766 | 0.0647 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p54_ld0p3_ls1` | 5-29 | 0.0763 | 0.0913 | 0.2272 | 0.1507 | 0.2244 | 0.0666 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0025_ph0p54_ld0p38_ls0p35` | 5-29 | 0.1067 | 0.0743 | 0.3178 | 0.1473 | 0.2496 | 0.0666 | 60 | 88.0000 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_a0_ph0p54_ld0p22_ls0p35` | 5-29 | 0.0688 | 0.0722 | 0.2214 | 0.1496 | 0.2294 | 0.0595 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p0025_ph0p32_ld0p3_ls0p65` | 5-29 | 0.1036 | 0.0895 | 0.3078 | 0.1492 | 0.2315 | 0.0654 | 77 | 88.0000 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_a0_ph0p54_ld0p22_ls0p35` | 5-29 | 0.0929 | 0.0740 | 0.2748 | 0.1486 | 0.3211 | 0.0607 | 90 | 88.0000 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p06_am0p014_ph0p54_ld0p22_ls0p35` | 5-29 | 0.1012 | 0.0652 | 0.3003 | 0.1479 | 0.3211 | 0.0695 | 69 | 88.0000 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_a0_ph0p3927_ld0p38_ls0p65` | 5-29 | 0.0876 | 0.0811 | 0.2554 | 0.1503 | 0.3085 | 0.0643 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p012_ph0p32_ld0p38_ls1` | 5-29 | 0.0907 | 0.0983 | 0.2634 | 0.1502 | 0.2766 | 0.0752 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p54_ld0p22_ls1` | 5-29 | 0.0729 | 0.0921 | 0.2213 | 0.1506 | 0.2209 | 0.0652 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p00625_ph0p3927_ld0p38_ls0p35` | 5-29 | 0.0776 | 0.0743 | 0.2491 | 0.1484 | 0.2481 | 0.0655 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p54_ld0p3_ls0p35` | 5-29 | 0.0970 | 0.0710 | 0.2953 | 0.1472 | 0.2503 | 0.0682 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p54_ld0p38_ls0p35` | 5-29 | 0.0757 | 0.0629 | 0.2384 | 0.1487 | 0.2912 | 0.0624 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p00625_ph0p54_ld0p22_ls1` | 5-29 | 0.0698 | 0.0944 | 0.2155 | 0.1509 | 0.2209 | 0.0660 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_a0_ph0p32_ld0p38_ls1` | 5-29 | 0.1008 | 0.0930 | 0.2867 | 0.1496 | 0.3226 | 0.0758 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p00875_ph0p47_ld0p38_ls0p35` | 5-29 | 0.0774 | 0.0757 | 0.2391 | 0.1489 | 0.2981 | 0.0668 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p54_ld0p3_ls1` | 5-29 | 0.0765 | 0.0923 | 0.2267 | 0.1501 | 0.2693 | 0.0668 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p32_ld0p38_ls0p35` | 5-29 | 0.0852 | 0.0736 | 0.2616 | 0.1483 | 0.2766 | 0.0668 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_a0_ph0p3927_ld0p22_ls0p65` | 5-29 | 0.0977 | 0.0809 | 0.2880 | 0.1487 | 0.2697 | 0.0670 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p012_ph0p3927_ld0p22_ls0p65` | 5-29 | 0.0994 | 0.0795 | 0.2966 | 0.1482 | 0.2761 | 0.0664 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p3927_ld0p22_ls0p65` | 5-29 | 0.0719 | 0.0766 | 0.2253 | 0.1505 | 0.2679 | 0.0617 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p47_ld0p22_ls0p35` | 5-29 | 0.0636 | 0.0675 | 0.2099 | 0.1497 | 0.2874 | 0.0618 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p00875_ph0p47_ld0p3_ls0p65` | 5-29 | 0.0780 | 0.0696 | 0.2408 | 0.1492 | 0.3815 | 0.0628 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p47_ld0p22_ls0p65` | 5-29 | 0.0931 | 0.0841 | 0.2855 | 0.1487 | 0.3614 | 0.0617 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p003_ph0p47_ld0p3_ls1` | 5-29 | 0.1000 | 0.0942 | 0.3076 | 0.1474 | 0.3131 | 0.0710 | 55 | 92.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p0075_ph0p54_ld0p22_ls1` | 5-29 | 0.0859 | 0.0942 | 0.2659 | 0.1489 | 0.3078 | 0.0665 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p0075_ph0p54_ld0p38_ls0p65` | 5-29 | 0.0731 | 0.0775 | 0.2289 | 0.1499 | 0.3092 | 0.0598 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p47_ld0p3_ls1` | 5-29 | 0.0764 | 0.0922 | 0.2381 | 0.1497 | 0.2609 | 0.0650 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p00625_ph0p32_ld0p22_ls0p65` | 5-29 | 0.1025 | 0.0763 | 0.3068 | 0.1481 | 0.2824 | 0.0631 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p0035_ph0p32_ld0p22_ls1` | 5-29 | 0.0760 | 0.0903 | 0.2255 | 0.1512 | 0.3576 | 0.0654 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_a0_ph0p54_ld0p3_ls1` | 5-29 | 0.0734 | 0.0882 | 0.2232 | 0.1505 | 0.3607 | 0.0653 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p54_ld0p22_ls0p65` | 5-29 | 0.0917 | 0.0814 | 0.2766 | 0.1491 | 0.3591 | 0.0644 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p003_ph0p47_ld0p22_ls1` | 5-29 | 0.0722 | 0.0954 | 0.2238 | 0.1504 | 0.3098 | 0.0654 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p012_ph0p3927_ld0p3_ls1` | 5-29 | 0.0772 | 0.0952 | 0.2313 | 0.1503 | 0.3126 | 0.0657 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p003_ph0p3927_ld0p3_ls1` | 5-29 | 0.0755 | 0.0942 | 0.2290 | 0.1508 | 0.3126 | 0.0645 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p012_ph0p32_ld0p3_ls0p35` | 5-29 | 0.0761 | 0.0686 | 0.2384 | 0.1498 | 0.3136 | 0.0597 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p47_ld0p38_ls0p65` | 5-29 | 0.0983 | 0.0812 | 0.3071 | 0.1467 | 0.3111 | 0.0666 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p01_ph0p47_ld0p3_ls1` | 5-29 | 0.0730 | 0.0968 | 0.2341 | 0.1491 | 0.2609 | 0.0657 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p01_ph0p47_ld0p38_ls0p65` | 5-29 | 0.1047 | 0.0854 | 0.3227 | 0.1460 | 0.3630 | 0.0682 | 81 | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p0025_ph0p54_ld0p22_ls0p65` | 5-29 | 0.0650 | 0.0797 | 0.2132 | 0.1503 | 0.2613 | 0.0598 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p0035_ph0p54_ld0p38_ls0p35` | 5-29 | 0.0655 | 0.0665 | 0.2131 | 0.1497 | 0.3572 | 0.0624 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p014_ph0p32_ld0p38_ls0p35` | 5-29 | 0.1085 | 0.0794 | 0.3206 | 0.1476 | 0.3574 | 0.0696 | 52 | 84.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0_ph0p32_ld0p3_ls1` | 5-29 | 0.0809 | 0.0934 | 0.2457 | 0.1496 | 0.3071 | 0.0658 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p0075_ph0p54_ld0p38_ls1` | 5-29 | 0.0742 | 0.0960 | 0.2339 | 0.1496 | 0.3135 | 0.0684 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p0075_ph0p32_ld0p22_ls1` | 5-29 | 0.0927 | 0.0921 | 0.2801 | 0.1492 | 0.3065 | 0.0709 | None | 84.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p3927_ld0p38_ls1` | 0-24 | 0.0774 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p3927_ld0p38_ls1` | 10-34 | 0.0589 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p3927_ld0p38_ls1` | 0-24 | 0.0693 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p3927_ld0p38_ls1` | 5-29 | 0.0646 | `high_lateral_velocity, single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p3927_ld0p38_ls1` | 10-34 | 0.0633 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p3927_ld0p38_ls1` | 15-39 | 0.0480 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p47_ld0p3_ls0p35` | 0-24 | 0.0835 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p47_ld0p3_ls0p35` | 10-34 | 0.0687 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p47_ld0p3_ls0p35` | 15-39 | 0.0534 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p47_ld0p3_ls0p35` | 10-34 | 0.0683 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p47_ld0p3_ls0p35` | 15-39 | 0.0659 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p47_ld0p3_ls0p35` | 0-24 | 0.0659 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p47_ld0p3_ls0p35` | 20-44 | 0.0619 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p47_ld0p3_ls0p35` | 5-29 | 0.0595 | `high_lateral_velocity, single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p47_ld0p3_ls0p35` | 25-49 | 0.0578 | `single_contact_pattern_dominates` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
