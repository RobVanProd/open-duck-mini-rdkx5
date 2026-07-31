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

- mined_windows: `391`
- pass_curated_seed_windows: `42`
- review_motion_hints: `349`
- rejected_dataset_seeds: `0`
- curated_source_files: `1`
- curated_modes: `42`
- curated_source_mode_pairs: `42`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65` | 5-29 | 0.0651 | 0.0755 | 0.2267 | 0.1491 | 0.3739 | 0.0607 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 5-29 | 0.0764 | 0.0942 | 0.2634 | 0.1479 | 0.3012 | 0.0721 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p22_ls1` | 5-29 | 0.0755 | 0.0941 | 0.2625 | 0.1480 | 0.2986 | 0.0750 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p16_ls1` | 5-29 | 0.0901 | 0.0979 | 0.2989 | 0.1471 | 0.2954 | 0.0735 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p3927_ld0p16_ls1` | 5-29 | 0.0674 | 0.0959 | 0.2300 | 0.1498 | 0.4125 | 0.0712 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p0105_ph0p47_ld0p16_ls1` | 5-29 | 0.0670 | 0.0979 | 0.2345 | 0.1497 | 0.4181 | 0.0748 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p0105_ph0p47_ld0p3_ls1` | 5-29 | 0.0770 | 0.0907 | 0.2649 | 0.1478 | 0.4194 | 0.0752 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p22_ls0p65` | 5-29 | 0.0869 | 0.0834 | 0.2890 | 0.1474 | 0.4215 | 0.0580 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p00525_ph0p32_ld0p22_ls1` | 5-29 | 0.0934 | 0.0972 | 0.3075 | 0.1470 | 0.4215 | 0.0708 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 5-29 | 0.0700 | 0.0720 | 0.2412 | 0.1485 | 0.7136 | 0.0598 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00525_ph0p47_ld0p16_ls0p65` | 5-29 | 0.0643 | 0.0775 | 0.2307 | 0.1489 | 0.5111 | 0.0603 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p0105_ph0p3927_ld0p16_ls0p65` | 5-29 | 0.0658 | 0.0736 | 0.2265 | 0.1490 | 0.5529 | 0.0605 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls0p65` | 5-29 | 0.0876 | 0.0826 | 0.2945 | 0.1466 | 0.6601 | 0.0636 | 61 | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p16_ls0p65` | 5-29 | 0.0898 | 0.0774 | 0.3029 | 0.1468 | 0.5111 | 0.0600 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0_ph0p3927_ld0p16_ls0p65` | 5-29 | 0.0646 | 0.0702 | 0.2226 | 0.1492 | 0.6758 | 0.0591 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0_ph0p47_ld0p3_ls0p65` | 5-29 | 0.0884 | 0.0876 | 0.2987 | 0.1463 | 0.8721 | 0.0627 | 52 | 84.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0p00525_ph0p3927_ld0p16_ls1` | 5-29 | 0.0934 | 0.0953 | 0.3100 | 0.1470 | 0.4125 | 0.0755 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0p0105_ph0p47_ld0p3_ls0p65` | 5-29 | 0.0920 | 0.0864 | 0.3100 | 0.1456 | 0.8721 | 0.0589 | 51 | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p00375_ph0p3927_ld0p3_ls0p65` | 5-29 | 0.0717 | 0.0771 | 0.2361 | 0.1488 | 0.5534 | 0.0562 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p3_ls0p65` | 5-29 | 0.0688 | 0.0752 | 0.2276 | 0.1489 | 0.6147 | 0.0559 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p3_ls0p65` | 5-29 | 0.0920 | 0.0833 | 0.2977 | 0.1468 | 0.6147 | 0.0626 | 72 | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p16_ls0p65` | 5-29 | 0.0659 | 0.0764 | 0.2209 | 0.1491 | 0.5776 | 0.0596 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p22_ls0p65` | 5-29 | 0.0685 | 0.0756 | 0.2210 | 0.1495 | 0.3861 | 0.0583 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p22_ls1` | 5-29 | 0.1014 | 0.0953 | 0.3034 | 0.1477 | 0.3715 | 0.0703 | 52 | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls0p65` | 5-29 | 0.0962 | 0.0840 | 0.3046 | 0.1465 | 0.5534 | 0.0626 | 79 | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0p00525_ph0p47_ld0p16_ls1` | 5-29 | 0.0902 | 0.0940 | 0.2778 | 0.1480 | 0.3723 | 0.0690 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0p0105_ph0p3927_ld0p3_ls0p65` | 5-29 | 0.1017 | 0.0864 | 0.3160 | 0.1467 | 0.5534 | 0.0630 | 54 | 84.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p00525_ph0p32_ld0p22_ls0p65` | 5-29 | 0.0750 | 0.0729 | 0.2373 | 0.1487 | 0.4724 | 0.0558 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p0105_ph0p32_ld0p22_ls0p65` | 5-29 | 0.0736 | 0.0762 | 0.2333 | 0.1487 | 0.4724 | 0.0552 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p0105_ph0p3927_ld0p22_ls0p65` | 5-29 | 0.0700 | 0.0716 | 0.2243 | 0.1489 | 0.5256 | 0.0560 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 5-29 | 0.0769 | 0.0904 | 0.2313 | 0.1504 | 0.2345 | 0.0659 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p06_a0p0075_ph0p47_ld0p3_ls0p65` | 5-29 | 0.0922 | 0.0848 | 0.2861 | 0.1477 | 0.2930 | 0.0601 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 5-29 | 0.0874 | 0.0932 | 0.2572 | 0.1500 | 0.2439 | 0.0663 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p16_ls1` | 5-29 | 0.0701 | 0.1000 | 0.2148 | 0.1507 | 0.2283 | 0.0655 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p00375_ph0p47_ld0p16_ls1` | 5-29 | 0.0935 | 0.0976 | 0.2797 | 0.1497 | 0.2283 | 0.0675 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p32_ld0p16_ls1` | 5-29 | 0.0939 | 0.0960 | 0.2810 | 0.1498 | 0.2287 | 0.0677 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p3927_ld0p16_ls0p65` | 5-29 | 0.0927 | 0.0855 | 0.2866 | 0.1478 | 0.3163 | 0.0619 | None | 84.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p16_ls1` | 5-29 | 0.0710 | 0.1011 | 0.2185 | 0.1504 | 0.2283 | 0.0678 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 5-29 | 0.0719 | 0.0702 | 0.2299 | 0.1491 | 0.4061 | 0.0584 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0p0075_ph0p32_ld0p16_ls0p65` | 5-29 | 0.0981 | 0.0777 | 0.2983 | 0.1477 | 0.3065 | 0.0613 | 58 | 84.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p22_ls0p65` | 5-29 | 0.0721 | 0.0755 | 0.2191 | 0.1504 | 0.3357 | 0.0582 | None | 88.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p0105_ph0p47_ld0p22_ls0p65` | 5-29 | 0.0932 | 0.0834 | 0.2794 | 0.1486 | 0.3357 | 0.0640 | None | 84.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65` | 0-24 | 0.0638 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65` | 10-34 | 0.0518 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65` | 15-39 | 0.0426 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65` | 15-39 | 0.0675 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65` | 20-44 | 0.0672 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65` | 10-34 | 0.0618 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65` | 25-49 | 0.0575 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65` | 30-54 | 0.0423 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 0-24 | 0.0715 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 10-34 | 0.0564 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 15-39 | 0.0437 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 20-44 | 0.0605 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 10-34 | 0.0585 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 25-49 | 0.0576 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 15-39 | 0.0570 | `single_contact_pattern_dominates` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
