# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `48`
- mode_count: `24`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `100`

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
- `low_forward_velocity`: `24`
- `high_lateral_velocity`: `22`
- `action_saturation`: `2`
- `double_support_dominates`: `2`
- `too_little_single_support`: `2`
- `single_contact_pattern_dominates`: `1`
- `single_support_not_balanced`: `1`
- `too_few_contact_transitions`: `1`

### seed_002
- `low_forward_velocity`: `24`
- `high_lateral_velocity`: `23`
- `double_support_dominates`: `3`
- `action_saturation`: `2`
- `too_little_single_support`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| teacher_p0p64_rs0p04_sk0p08_sam0p02_spg0p5_pd1_lg0_clb0p5 | 0 | seed_000 | -0.4492 | -0.3822 | -0.0012 | 0.0050 | 0.1164 | 92.0000 | 10 | 0.0053 | `double_support_dominates, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p08_sa0_spg0p5_pd2_lg0p5_clb0p5 | 0 | seed_002 | -0.4543 | -0.4463 | -0.0003 | 0.0050 | 0.1424 | 88.0000 | 22 | 0.0056 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p08_sa0p02_spg1p5_pd0_lg0_clb0p5 | 0 | seed_000 | -0.4920 | -0.4708 | 0.0033 | 0.0107 | 0.1483 | 90.0000 | 18 | 0.0066 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p08_sa0p02_spg0p5_pd1_lg0_clb0p5 | 0 | seed_000 | -0.5275 | -0.4787 | 0.0060 | 0.0080 | 0.1377 | 92.0000 | 11 | 0.0075 | `double_support_dominates, high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p06_sk0p08_sa0p02_spg1p5_pd2_lg0_clb0p5 | 0 | seed_000 | -0.5519 | -0.4954 | -0.0036 | 0.0069 | 0.1426 | 86.0000 | 20 | 0.0061 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p12_sa0_spg1_pd0_lg0_clb0 | 0 | seed_000 | -0.5772 | -0.5691 | 0.0089 | 0.0075 | 0.1586 | 84.0000 | 19 | 0.0064 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p08_sa0_spg1p5_pd2_lg0_clb0 | 0 | seed_000 | -0.6824 | -0.5964 | -0.0028 | 0.0065 | 0.1411 | 93.0000 | 5 | 0.0046 | `double_support_dominates, high_lateral_velocity, low_forward_velocity, too_little_single_support` |
| teacher_p0p64_rs0p02_sk0p12_sa0p02_spg1p5_pd0_lg1_clb0 | 0 | seed_002 | -0.8863 | -0.7172 | -0.0033 | 0.0033 | 0.1945 | 88.0000 | 12 | 0.0077 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p08_sa0p02_spg0p5_pd2_lg0p5_clb1 | 0 | seed_000 | -0.9438 | -0.8939 | 0.0016 | 0.0160 | 0.2035 | 80.0000 | 27 | 0.0100 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p08_sa0p02_spg1p5_pd2_lg0p5_clb1 | 0 | seed_000 | -0.9564 | -0.8890 | 0.0014 | 0.0148 | 0.1993 | 80.0000 | 23 | 0.0096 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p16_sa0p02_spg0p5_pd1_lg0_clb0 | 0 | seed_000 | -1.1012 | -1.0899 | 0.0203 | 0.0251 | 0.2431 | 79.0000 | 16 | 0.0120 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p04_sk0p08_sa0p02_spg1p5_pd2_lg0p5_clb1 | 0 | seed_002 | -1.3191 | -1.2764 | 0.0036 | 0.0007 | 0.2457 | 67.0000 | 30 | 0.0071 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p04_sk0p12_sa0_spg1_pd1_lg0p5_clb0p5 | 0 | seed_002 | -1.4671 | -1.4516 | 0.0099 | 0.0065 | 0.2707 | 69.0000 | 28 | 0.0073 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p06_sk0p12_sa0_spg0p5_pd1_lg0p5_clb0 | 0 | seed_002 | -1.5492 | -1.5389 | 0.0031 | 0.0026 | 0.2766 | 72.0000 | 23 | 0.0078 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p02_sk0p12_sa0_spg1p5_pd2_lg0p5_clb0p5 | 0 | seed_000 | -1.5651 | -1.4988 | 0.0139 | 0.0140 | 0.2748 | 64.0000 | 31 | 0.0093 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p02_sk0p16_sam0p02_spg0p5_pd1_lg0_clb1 | 0 | seed_000 | -1.6114 | -1.4485 | 0.0170 | 0.0176 | 0.1971 | 85.0000 | 12 | 0.0095 | `action_saturation, high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p06_sk0p16_sam0p02_spg1p5_pd1_lg0_clb0 | 0 | seed_002 | -1.8094 | -1.7839 | 0.0196 | 0.0168 | 0.3251 | 63.0000 | 23 | 0.0080 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p04_sk0p16_sa0_spg1p5_pd1_lg1_clb0 | 0 | seed_000 | -1.8912 | -1.8760 | 0.0158 | 0.0188 | 0.3338 | 67.0000 | 21 | 0.0083 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p06_sk0p12_sam0p02_spg1_pd2_lg1_clb0 | 0 | seed_000 | -1.9353 | -1.8781 | 0.0037 | 0.0045 | 0.3127 | 68.0000 | 27 | 0.0074 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p06_sk0p12_sa0p02_spg1_pd0_lg1_clb1 | 0 | seed_002 | -1.9735 | -1.9620 | 0.0208 | 0.0058 | 0.3332 | 66.0000 | 23 | 0.0123 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p06_sk0p16_sam0p02_spg1_pd1_lg0_clb0 | 0 | seed_002 | -1.9998 | -1.8375 | 0.0237 | 0.0213 | 0.3539 | 57.0000 | 23 | 0.0082 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p64_rs0p06_sk0p16_sa0p02_spg1p5_pd0_lg0p5_clb0 | 0 | seed_000 | -2.2587 | -2.1592 | 0.0100 | 0.0316 | 0.3730 | 59.0000 | 24 | 0.0159 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p56_rs0p06_sk0p16_sa0_spg0p5_pd0_lg0p5_clb0p5 | 0 | seed_000 | -2.3044 | -2.2531 | 0.0175 | 0.0167 | 0.3740 | 57.0000 | 30 | 0.0129 | `high_lateral_velocity, low_forward_velocity` |
| teacher_p0p48_rs0p04_sk0p16_sam0p02_spg0p5_pd2_lg0p5_clb1 | 0 | seed_002 | -2.3978 | -2.3716 | 0.0193 | 0.0183 | 0.3611 | 56.0000 | 25 | 0.0102 | `action_saturation, high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
