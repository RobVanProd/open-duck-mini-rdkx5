# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `64`
- mode_count: `32`
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
- `low_forward_velocity`: `32`
- `double_support_dominates`: `28`
- `too_little_single_support`: `22`
- `single_support_not_balanced`: `18`
- `single_contact_pattern_dominates`: `10`
- `high_lateral_velocity`: `6`

### seed_002
- `low_forward_velocity`: `31`
- `double_support_dominates`: `29`
- `too_little_single_support`: `27`
- `single_contact_pattern_dominates`: `20`
- `single_support_not_balanced`: `17`
- `high_lateral_velocity`: `1`
- `missing_seed_trace_or_window`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| primitive_p0p48_hrb0p04_hra0p06_hrph0_hb0p02_h0p025_kb0p04_k0p14_ab0_am0p00625_ph0_ld0p4_ls0p75_sp0_sasm0p5_vpgm1 | 0 | seed_002 | -0.3076 | -0.2996 | 0.0031 | 0.0058 | 0.0831 | 92.0000 | 12 | 0.0064 | `double_support_dominates, low_forward_velocity` |
| primitive_p0p64_hrb0p04_hra0p06_hrph0_hb0_h0p04_kb0p02_k0p1_ab0_a0_ph0p7854_ld0p24_ls1_sp0p02_sasm0p5_vpgm1 | 0 | seed_002 | -0.3746 | -0.3647 | 0.0006 | 0.0043 | 0.0624 | 93.3333 | 9 | 0.0059 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p56_hrb0p06_hra0p06_hrph0_hb0p02_h0p04_kb0p04_k0p14_ab0_a0_ph0_ld0p4_ls0p75_spm0p02_sas0_vpg0p5 | 0 | seed_000 | -0.3763 | -0.3611 | 0.0018 | 0.0053 | 0.1292 | 90.0000 | 17 | 0.0054 | `high_lateral_velocity, low_forward_velocity` |
| primitive_p0p64_hrb0p06_hra0p06_hrph0_hb0p02_h0p04_kb0p04_k0p1_ab0_am0p01_ph1p5708_ld0p32_ls1_spm0p02_sasm0p5_vpg1 | 0 | seed_002 | -0.3831 | -0.3603 | 0.0010 | 0.0034 | 0.0849 | 93.3333 | 9 | 0.0061 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p64_hrb0p06_hra0p06_hrph0_hb0p02_h0p04_kb0p02_k0p14_ab0_a0p01_ph0p7854_ld0p24_ls0p75_sp0p02_sas0p5_vpg1 | 0 | seed_002 | -0.3893 | -0.3667 | 0.0047 | 0.0056 | 0.0944 | 94.0000 | 9 | 0.0055 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p48_hrb0p06_hra0p06_hrph1p5708_hb0_h0p025_kb0p04_k0p14_ab0_a0_ph0_ld0p24_ls0p75_sp0p02_sasm0p5_vpgm1 | 0 | seed_000 | -0.4244 | -0.4221 | 0.0032 | 0.0037 | 0.0856 | 94.0000 | 7 | 0.0044 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| primitive_p0p64_hrb0p02_hra0p06_hrph0_hb0p02_h0p04_kb0p02_k0p1_ab0_a0p01_ph0p7854_ld0p32_ls0p75_sp0_sasm0p5_vpgm1 | 0 | seed_002 | -0.4420 | -0.4416 | 0.0028 | 0.0042 | 0.0603 | 94.6667 | 7 | 0.0045 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| primitive_p0p64_hrb0p06_hra0p04_hrph0_hb0p02_h0p04_kb0p02_k0p14_ab0_a0p01_ph0_ld0p4_ls1_sp0_sas0p5_vpg0p5 | 0 | seed_002 | -0.4452 | -0.4338 | 0.0020 | 0.0061 | 0.1114 | 95.3333 | 9 | 0.0063 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, too_little_single_support` |
| primitive_p0p56_hrb0p06_hra0p04_hrph1p5708_hb0p02_h0p04_kb0p02_k0p1_ab0_am0p01_ph0_ld0p4_ls0p75_spm0p02_sas0p5_vpg0p5 | 0 | seed_002 | -0.4703 | -0.4589 | 0.0006 | 0.0033 | 0.0887 | 95.3333 | 5 | 0.0049 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, too_little_single_support` |
| primitive_p0p48_hrb0p02_hra0p04_hrph0_hb0p02_h0p025_kb0p04_k0p1_ab0_a0_ph0p7854_ld0p24_ls0p75_sp0_sas0p5_vpg0p5 | 0 | seed_002 | -0.4908 | -0.4642 | 0.0032 | 0.0055 | 0.0598 | 96.0000 | 7 | 0.0039 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, too_little_single_support` |
| primitive_p0p56_hrb0p02_hra0p06_hrphm1p5708_hb0_h0p04_kb0p04_k0p1_ab0_am0p01_ph1p5708_ld0p32_ls1_sp0_sas0p5_vpg0p5 | 0 | seed_002 | -0.4945 | -0.4248 | 0.0026 | 0.0051 | 0.0555 | 96.0000 | 5 | 0.0035 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, too_little_single_support` |
| primitive_p0p56_hrb0p02_hra0p04_hrph1p5708_hb0p02_h0p025_kb0p02_k0p14_ab0_a0_ph0p7854_ld0p4_ls0p75_sp0p02_sasm0p5_vpgm1 | 0 | seed_002 | -0.5055 | -0.4780 | 0.0033 | 0.0038 | 0.0614 | 96.0000 | 7 | 0.0051 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, too_little_single_support` |
| primitive_p0p48_hrb0p02_hra0p06_hrph0_hb0_h0p025_kb0p04_k0p14_ab0_a0p00625_ph0_ld0p4_ls1_spm0p02_sasm0p5_vpg1 | 0 | seed_000 | -0.5160 | -0.3965 | 0.0006 | 0.0048 | 0.1177 | 88.0000 | 24 | 0.0048 | `low_forward_velocity` |
| primitive_p0p64_hrb0p06_hra0p04_hrph0_hb0_h0p04_kb0p02_k0p14_ab0_a0_ph0_ld0p24_ls0p75_spm0p02_sasm0p5_vpg1 | 0 | seed_002 | -0.5170 | -0.4972 | 0.0040 | 0.0085 | 0.0972 | 96.6667 | 5 | 0.0044 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p48_hrb0p02_hra0p06_hrph1p5708_hb0p02_h0p04_kb0p04_k0p1_ab0_a0p01_ph1p5708_ld0p24_ls1_sp0p02_sas0p5_vpgm1 | 0 | seed_002 | -0.5304 | -0.4941 | 0.0025 | 0.0025 | 0.0603 | 96.0000 | 5 | 0.0050 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p56_hrb0p02_hra0p06_hrphm1p5708_hb0p02_h0p04_kb0p02_k0p1_ab0_a0p01_ph0p7854_ld0p32_ls0p75_sp0p02_sasm0p5_vpg0p5 | 0 | seed_000 | -0.5359 | -0.4811 | 0.0005 | 0.0060 | 0.0722 | 94.6667 | 8 | 0.0059 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| primitive_p0p56_hrb0p02_hra0p04_hrphm1p5708_hb0p02_h0p025_kb0p02_k0p14_ab0_a0p00625_ph0p7854_ld0p24_ls1_sp0_sas0p5_vpgm1 | 0 | seed_000 | -0.5362 | -0.4916 | -0.0012 | 0.0022 | 0.0728 | 94.6667 | 7 | 0.0046 | `double_support_dominates, low_forward_velocity, too_little_single_support` |
| primitive_p0p48_hrb0p06_hra0p04_hrph0_hb0p02_h0p04_kb0p02_k0p14_ab0_a0p01_ph0_ld0p24_ls1_spm0p02_sasm0p5_vpgm1 | 0 | seed_002 | -0.5414 | -0.4627 | 0.0024 | 0.0058 | 0.0554 | 96.6667 | 5 | 0.0045 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p56_hrb0p02_hra0p04_hrph0_hb0p02_h0p025_kb0p04_k0p1_ab0_a0p00625_ph1p5708_ld0p32_ls0p75_vpg0p5 | 0 | seed_002 | -0.5434 | -0.5045 | 0.0031 | 0.0055 | 0.0874 | 96.6667 | 5 | 0.0049 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p56_hrb0p02_hra0p04_hrph0_hb0_h0p025_kb0p02_k0p1_ab0_a0p00625_ph0_ld0p24_ls1_spm0p02_sasm0p5_vpgm1 | 0 | seed_002 | -0.5490 | -0.4468 | 0.0032 | 0.0049 | 0.0412 | 96.6667 | 5 | 0.0045 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p64_hrb0p02_hra0p04_hrphm1p5708_hb0p02_h0p025_kb0p02_k0p14_ab0_am0p00625_ph1p5708_ld0p4_ls1_sp0_sasm0p5_vpgm1 | 0 | seed_002 | -0.5515 | -0.4380 | 0.0040 | 0.0046 | 0.0535 | 96.6667 | 5 | 0.0045 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p56_hrb0p04_hra0p04_hrph1p5708_hb0_h0p025_kb0p02_k0p14_ab0_a0p00625_ph1p5708_ld0p4_ls0p75_vpg1 | 0 | seed_000 | -0.5539 | -0.5526 | 0.0029 | 0.0047 | 0.0740 | 96.6667 | 3 | 0.0050 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p56_hrb0p04_hra0p04_hrph0_hb0_h0p04_kb0p04_k0p14_ab0_a0_ph0p7854_ld0p24_ls0p75_spm0p02_sas0_vpgm1 | 0 | seed_000 | -0.5670 | -0.5574 | 0.0029 | 0.0051 | 0.0631 | 96.6667 | 3 | 0.0042 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p48_hrb0p02_hra0p04_hrphm1p5708_hb0p02_h0p025_kb0p04_k0p14_ab0_a0_ph1p5708_ld0p4_ls1_sp0p02_sas0p5_vpg0p5 | 0 | seed_002 | -0.5733 | -0.4866 | 0.0044 | 0.0067 | 0.1080 | 97.3333 | 3 | 0.0050 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, single_support_not_balanced, too_little_single_support` |
| primitive_p0p48_hrb0p06_hra0p04_hrph1p5708_hb0_h0p04_kb0p02_k0p1_ab0_a0_ph0p7854_ld0p32_ls0p75_sp0p02_sas0p5_vpgm1 | 0 | seed_000 | -0.5743 | -0.5452 | 0.0006 | 0.0027 | 0.0616 | 96.0000 | 5 | 0.0043 | `double_support_dominates, low_forward_velocity, single_contact_pattern_dominates, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
