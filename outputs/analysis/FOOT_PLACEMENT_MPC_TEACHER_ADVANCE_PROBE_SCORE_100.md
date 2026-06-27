# Target Objective Score

status: `HOLD_NO_SEED_ROBUST_TARGETS`

This ranks target primitive traces by the worst seed. It does not run
simulation or training.

## Summary

- trace_files: `32`
- mode_count: `16`
- robust_mode_count: `0`
- required_seeds: `[0, 2]`
- window_samples: `100`

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
- `low_forward_velocity`: `16`
- `high_lateral_velocity`: `11`
- `single_contact_pattern_dominates`: `4`

### seed_002
- `low_forward_velocity`: `16`
- `high_lateral_velocity`: `14`
- `high_sent_target_velocity`: `3`
- `short_done_margin`: `1`

## Top Worst-Seed Candidates

| mode | pass_seeds | worst_seed | min_score | mean_score | seed0_vx | seed0_dx | seed0_wdx | seed2_vx | seed2_dx | seed2_wdx | seed2_vy95 | seed2_yaw95 | seed2_contact | seed2_transitions | seed2_foot_z95 | seed2_failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.3720 | -0.2740 | 0.0096 | 0.0192 | -0.0025 | 0.0160 | 0.0320 | -0.0272 | 0.1038 | 0.1485 | 82.0000 | 21 | 0.0068 | `low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.4226 | -0.3361 | 0.0036 | 0.0073 | 0.0001 | 0.0078 | 0.0157 | -0.0230 | 0.0736 | 0.0843 | 90.0000 | 8 | 0.0072 | `low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.5006 | -0.4476 | 0.0038 | 0.0077 | -0.0029 | 0.0086 | 0.0172 | -0.0365 | 0.1522 | 0.0742 | 75.0000 | 19 | 0.0059 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.5141 | -0.4336 | 0.0029 | 0.0057 | 0.0026 | 0.0140 | 0.0280 | -0.0398 | 0.1600 | 0.0735 | 76.0000 | 25 | 0.0060 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.5283 | -0.3919 | 0.0072 | 0.0143 | -0.0088 | 0.0064 | 0.0129 | -0.0395 | 0.1533 | 0.0589 | 75.0000 | 20 | 0.0064 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.5617 | -0.4872 | 0.0017 | 0.0033 | 0.0173 | 0.0152 | 0.0304 | -0.0629 | 0.1673 | 0.0798 | 70.0000 | 29 | 0.0069 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_000 | -0.5791 | -0.4581 | 0.0011 | 0.0023 | 0.0130 | 0.0145 | 0.0291 | -0.0464 | 0.1385 | 0.0897 | 78.0000 | 19 | 0.0051 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.6181 | -0.5534 | 0.0042 | 0.0084 | 0.0018 | 0.0173 | 0.0346 | -0.0356 | 0.1767 | 0.1806 | 76.0000 | 26 | 0.0048 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_000 | -0.6346 | -0.5832 | 0.0022 | 0.0043 | 0.0214 | 0.0105 | 0.0209 | -0.0394 | 0.1582 | 0.1037 | 73.0000 | 29 | 0.0063 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.7140 | -0.5949 | -0.0069 | -0.0137 | 0.0198 | 0.0095 | 0.0189 | -0.0439 | 0.1799 | 0.0582 | 80.0000 | 24 | 0.0045 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.8089 | -0.5946 | 0.0001 | 0.0002 | 0.0066 | 0.0108 | 0.0216 | -0.0476 | 0.1933 | 0.1415 | 67.0000 | 31 | 0.0058 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 0 | seed_002 | -0.8314 | -0.5792 | 0.0030 | 0.0060 | 0.0050 | 0.0131 | 0.0263 | -0.0424 | 0.1987 | 0.1282 | 77.0000 | 24 | 0.0048 | `high_lateral_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.8898 | -0.6104 | -0.0014 | -0.0028 | 0.0153 | 0.0141 | 0.0282 | -0.0514 | 0.2071 | 0.1223 | 72.0000 | 30 | 0.0053 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.9820 | -0.6586 | -0.0019 | -0.0038 | 0.0171 | 0.0173 | 0.0347 | -0.0480 | 0.2223 | 0.1444 | 72.0000 | 26 | 0.0052 | `high_lateral_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -0.9884 | -0.6827 | -0.0046 | -0.0093 | 0.0116 | 0.0141 | 0.0282 | -0.0678 | 0.2194 | 0.1304 | 56.0000 | 38 | 0.0054 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 0 | seed_002 | -2.0153 | -1.1545 | 0.0029 | 0.0059 | -0.0066 | -0.0331 | -0.0661 | -0.0226 | 0.2523 | 0.1364 | 50.0000 | 37 | 0.0137 | `high_lateral_velocity, high_sent_target_velocity, low_forward_velocity, short_done_margin` |

## Gate

- `PASS_SEED_ROBUST_TARGETS` requires at least one mode passing all required seeds.
- A high worst-seed score with seed2 lateral/contact failures is a near miss, not training permission.
- Do not build a supervised target manifest until robust modes exist.
