# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `36`
- mode_count: `18`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `150`

## Criteria

- min_mean_vx: `0.04`
- min_forward_displacement_m: `0.004`
- max_vy_abs_p95: `0.12`
- max_contact_dominance_pct: `95.0`
- max_double_support_pct: `75.0`
- max_no_support_pct: `100.0`
- min_single_support_pct: `20.0`
- min_each_single_support_pct: `5.0`
- max_pitch_abs_p95: `0.35`
- min_base_height: `0.145`
- max_sent_velocity_p95: `3.75`
- max_tracking_p95: `0.12`
- min_done_margin: `20`
- min_contact_transitions: `2`
- min_foot_site_z_p95: `-1.0`

## Seed Failure Counts

### seed_000
- `high_lateral_velocity`: `18`
- `low_forward_velocity`: `18`
- `high_sent_target_velocity`: `5`
- `double_support_dominates`: `2`

### seed_002
- `high_lateral_velocity`: `18`
- `low_forward_velocity`: `18`
- `high_sent_target_velocity`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0p04_sap0_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.0728 | -1.0353 | 0.0015 | 0.0045 | 0.0110 | 0.0329 | 0.2264 | 67.3333 | 41 | 0.0103 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0p04_sapm0p04_ssps1_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_000 | -1.1085 | -1.0680 | 0.0019 | 0.0058 | 0.0112 | 0.0335 | 0.2210 | 64.0000 | 38 | 0.0098 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0p04_sapm0p04_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.1256 | -1.0856 | 0.0035 | 0.0105 | 0.0103 | 0.0309 | 0.2323 | 66.6667 | 37 | 0.0105 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0p04_sap0p04_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_000 | -1.2202 | -1.1379 | 0.0086 | 0.0258 | 0.0124 | 0.0373 | 0.2259 | 68.6667 | 44 | 0.0104 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0_sap0_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_000 | -1.2795 | -1.2513 | 0.0063 | 0.0188 | 0.0125 | 0.0374 | 0.2469 | 64.0000 | 35 | 0.0116 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0_sapm0p04_ssps1_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.3105 | -1.2291 | 0.0060 | 0.0179 | 0.0138 | 0.0415 | 0.2594 | 66.0000 | 31 | 0.0108 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0_sapm0p04_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.3141 | -1.1781 | 0.0024 | 0.0071 | 0.0142 | 0.0425 | 0.2602 | 62.0000 | 39 | 0.0105 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0_sap0_ssps1_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.3280 | -1.2451 | 0.0033 | 0.0099 | 0.0146 | 0.0439 | 0.2625 | 61.3333 | 34 | 0.0110 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0p04_sap0p04_ssps1_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_000 | -1.3369 | -1.2827 | 0.0015 | 0.0045 | 0.0102 | 0.0305 | 0.2450 | 66.6667 | 28 | 0.0085 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skpm0p04_sapm0p04_ssps1_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.3561 | -1.2693 | 0.0092 | 0.0277 | 0.0126 | 0.0378 | 0.2637 | 62.0000 | 32 | 0.0074 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0p04_sap0_ssps1_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.3657 | -1.2054 | 0.0041 | 0.0124 | 0.0119 | 0.0357 | 0.2641 | 70.0000 | 31 | 0.0079 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skpm0p04_sap0p04_ssps1_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.3883 | -1.2509 | 0.0024 | 0.0073 | 0.0171 | 0.0513 | 0.2728 | 60.0000 | 37 | 0.0098 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skpm0p04_sap0p04_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.3905 | -1.3871 | 0.0085 | 0.0255 | 0.0122 | 0.0367 | 0.2676 | 62.0000 | 34 | 0.0104 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skpm0p04_sap0_ssps1_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.5846 | -1.3695 | 0.0059 | 0.0178 | 0.0157 | 0.0471 | 0.2645 | 63.3333 | 36 | 0.0121 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0_sap0p04_ssps1_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_000 | -1.5932 | -1.5577 | 0.0052 | 0.0156 | 0.0141 | 0.0422 | 0.2549 | 60.6667 | 39 | 0.0110 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skpm0p04_sapm0p04_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_000 | -1.6026 | -1.5018 | 0.0019 | 0.0056 | 0.0170 | 0.0509 | 0.2742 | 62.6667 | 36 | 0.0099 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skpm0p04_sap0_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_000 | -1.6029 | -1.4641 | 0.0040 | 0.0121 | 0.0144 | 0.0432 | 0.2619 | 66.0000 | 31 | 0.0094 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0_sap0p04_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.6944 | -1.4764 | 0.0028 | 0.0084 | 0.0171 | 0.0514 | 0.3111 | 66.6667 | 32 | 0.0103 | `high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
