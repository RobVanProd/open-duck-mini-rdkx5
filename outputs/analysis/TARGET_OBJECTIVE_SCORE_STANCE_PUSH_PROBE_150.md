# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `96`
- mode_count: `48`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `150`

## Criteria

- min_mean_vx: `0.04`
- max_vy_abs_p95: `0.12`
- max_contact_dominance_pct: `95.0`
- max_double_support_pct: `90.0`
- max_no_support_pct: `100.0`
- min_single_support_pct: `8.0`
- min_each_single_support_pct: `2.0`
- max_pitch_abs_p95: `0.35`
- min_base_height: `0.145`
- max_sent_velocity_p95: `2.5`
- max_tracking_p95: `0.12`
- min_done_margin: `50`
- min_contact_transitions: `3`
- min_foot_site_z_p95: `-1.0`

## Seed Failure Counts

### seed_000
- `low_forward_velocity`: `48`
- `double_support_dominates`: `46`
- `too_little_single_support`: `39`
- `single_support_not_balanced`: `33`
- `single_contact_pattern_dominates`: `17`
- `high_lateral_velocity`: `6`
- `too_few_contact_transitions`: `1`

### seed_002
- `double_support_dominates`: `48`
- `low_forward_velocity`: `48`
- `too_little_single_support`: `41`
- `single_contact_pattern_dominates`: `24`
- `single_support_not_balanced`: `17`
- `high_lateral_velocity`: `1`
- `too_few_contact_transitions`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p64_hrb0p02_hra0p06_hrph0_hb0p02_h0p04_kb0p04_k0p14_ab0_a0_ph0_ld0p4_ls1_sp0p02_sasm0p5 | 0 | seed_000 | -0.2948 | -0.2934 | 0.0028 | 0.0061 | 0.0890 | 91.3333 | 13 | 0.0063 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p64_hrb0p04_hra0p06_hrph0_hb0_h0p025_kb0p02_k0p14_ab0_am0p00625_ph0p7854_ld0p24_ls1_sp0p04_sasm0p5 | 0 | seed_000 | -0.3386 | -0.3354 | -0.0007 | 0.0016 | 0.0933 | 91.3333 | 8 | 0.0058 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p56_hrb0p06_hra0p06_hrphm1p5708_hb0p02_h0p025_kb0p02_k0p14_ab0_a0_ph1p5708_ld0p24_ls1_spm0p04_sasm0p5 | 0 | seed_000 | -0.3443 | -0.3415 | 0.0035 | 0.0053 | 0.1045 | 92.6667 | 9 | 0.0039 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p56_hrb0p06_hra0p06_hrph0_hb0_h0p025_kb0p04_k0p14_ab0_a0_ph0p7854_ld0p32_ls0p75_sp0p04_sas0p5 | 0 | seed_002 | -0.3766 | -0.3418 | 0.0059 | 0.0070 | 0.0677 | 94.0000 | 13 | 0.0051 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p56_hrb0p06_hra0p04_hrph1p5708_hb0p02_h0p025_kb0p04_k0p14_ab0_a0p00625_ph0_ld0p24_ls1_spm0p04_sas0p5 | 0 | seed_002 | -0.3899 | -0.3849 | 0.0003 | 0.0026 | 0.0768 | 93.3333 | 7 | 0.0046 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p64_hrb0p06_hra0p06_hrph0_hb0p02_h0p04_kb0p02_k0p14_ab0_a0p01_ph0p7854_ld0p32_ls0p75_sp0p02_sas0 | 0 | seed_002 | -0.4041 | -0.3961 | 0.0028 | 0.0040 | 0.0672 | 94.0000 | 13 | 0.0051 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p64_hrb0p04_hra0p06_hrph1p5708_hb0p02_h0p025_kb0p04_k0p14_ab0_a0p00625_ph0p7854_ld0p32_ls1_sp0p02_sas0 | 0 | seed_002 | -0.4321 | -0.3670 | 0.0035 | 0.0038 | 0.1216 | 94.0000 | 5 | 0.0061 | `double_support_dominates, high_lateral_velocity, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| primitive_p0p64_hrb0p02_hra0p06_hrph1p5708_hb0p02_h0p04_kb0p02_k0p14_ab0_am0p01_ph0_ld0p4_ls0p75_spm0p02_sas0p5 | 0 | seed_000 | -0.4373 | -0.3724 | 0.0024 | 0.0058 | 0.1135 | 92.0000 | 9 | 0.0047 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p56_hrb0p04_hra0p06_hrph0_hb0p02_h0p04_kb0p02_k0p1_ab0_a0p01_ph0_ld0p24_ls1_sp0p02_sas0 | 0 | seed_002 | -0.4399 | -0.3884 | 0.0011 | 0.0030 | 0.0644 | 94.6667 | 11 | 0.0048 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p64_hrb0p06_hra0p06_hrph1p5708_hb0_h0p025_kb0p02_k0p14_ab0_am0p00625_ph0_ld0p4_ls0p75_spm0p04_sas0 | 0 | seed_000 | -0.4405 | -0.3824 | 0.0029 | 0.0040 | 0.1070 | 92.0000 | 11 | 0.0044 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p64_hrb0p02_hra0p06_hrph1p5708_hb0_h0p025_kb0p04_k0p14_ab0_a0p00625_ph1p5708_ld0p24_ls1_spm0p04_sas0p5 | 0 | seed_002 | -0.4426 | -0.4349 | -0.0001 | 0.0027 | 0.0917 | 94.6667 | 7 | 0.0045 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p56_hrb0p06_hra0p06_hrphm1p5708_hb0p02_h0p025_kb0p04_k0p1_ab0_a0_ph0p7854_ld0p24_ls1_spm0p02_sasm0p5 | 0 | seed_000 | -0.4508 | -0.4099 | 0.0020 | 0.0049 | 0.0685 | 93.3333 | 11 | 0.0039 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p48_hrb0p04_hra0p06_hrph1p5708_hb0_h0p04_kb0p02_k0p14_ab0_a0_ph0p7854_ld0p24_ls0p75_spm0p02_sas0 | 0 | seed_000 | -0.4516 | -0.4349 | 0.0002 | 0.0024 | 0.0945 | 94.0000 | 7 | 0.0037 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p72_hrb0p06_hra0p06_hrphm1p5708_hb0_h0p025_kb0p02_k0p14_ab0_a0_ph0_ld0p24_ls0p75_sp0p04_sasm0p5 | 0 | seed_002 | -0.4605 | -0.4589 | -0.0005 | 0.0007 | 0.0484 | 94.6667 | 9 | 0.0047 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p72_hrb0p06_hra0p06_hrph1p5708_hb0p02_h0p04_kb0p04_k0p14_ab0_a0p01_ph1p5708_ld0p4_ls0p75_sp0p02_sas0 | 0 | seed_000 | -0.4629 | -0.4616 | 0.0049 | 0.0059 | 0.0765 | 95.3333 | 9 | 0.0076 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p56_hrb0p02_hra0p06_hrphm1p5708_hb0_h0p04_kb0p04_k0p1_ab0_a0p01_ph1p5708_ld0p32_ls1_sp0p04_sas0 | 0 | seed_002 | -0.4632 | -0.4016 | 0.0035 | 0.0056 | 0.0610 | 95.3333 | 7 | 0.0045 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p72_hrb0p04_hra0p06_hrph1p5708_hb0_h0p04_kb0p04_k0p14_ab0_a0p01_ph1p5708_ld0p32_ls1_spm0p04_sas0 | 0 | seed_000 | -0.4638 | -0.4331 | 0.0018 | 0.0042 | 0.1013 | 94.0000 | 7 | 0.0051 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p48_hrb0p04_hra0p06_hrph0_hb0_h0p025_kb0p04_k0p14_ab0_am0p00625_ph1p5708_ld0p32_ls0p75_sp0p02_sasm0p5 | 0 | seed_000 | -0.4654 | -0.4497 | 0.0031 | 0.0036 | 0.0739 | 94.6667 | 9 | 0.0046 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p48_hrb0p02_hra0p06_hrphm1p5708_hb0_h0p025_kb0p04_k0p1_ab0_a0p00625_ph0_ld0p24_ls1_sp0p02_sas0 | 0 | seed_000 | -0.4654 | -0.3989 | 0.0001 | 0.0031 | 0.0553 | 92.0000 | 12 | 0.0041 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p72_hrb0p02_hra0p06_hrphm1p5708_hb0_h0p025_kb0p02_k0p1_ab0_a0p00625_ph1p5708_ld0p4_ls0p75_sp0p04_sas0 | 0 | seed_000 | -0.4658 | -0.4649 | 0.0016 | 0.0040 | 0.0458 | 95.3333 | 9 | 0.0045 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, too_little_single_support` |
| primitive_p0p72_hrb0p02_hra0p06_hrphm1p5708_hb0_h0p04_kb0p04_k0p1_ab0_am0p01_ph0p7854_ld0p32_ls1_sp0p04_sasm0p5 | 0 | seed_000 | -0.4799 | -0.4459 | 0.0000 | 0.0031 | 0.0729 | 94.0000 | 6 | 0.0055 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p72_hrb0p06_hra0p06_hrph1p5708_hb0_h0p04_kb0p04_k0p1_ab0_a0p01_ph0_ld0p4_ls0p75_spm0p04_sasm0p5 | 0 | seed_002 | -0.4833 | -0.4654 | 0.0021 | 0.0048 | 0.0649 | 95.3333 | 9 | 0.0039 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p48_hrb0p02_hra0p06_hrph0_hb0p02_h0p04_kb0p02_k0p1_ab0_a0_ph0_ld0p32_ls0p75_sp0p04_sas0 | 0 | seed_002 | -0.4879 | -0.4486 | 0.0004 | 0.0028 | 0.0743 | 95.3333 | 5 | 0.0051 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p72_hrb0p02_hra0p06_hrphm1p5708_hb0_h0p025_kb0p02_k0p1_ab0_am0p00625_ph0p7854_ld0p4_ls1_spm0p02_sas0p5 | 0 | seed_000 | -0.4911 | -0.4425 | -0.0014 | 0.0022 | 0.0551 | 93.3333 | 6 | 0.0042 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p48_hrb0p04_hra0p04_hrphm1p5708_hb0p02_h0p025_kb0p04_k0p1_ab0_a0_ph0p7854_ld0p32_ls1_sp0p02_sas0 | 0 | seed_002 | -0.5015 | -0.4478 | 0.0021 | 0.0043 | 0.0587 | 96.0000 | 7 | 0.0043 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
