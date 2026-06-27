# Target Seed Robustness Audit

status: `HOLD_SEED2_LATERAL_CONTACT`

This audits compact target-window curation outputs for modes that pass
across multiple source seeds. It does not run simulation or training.

## Inputs

| input | source_status | status | modes | robust_modes | seed0_curated_seed2_review |
|---|---|---|---:|---:|---:|
| target_generator_dynamic_roll_window_curation_50.json | `PASS_CURATED_DATASET_SEED_READY` | `HOLD_SEED2_LATERAL_CONTACT` | 69 | 0 | 35 |

## Seed 2 Reason Counts

- `single_contact_pattern_dominates`: `125`
- `high_lateral_velocity`: `72`

## Top Seed 2 Near Misses

| input | mode | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact_max | seed2_reasons |
|---|---|---:|---:|---:|---:|---|
| target_generator_dynamic_roll_window_curation_50.json | `primitive_p0p52_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 0.0436 | 0.0543 | 0.1918 | 92.0000 | `high_lateral_velocity` |
| target_generator_dynamic_roll_window_curation_50.json | `primitive_p0p52_hrb0_hra0p04_hrph1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p32_ld0p22_ls0p65` | 0.0413 | 0.0532 | 0.1811 | 94.0000 | `high_lateral_velocity` |
| target_generator_dynamic_roll_window_curation_50.json | `primitive_p0p52_hrb0_hra0p03_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 0.0416 | 0.0527 | 0.2088 | 86.0000 | `high_lateral_velocity` |
| target_generator_dynamic_roll_window_curation_50.json | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 0.0497 | 0.0517 | 0.1889 | 94.0000 | `high_lateral_velocity` |
| target_generator_dynamic_roll_window_curation_50.json | `primitive_p0p58_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 0.0444 | 0.0516 | 0.1911 | 94.0000 | `high_lateral_velocity` |
| target_generator_dynamic_roll_window_curation_50.json | `primitive_p0p58_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls1` | 0.0479 | 0.0515 | 0.1799 | 92.0000 | `high_lateral_velocity` |
| target_generator_dynamic_roll_window_curation_50.json | `primitive_p0p52_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 0.0448 | 0.0511 | 0.1799 | 92.0000 | `high_lateral_velocity` |
| target_generator_dynamic_roll_window_curation_50.json | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 0.0447 | 0.0504 | 0.1669 | 94.0000 | `high_lateral_velocity` |
| target_generator_dynamic_roll_window_curation_50.json | `primitive_p0p58_hrb0_hra0p02_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 0.0405 | 0.0501 | 0.1739 | 92.0000 | `high_lateral_velocity` |
| target_generator_dynamic_roll_window_curation_50.json | `primitive_p0p58_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p22_ls1` | 0.0416 | 0.0501 | 0.1851 | 94.0000 | `high_lateral_velocity` |

## Interpretation

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode curated on multiple seeds.
- Current holds mean the primitive family can generate motion, but not robustly across reset seeds.
- Do not train from single-source curated windows as if they were a general target dataset.
