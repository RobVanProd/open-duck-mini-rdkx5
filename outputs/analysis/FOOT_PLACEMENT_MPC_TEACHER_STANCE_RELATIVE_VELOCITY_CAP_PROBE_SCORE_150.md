# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `128`
- mode_count: `64`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `150`

## Criteria

- min_mean_vx: `0.04`
- min_forward_displacement_m: `-1.0`
- max_vy_abs_p95: `0.12`
- max_contact_dominance_pct: `95.0`
- max_double_support_pct: `100.0`
- max_no_support_pct: `100.0`
- min_single_support_pct: `0.0`
- min_each_single_support_pct: `0.0`
- max_pitch_abs_p95: `0.35`
- min_base_height: `0.145`
- max_sent_velocity_p95: `2.5`
- max_tracking_p95: `0.12`
- min_done_margin: `50`
- min_contact_transitions: `0`
- min_foot_site_z_p95: `-1.0`

## Seed Failure Counts

### seed_000
- `high_lateral_velocity`: `58`
- `low_forward_velocity`: `58`
- `high_sent_target_velocity`: `30`
- `missing_seed_trace_or_window`: `6`
- `high_body_pitch`: `3`
- `low_base_height`: `2`
- `done_inside_window`: `1`

### seed_002
- `high_lateral_velocity`: `62`
- `low_forward_velocity`: `61`
- `high_sent_target_velocity`: `23`
- `missing_seed_trace_or_window`: `2`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.9578 | -0.8536 | 0.0121 | 0.0363 | 0.0208 | 0.0102 | 0.0306 | -0.0359 | 0.1851 | 0.3964 | 81.3333 | 17 | 0.0081 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.9951 | -0.8544 | 0.0096 | 0.0289 | -0.0039 | 0.0328 | 0.0984 | -0.0947 | 0.2061 | 0.4028 | 56.0000 | 44 | 0.0095 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.0149 | -0.8180 | 0.0193 | 0.0578 | -0.0191 | 0.0102 | 0.0307 | -0.0444 | 0.1692 | 0.4132 | 68.0000 | 36 | 0.0080 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.0932 | -0.9648 | 0.0155 | 0.0465 | 0.0154 | 0.0083 | 0.0249 | -0.0323 | 0.1939 | 0.4236 | 77.3333 | 25 | 0.0074 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1164 | -1.0836 | 0.0034 | 0.0101 | 0.0048 | 0.0277 | 0.0830 | -0.0893 | 0.2507 | 0.2325 | 51.3333 | 40 | 0.0090 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.1228 | -0.8460 | 0.0052 | 0.0155 | 0.0215 | 0.0159 | 0.0478 | -0.0627 | 0.1691 | 0.4351 | 72.6667 | 30 | 0.0098 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -1.1245 | -1.0331 | 0.0065 | 0.0194 | 0.0108 | 0.0188 | 0.0563 | -0.0583 | 0.2417 | 0.1367 | 70.0000 | 24 | 0.0117 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.1311 | -0.9498 | 0.0103 | 0.0310 | 0.0177 | 0.0108 | 0.0325 | -0.0387 | 0.1882 | 0.3953 | 74.0000 | 27 | 0.0100 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.1659 | -1.0938 | 0.0127 | 0.0380 | -0.0082 | 0.0188 | 0.0564 | -0.0581 | 0.2289 | 0.3933 | 60.0000 | 39 | 0.0094 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.1747 | -0.9795 | 0.0080 | 0.0239 | 0.0136 | 0.0260 | 0.0780 | -0.0852 | 0.2073 | 0.4567 | 54.6667 | 29 | 0.0106 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.2173 | -0.9776 | 0.0174 | 0.0523 | 0.0166 | 0.0152 | 0.0456 | -0.0578 | 0.1893 | 0.4327 | 69.3333 | 30 | 0.0080 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.2271 | -0.8875 | 0.0184 | 0.0552 | 0.0147 | 0.0163 | 0.0490 | -0.0390 | 0.1669 | 0.4258 | 72.6667 | 26 | 0.0076 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.2662 | -1.2661 | 0.0077 | 0.0231 | 0.0057 | 0.0235 | 0.0704 | -0.0909 | 0.2646 | 0.3613 | 54.6667 | 38 | 0.0119 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.2926 | -1.0777 | 0.0232 | 0.0696 | -0.0381 | 0.0122 | 0.0367 | -0.0379 | 0.2016 | 0.3806 | 71.3333 | 26 | 0.0079 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.3027 | -1.2228 | 0.0076 | 0.0229 | 0.0398 | 0.0150 | 0.0450 | -0.0674 | 0.2397 | 0.3922 | 68.0000 | 29 | 0.0102 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.3142 | -1.2088 | 0.0228 | 0.0683 | 0.0023 | 0.0194 | 0.0581 | -0.0919 | 0.2397 | 0.3457 | 52.6667 | 28 | 0.0116 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.3179 | -1.0902 | 0.0119 | 0.0356 | -0.0176 | 0.0231 | 0.0693 | -0.0701 | 0.2138 | 0.2909 | 57.3333 | 40 | 0.0094 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.3180 | -1.0327 | 0.0053 | 0.0158 | 0.0207 | 0.0210 | 0.0629 | -0.0768 | 0.1970 | 0.3869 | 63.3333 | 30 | 0.0090 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.3213 | -1.1037 | 0.0142 | 0.0427 | 0.0030 | 0.0113 | 0.0339 | -0.0535 | 0.2035 | 0.3972 | 69.3333 | 30 | 0.0100 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.3612 | -1.1372 | 0.0076 | 0.0227 | -0.0175 | 0.0213 | 0.0639 | -0.0610 | 0.2181 | 0.3591 | 52.6667 | 33 | 0.0093 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.4175 | -1.2795 | 0.0162 | 0.0487 | -0.0035 | 0.0252 | 0.0756 | -0.0800 | 0.2511 | 0.3096 | 46.0000 | 45 | 0.0088 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.4358 | -1.4024 | 0.0185 | 0.0556 | -0.0228 | 0.0127 | 0.0380 | -0.0432 | 0.2029 | 0.3622 | 73.3333 | 27 | 0.0099 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.4899 | -1.1815 | 0.0224 | 0.0671 | -0.0025 | 0.0115 | 0.0344 | -0.0450 | 0.2020 | 0.3718 | 66.0000 | 24 | 0.0084 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.4922 | -1.4252 | 0.0060 | 0.0180 | 0.0114 | 0.0156 | 0.0469 | -0.0537 | 0.2049 | 0.3844 | 65.3333 | 39 | 0.0082 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -1.4988 | -1.1532 | 0.0060 | 0.0179 | 0.0016 | 0.0340 | 0.1020 | -0.1015 | 0.2192 | 0.3422 | 52.0000 | 41 | 0.0106 | `high_lateral_velocity, low_forward_velocity` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
