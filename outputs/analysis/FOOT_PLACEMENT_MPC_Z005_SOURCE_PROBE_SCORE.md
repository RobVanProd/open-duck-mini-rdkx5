# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `32`
- mode_count: `16`
- robust_mode_count: `0`
- required_seeds: `[0, 5]`
- window_samples: `50`

## Criteria

- min_mean_vx: `0.028`
- min_forward_displacement_m: `0.01`
- max_vy_abs_p95: `0.25`
- max_contact_dominance_pct: `95.0`
- max_double_support_pct: `80.0`
- max_no_support_pct: `100.0`
- min_single_support_pct: `20.0`
- min_each_single_support_pct: `2.0`
- max_pitch_abs_p95: `0.25`
- min_base_height: `0.12`
- max_sent_velocity_p95: `2.5`
- max_tracking_p95: `0.2`
- min_done_margin: `0`
- min_contact_transitions: `1`
- min_foot_site_z_p95: `-1.0`
- min_swing_segments_per_foot: `0`
- min_swing_rel_x_range_p95_m: `-1.0`
- min_swing_rel_x_delta_p95_m: `-1.0`
- min_swing_peak_lift_m: `-1.0`

## Seed Failure Counts

### seed_000
- `double_support_dominates`: `16`
- `low_forward_displacement`: `16`
- `low_forward_velocity`: `16`
- `too_little_single_support`: `16`
- `single_support_not_balanced`: `8`

### seed_005
- `missing_seed_trace_or_window`: `16`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0p04_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 0 | seed_005 | -999.0000 | -499.8598 | -0.0010 | -0.0010 | -0.0044 | NA | NA | NA | NA | NA | NA | NA | NA | `` |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 0 | seed_005 | -999.0000 | -499.8612 | -0.0011 | -0.0011 | -0.0040 | NA | NA | NA | NA | NA | NA | NA | NA | `` |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 0 | seed_005 | -999.0000 | -499.8612 | -0.0011 | -0.0011 | -0.0040 | NA | NA | NA | NA | NA | NA | NA | NA | `` |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0p04_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 0 | seed_005 | -999.0000 | -499.8612 | -0.0011 | -0.0011 | -0.0040 | NA | NA | NA | NA | NA | NA | NA | NA | `` |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0p04_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 0 | seed_005 | -999.0000 | -499.8612 | -0.0011 | -0.0011 | -0.0040 | NA | NA | NA | NA | NA | NA | NA | NA | `` |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 0 | seed_005 | -999.0000 | -499.8612 | -0.0011 | -0.0011 | -0.0040 | NA | NA | NA | NA | NA | NA | NA | NA | `` |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 0 | seed_005 | -999.0000 | -499.8612 | -0.0011 | -0.0011 | -0.0040 | NA | NA | NA | NA | NA | NA | NA | NA | `` |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0p04_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 0 | seed_005 | -999.0000 | -499.8924 | -0.0050 | -0.0050 | -0.0011 | NA | NA | NA | NA | NA | NA | NA | NA | `` |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0p04_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 0 | seed_005 | -999.0000 | -499.8976 | 0.0064 | 0.0064 | -0.0128 | NA | NA | NA | NA | NA | NA | NA | NA | `` |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 0 | seed_005 | -999.0000 | -499.9070 | 0.0053 | 0.0053 | -0.0120 | NA | NA | NA | NA | NA | NA | NA | NA | `` |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 0 | seed_005 | -999.0000 | -499.9070 | 0.0053 | 0.0053 | -0.0120 | NA | NA | NA | NA | NA | NA | NA | NA | `` |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0p04_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 0 | seed_005 | -999.0000 | -499.9070 | 0.0053 | 0.0053 | -0.0120 | NA | NA | NA | NA | NA | NA | NA | NA | `` |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0p04_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 0 | seed_005 | -999.0000 | -499.9070 | 0.0053 | 0.0053 | -0.0120 | NA | NA | NA | NA | NA | NA | NA | NA | `` |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 0 | seed_005 | -999.0000 | -499.9070 | 0.0053 | 0.0053 | -0.0120 | NA | NA | NA | NA | NA | NA | NA | NA | `` |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 0 | seed_005 | -999.0000 | -499.9070 | 0.0053 | 0.0053 | -0.0120 | NA | NA | NA | NA | NA | NA | NA | NA | `` |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0p04_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 0 | seed_005 | -999.0000 | -499.9143 | 0.0044 | 0.0044 | -0.0114 | NA | NA | NA | NA | NA | NA | NA | NA | `` |

## Step Transition Metrics

| mode | worst_seed | seed2_min_swing_segments | seed2_min_rel_x_range_p95 | seed2_min_rel_x_delta_p95 | seed2_min_swing_peak_lift |
|---|---|---:|---:|---:|---:|
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0p04_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | seed_005 | NA | NA | NA | NA |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | seed_005 | NA | NA | NA | NA |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | seed_005 | NA | NA | NA | NA |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0p04_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | seed_005 | NA | NA | NA | NA |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0p04_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | seed_005 | NA | NA | NA | NA |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | seed_005 | NA | NA | NA | NA |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | seed_005 | NA | NA | NA | NA |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0p04_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | seed_005 | NA | NA | NA | NA |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0p04_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | seed_005 | NA | NA | NA | NA |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | seed_005 | NA | NA | NA | NA |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | seed_005 | NA | NA | NA | NA |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0p04_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | seed_005 | NA | NA | NA | NA |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0p04_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | seed_005 | NA | NA | NA | NA |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | seed_005 | NA | NA | NA | NA |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | seed_005 | NA | NA | NA | NA |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0p04_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | seed_005 | NA | NA | NA | NA |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
