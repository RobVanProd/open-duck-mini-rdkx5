# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `4`
- mode_count: `2`
- robust_mode_count: `0`
- required_seeds: `[2, 4]`
- window_samples: `150`

## Criteria

- min_mean_vx: `0.04`
- min_forward_displacement_m: `-1.0`
- max_vy_abs_p95: `0.12`
- max_contact_dominance_pct: `95.0`
- max_double_support_pct: `75.0`
- max_no_support_pct: `100.0`
- min_single_support_pct: `20.0`
- min_each_single_support_pct: `5.0`
- max_pitch_abs_p95: `0.35`
- min_base_height: `0.145`
- max_sent_velocity_p95: `2.5`
- max_tracking_p95: `0.2`
- min_done_margin: `50`
- min_contact_transitions: `2`
- min_foot_site_z_p95: `0.005`
- min_swing_segments_per_foot: `1`
- min_swing_rel_x_range_p95_m: `0.003`
- min_swing_rel_x_delta_p95_m: `-1.0`
- min_swing_peak_lift_m: `0.005`

## Seed Failure Counts

### seed_002
- `double_support_dominates`: `2`
- `low_forward_velocity`: `2`
- `single_support_not_balanced`: `2`
- `too_little_single_support`: `2`

### seed_004
- `double_support_dominates`: `1`
- `low_forward_velocity`: `1`
- `low_swing_peak_lift`: `1`
- `low_swing_rel_x_range`: `1`
- `missing_seed_trace_or_window`: `1`
- `single_contact_pattern_dominates`: `1`
- `single_support_not_balanced`: `1`
- `too_few_swing_segments`: `1`
- `too_little_single_support`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p005_shp0p02_skp0_sap0p02_sbx0_sg0_vxg0_pl0_pp1_tvl2p5_plg0p1_pyg0p1_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_004 | -1.8473 | -1.4149 | NA | NA | NA | 0.0079 | 0.0236 | -0.0130 | 0.0660 | 0.0635 | 94.0000 | 7 | 0.0170 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p005_shp0p02_skp0_sap0p02_sbx0_sg0_vxg0_pl0_pp1_tvl2p5_plg0p1_pyg0p1_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_004 | -999.0000 | -500.0375 | NA | NA | NA | -0.0010 | -0.0031 | 0.0012 | 0.0635 | 0.0513 | 94.6667 | 7 | 0.0145 | `double_support_dominates, low_forward_velocity, single_support_not_balanced, too_little_single_support` |

## Step Transition Metrics

| mode | worst_seed | seed2_min_swing_segments | seed2_min_rel_x_range_p95 | seed2_min_rel_x_delta_p95 | seed2_min_swing_peak_lift |
|---|---|---:|---:|---:|---:|
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p005_shp0p02_skp0_sap0p02_sbx0_sg0_vxg0_pl0_pp1_tvl2p5_plg0p1_pyg0p1_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | seed_004 | 1 | 0.0051 | 0.0051 | 0.0091 |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p005_shp0p02_skp0_sap0p02_sbx0_sg0_vxg0_pl0_pp1_tvl2p5_plg0p1_pyg0p1_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | seed_004 | 1 | 0.0041 | 0.0041 | 0.0085 |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
