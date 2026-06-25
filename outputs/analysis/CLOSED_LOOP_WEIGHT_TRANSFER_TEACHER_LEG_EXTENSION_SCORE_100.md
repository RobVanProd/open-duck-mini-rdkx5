# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `36`
- mode_count: `18`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `100`

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
- `double_support_dominates`: `13`
- `high_sent_target_velocity`: `3`
- `too_little_single_support`: `3`
- `single_support_not_balanced`: `1`

### seed_002
- `high_lateral_velocity`: `18`
- `low_forward_velocity`: `18`
- `high_sent_target_velocity`: `3`
- `double_support_dominates`: `2`
- `low_forward_displacement`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0p04_sap0p04_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -0.6694 | -0.6157 | 0.0077 | 0.0154 | 0.0054 | 0.0108 | 0.1673 | 76.0000 | 30 | 0.0065 | `double_support_dominates, high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0p04_sapm0p04_ssps1_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_000 | -0.8383 | -0.7973 | 0.0056 | 0.0112 | 0.0052 | 0.0104 | 0.1804 | 72.0000 | 24 | 0.0056 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0p04_sapm0p04_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -0.9032 | -0.8231 | 0.0098 | 0.0196 | 0.0018 | 0.0036 | 0.1945 | 74.0000 | 23 | 0.0053 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0_sapm0p04_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -0.9053 | -0.8499 | 0.0052 | 0.0104 | 0.0088 | 0.0176 | 0.2031 | 68.0000 | 24 | 0.0073 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0p04_sap0p04_ssps1_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -0.9119 | -0.9107 | 0.0021 | 0.0043 | 0.0045 | 0.0090 | 0.1991 | 74.0000 | 16 | 0.0047 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0p04_sap0_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -0.9640 | -0.7683 | 0.0020 | 0.0041 | 0.0019 | 0.0039 | 0.2026 | 75.0000 | 27 | 0.0057 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skpm0p04_sap0_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_000 | -0.9694 | -0.9557 | 0.0073 | 0.0145 | 0.0079 | 0.0159 | 0.2067 | 71.0000 | 23 | 0.0058 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skpm0p04_sapm0p04_ssps1_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.0385 | -0.8153 | 0.0090 | 0.0181 | 0.0085 | 0.0171 | 0.2194 | 67.0000 | 21 | 0.0063 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0p04_sap0_ssps1_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.0610 | -0.8954 | 0.0062 | 0.0125 | 0.0081 | 0.0162 | 0.2167 | 77.0000 | 17 | 0.0059 | `double_support_dominates, high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skpm0p04_sap0p04_ssps1_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.0761 | -1.0306 | 0.0059 | 0.0117 | 0.0108 | 0.0216 | 0.2267 | 66.0000 | 26 | 0.0069 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0_sap0_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_000 | -1.0803 | -1.0692 | 0.0107 | 0.0213 | 0.0032 | 0.0065 | 0.2159 | 70.0000 | 23 | 0.0053 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0_sap0p04_ssps1_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.1328 | -1.0353 | 0.0083 | 0.0166 | 0.0042 | 0.0084 | 0.2263 | 67.0000 | 23 | 0.0070 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skpm0p04_sap0p04_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.1529 | -1.1321 | 0.0126 | 0.0252 | 0.0036 | 0.0071 | 0.1983 | 68.0000 | 23 | 0.0048 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0_sapm0p04_ssps1_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.1614 | -0.9669 | 0.0096 | 0.0192 | 0.0189 | 0.0378 | 0.2464 | 60.0000 | 26 | 0.0113 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skpm0p04_sapm0p04_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.1754 | -1.0911 | 0.0033 | 0.0066 | 0.0122 | 0.0245 | 0.2407 | 71.0000 | 21 | 0.0080 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0_sap0_ssps1_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.2496 | -1.0889 | 0.0099 | 0.0197 | 0.0184 | 0.0367 | 0.2569 | 53.0000 | 26 | 0.0116 | `high_lateral_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skpm0p04_sap0_ssps1_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.2739 | -1.1154 | 0.0075 | 0.0151 | 0.0075 | 0.0151 | 0.2165 | 70.0000 | 23 | 0.0067 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_skp0_sap0p04_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lg1_byg1_plg0p06_clb1 | 0 | seed_002 | -1.3348 | -0.9824 | 0.0078 | 0.0157 | 0.0207 | 0.0413 | 0.2701 | 66.0000 | 21 | 0.0110 | `high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
