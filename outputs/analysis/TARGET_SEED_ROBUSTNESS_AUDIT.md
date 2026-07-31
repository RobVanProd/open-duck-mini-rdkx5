# Target Seed Robustness Audit

status: `HOLD_SEED2_LATERAL_CONTACT`

This audits compact target-window curation outputs for modes that pass
across multiple source seeds. It does not run simulation or training.

## Inputs

| input | source_status | status | modes | robust_modes | seed0_curated_seed2_review |
|---|---|---|---:|---:|---:|
| target_generator_lateral_contact_window_curation_50.json | `HOLD_INSUFFICIENT_CURATED_DIVERSITY` | `HOLD_SEED2_LATERAL_CONTACT` | 19 | 0 | 3 |
| target_generator_seed2_balance_window_curation_50.json | `HOLD_INSUFFICIENT_CURATED_DIVERSITY` | `HOLD_SEED2_LATERAL_CONTACT` | 33 | 0 | 9 |

## Seed 2 Reason Counts

- `single_contact_pattern_dominates`: `64`
- `high_lateral_velocity`: `40`

## Top Seed 2 Near Misses

| input | mode | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact_max | seed2_reasons |
|---|---|---:|---:|---:|---:|---|
| target_generator_lateral_contact_window_curation_50.json | `primitive_p0p55_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p7854` | 0.0541 | 0.0549 | 0.1611 | 94.0000 | `high_lateral_velocity` |
| target_generator_lateral_contact_window_curation_50.json | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p3927` | 0.0428 | 0.0483 | 0.1657 | 92.0000 | `high_lateral_velocity` |
| target_generator_lateral_contact_window_curation_50.json | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p3927` | 0.0441 | 0.0431 | 0.0315 | 100.0000 | `single_contact_pattern_dominates` |
| target_generator_seed2_balance_window_curation_50.json | `primitive_p0p5_hrb0_hb0p06_h0p05_kb0p03_k0p1_ab0p08_a0_ph0p3927` | 0.0432 | 0.0592 | 0.1689 | 92.0000 | `high_lateral_velocity` |
| target_generator_seed2_balance_window_curation_50.json | `primitive_p0p55_hrb0p01_hb0p06_h0p05_kb0p03_k0p08_ab0p08_a0p015_ph0p3927` | 0.0435 | 0.0565 | 0.1820 | 94.0000 | `high_lateral_velocity` |
| target_generator_seed2_balance_window_curation_50.json | `primitive_p0p5_hrb0_hb0p06_h0p04_kb0p03_k0p1_ab0p08_a0_ph0p7854` | 0.0409 | 0.0545 | 0.1826 | 94.0000 | `high_lateral_velocity` |
| target_generator_seed2_balance_window_curation_50.json | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927` | 0.0565 | 0.0537 | 0.1630 | 92.0000 | `high_lateral_velocity` |
| target_generator_seed2_balance_window_curation_50.json | `primitive_p0p7_hrbm0p01_hb0p08_h0p05_kb0p06_k0p12_ab0p04_a0_ph0p589` | 0.0543 | 0.0509 | 0.0380 | 100.0000 | `single_contact_pattern_dominates` |
| target_generator_seed2_balance_window_curation_50.json | `primitive_p0p55_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963` | 0.0494 | 0.0467 | 0.1710 | 94.0000 | `high_lateral_velocity` |
| target_generator_seed2_balance_window_curation_50.json | `primitive_p0p7_hrb0p01_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p1963` | 0.0503 | 0.0464 | 0.0403 | 100.0000 | `single_contact_pattern_dominates` |
| target_generator_seed2_balance_window_curation_50.json | `primitive_p0p7_hrb0_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p1963` | 0.0537 | 0.0444 | 0.0419 | 100.0000 | `single_contact_pattern_dominates` |
| target_generator_seed2_balance_window_curation_50.json | `primitive_p0p5_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963` | 0.0458 | 0.0442 | 0.1703 | 94.0000 | `high_lateral_velocity` |

## Interpretation

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode curated on multiple seeds.
- Current holds mean the primitive family can generate motion, but not robustly across reset seeds.
- Do not train from single-source curated windows as if they were a general target dataset.
