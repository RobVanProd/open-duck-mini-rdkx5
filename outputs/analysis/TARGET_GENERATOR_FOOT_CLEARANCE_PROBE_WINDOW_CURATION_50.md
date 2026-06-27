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

- mined_windows: `152`
- pass_curated_seed_windows: `23`
- review_motion_hints: `129`
- rejected_dataset_seeds: `0`
- curated_source_files: `1`
- curated_modes: `19`
- curated_source_mode_pairs: `19`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p22_ls0p65` | 5-54 | 0.0476 | 0.0686 | 0.3269 | 0.1466 | 0.4215 | 0.0657 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p00525_ph0p32_ld0p22_ls1` | 5-54 | 0.0486 | 0.0848 | 0.3408 | 0.1462 | 0.4215 | 0.0764 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 0-49 | 0.0475 | 0.1197 | 0.2851 | 0.1474 | 0.6924 | 0.0825 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 5-54 | 0.0428 | 0.0693 | 0.2898 | 0.1464 | 0.7136 | 0.0691 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p16_ls0p65` | 5-54 | 0.0531 | 0.0725 | 0.3411 | 0.1457 | 0.5111 | 0.0687 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0_ph0p3927_ld0p16_ls0p65` | 0-49 | 0.0463 | 0.1173 | 0.2836 | 0.1478 | 0.5720 | 0.0859 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0_ph0p3927_ld0p16_ls0p65` | 5-54 | 0.0418 | 0.0625 | 0.2845 | 0.1467 | 0.6758 | 0.0716 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0p00525_ph0p3927_ld0p16_ls1` | 5-54 | 0.0491 | 0.0859 | 0.3414 | 0.1460 | 0.4125 | 0.0792 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p00375_ph0p3927_ld0p3_ls0p65` | 5-54 | 0.0473 | 0.0656 | 0.2925 | 0.1474 | 0.5027 | 0.0639 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p3_ls0p65` | 5-54 | 0.0474 | 0.0600 | 0.2930 | 0.1475 | 0.5268 | 0.0623 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p16_ls0p65` | 5-54 | 0.0450 | 0.0593 | 0.2863 | 0.1472 | 0.5153 | 0.0679 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls0p65` | 5-54 | 0.0584 | 0.0794 | 0.3470 | 0.1454 | 0.5027 | 0.0693 | 54 | 92.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p00525_ph0p32_ld0p22_ls0p65` | 5-54 | 0.0508 | 0.0668 | 0.2997 | 0.1468 | 0.4758 | 0.0661 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p0105_ph0p32_ld0p22_ls0p65` | 5-54 | 0.0515 | 0.0709 | 0.3016 | 0.1468 | 0.4758 | 0.0639 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p0105_ph0p3927_ld0p22_ls0p65` | 5-54 | 0.0517 | 0.0660 | 0.3030 | 0.1469 | 0.4922 | 0.0625 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p0105_ph0p3927_ld0p22_ls0p65` | 0-49 | 0.0510 | 0.1190 | 0.2997 | 0.1469 | 0.5127 | 0.0791 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p06_a0p0075_ph0p47_ld0p3_ls0p65` | 5-54 | 0.0538 | 0.0632 | 0.3315 | 0.1462 | 0.3851 | 0.0613 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 5-54 | 0.0434 | 0.0824 | 0.3076 | 0.1466 | 0.2439 | 0.0698 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p3927_ld0p16_ls0p65` | 5-54 | 0.0540 | 0.0616 | 0.3326 | 0.1462 | 0.3917 | 0.0624 | None | 92.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 5-54 | 0.0505 | 0.0630 | 0.3044 | 0.1467 | 0.4323 | 0.0624 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 0-49 | 0.0468 | 0.1200 | 0.2827 | 0.1467 | 0.4999 | 0.0736 | None | 90.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p22_ls0p65` | 5-54 | 0.0423 | 0.0600 | 0.2624 | 0.1487 | 0.3430 | 0.0632 | None | 94.0000 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p0105_ph0p47_ld0p22_ls0p65` | 5-54 | 0.0544 | 0.0682 | 0.3359 | 0.1465 | 0.3430 | 0.0648 | None | 92.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65` | 0-49 | 0.0485 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65` | 10-59 | 0.0442 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65` | 5-54 | 0.0409 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65` | 15-64 | 0.0408 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 0-49 | 0.0404 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 0-49 | 0.0504 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 10-59 | 0.0460 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 5-54 | 0.0453 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p22_ls1` | 0-49 | 0.0401 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p22_ls1` | 0-49 | 0.0505 | `high_lateral_velocity` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p22_ls1` | 10-59 | 0.0456 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p22_ls1` | 5-54 | 0.0452 | `single_contact_pattern_dominates` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p16_ls1` | 0-49 | 0.0503 | `high_lateral_velocity` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p16_ls1` | 5-54 | 0.0477 | `single_contact_pattern_dominates` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p16_ls1` | 0-49 | 0.0546 | `high_lateral_velocity` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
