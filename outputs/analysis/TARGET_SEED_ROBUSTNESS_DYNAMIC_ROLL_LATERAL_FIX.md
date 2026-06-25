# Target Seed Robustness Audit

status: `PASS_SEED_ROBUST_TARGETS`

This audits compact target-window curation outputs for modes that pass
across multiple source seeds. It does not run simulation or training.

## Inputs

| input | source_status | status | modes | robust_modes | seed0_curated_seed2_review |
|---|---|---|---:|---:|---:|
| target_generator_dynamic_roll_lateral_fix_window_curation_50.json | `PASS_CURATED_DATASET_SEED_READY` | `PASS_SEED_ROBUST_TARGETS` | 160 | 3 | 56 |

## Seed 2 Reason Counts

- `high_lateral_velocity`: `162`
- `single_contact_pattern_dominates`: `155`

## Top Seed 2 Near Misses

| input | mode | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact_max | seed2_reasons |
|---|---|---:|---:|---:|---:|---|
| target_generator_dynamic_roll_lateral_fix_window_curation_50.json | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p3927_ld0p36_ls0p55` | 0.0480 | 0.0603 | 0.1652 | 88.0000 | `high_lateral_velocity` |
| target_generator_dynamic_roll_lateral_fix_window_curation_50.json | `primitive_p0p54_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0063_ph0p37_ld0p3_ls0p65` | 0.0469 | 0.0564 | 0.1914 | 94.0000 | `high_lateral_velocity` |
| target_generator_dynamic_roll_lateral_fix_window_curation_50.json | `primitive_p0p58_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p42_ld0p3_ls0p55` | 0.0436 | 0.0563 | 0.1838 | 90.0000 | `high_lateral_velocity` |
| target_generator_dynamic_roll_lateral_fix_window_curation_50.json | `primitive_p0p54_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p36_ls0p75` | 0.0407 | 0.0549 | 0.1804 | 92.0000 | `high_lateral_velocity` |
| target_generator_dynamic_roll_lateral_fix_window_curation_50.json | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p34_ld0p24_ls0p55` | 0.0430 | 0.0549 | 0.1796 | 92.0000 | `high_lateral_velocity` |
| target_generator_dynamic_roll_lateral_fix_window_curation_50.json | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p37_ld0p36_ls0p55` | 0.0462 | 0.0546 | 0.1677 | 90.0000 | `high_lateral_velocity` |
| target_generator_dynamic_roll_lateral_fix_window_curation_50.json | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 0.0413 | 0.0542 | 0.1793 | 94.0000 | `high_lateral_velocity` |
| target_generator_dynamic_roll_lateral_fix_window_curation_50.json | `primitive_p0p54_hrb0_hra0p032_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p47_ld0p24_ls0p55` | 0.0406 | 0.0540 | 0.1680 | 94.0000 | `high_lateral_velocity` |
| target_generator_dynamic_roll_lateral_fix_window_curation_50.json | `primitive_p0p54_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p34_ld0p3_ls0p55` | 0.0429 | 0.0539 | 0.1790 | 94.0000 | `high_lateral_velocity` |
| target_generator_dynamic_roll_lateral_fix_window_curation_50.json | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p42_ld0p24_ls0p55` | 0.0424 | 0.0537 | 0.1777 | 90.0000 | `high_lateral_velocity` |

## Interpretation

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode curated on multiple seeds.
- Current holds mean the primitive family can generate motion, but not robustly across reset seeds.
- Do not train from single-source curated windows as if they were a general target dataset.
