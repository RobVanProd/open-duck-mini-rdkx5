# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `24`
- mode_count: `12`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `150`

## Criteria

- min_mean_vx: `0.04`
- min_forward_displacement_m: `0.06`
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
- `double_support_dominates`: `12`
- `low_forward_displacement`: `12`
- `low_forward_velocity`: `12`
- `single_support_not_balanced`: `12`
- `too_little_single_support`: `12`
- `single_contact_pattern_dominates`: `8`
- `high_lateral_velocity`: `4`

### seed_002
- `low_forward_displacement`: `12`
- `low_forward_velocity`: `12`
- `double_support_dominates`: `8`
- `high_lateral_velocity`: `7`
- `too_little_single_support`: `5`
- `single_support_not_balanced`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed2_vx | seed2_dx | seed2_vy95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy2_kdy0p5_kpvx1_ffp0p02_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.7049 | -1.5225 | 0.0005 | 0.0015 | 0.0032 | 0.0096 | 0.1195 | 92.0000 | 6 | 0.0046 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p04_lvg0p12_kpy2_kdy0p5_kpvx1_ffp0p02_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.7049 | -1.5225 | 0.0005 | 0.0015 | 0.0032 | 0.0096 | 0.1195 | 92.0000 | 6 | 0.0046 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.7188 | -1.5271 | 0.0003 | 0.0009 | 0.0031 | 0.0092 | 0.1198 | 91.3333 | 8 | 0.0046 | `double_support_dominates, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p3_uf0p2_lo0p03_byg0p04_lvg0p12_kpy2_kdy0p2_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.7459 | -1.5099 | 0.0005 | 0.0015 | 0.0046 | 0.0137 | 0.1286 | 87.3333 | 21 | 0.0050 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p3_uf0p2_lo0p03_byg0p04_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.7459 | -1.5099 | 0.0005 | 0.0015 | 0.0046 | 0.0137 | 0.1286 | 87.3333 | 21 | 0.0050 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p04_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.7968 | -1.5641 | 0.0003 | 0.0010 | 0.0043 | 0.0130 | 0.1238 | 92.6667 | 7 | 0.0045 | `double_support_dominates, high_lateral_velocity, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy2_kdy0p2_kpvx1_ffp0p02_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.7968 | -1.6417 | 0.0003 | 0.0010 | 0.0041 | 0.0122 | 0.1376 | 93.3333 | 7 | 0.0046 | `double_support_dominates, high_lateral_velocity, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p04_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p02_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.7968 | -1.6417 | 0.0003 | 0.0010 | 0.0041 | 0.0122 | 0.1376 | 93.3333 | 7 | 0.0046 | `double_support_dominates, high_lateral_velocity, low_forward_displacement, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.8401 | -1.6713 | -0.0001 | -0.0002 | 0.0020 | 0.0060 | 0.0985 | 94.0000 | 4 | 0.0044 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |
| com_p0p56_lf0p3_uf0p2_lo0p03_byg0p04_lvg0p12_kpy2_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.8991 | -1.6029 | -0.0000 | -0.0001 | 0.0048 | 0.0143 | 0.1345 | 86.0000 | 21 | 0.0047 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p3_uf0p2_lo0p03_byg0p03_lvg0p12_kpy2_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.9023 | -1.6418 | -0.0001 | -0.0002 | 0.0050 | 0.0149 | 0.1454 | 86.0000 | 21 | 0.0052 | `high_lateral_velocity, low_forward_displacement, low_forward_velocity` |
| com_p0p56_lf0p3_uf0p2_lo0p03_byg0p03_lvg0p12_kpy1_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 0 | seed_000 | -1.9120 | -1.6939 | -0.0002 | -0.0005 | 0.0028 | 0.0083 | 0.1111 | 94.6667 | 7 | 0.0045 | `double_support_dominates, low_forward_displacement, low_forward_velocity, too_little_single_support` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
