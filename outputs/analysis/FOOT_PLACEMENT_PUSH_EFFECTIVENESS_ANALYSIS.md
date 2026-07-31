# Foot-Placement Push Effectiveness Analysis

status: `HOLD_PUSH_INEFFECTIVE`
trace_count: `32`
usable_trace_count: `32`
lookahead_s: `0.1`

## Aggregate

- mean_push_allowed_pct: `27.5362`
- mean_push_future_vx_delta_m_s: `-0.0003`
- status_counts: `{'HOLD_PUSH_INEFFECTIVE': 32}`
- failure_counts: `{'push_does_not_accelerate': 19, 'push_lateral_velocity_high': 32, 'push_target_velocity_high': 18}`

## Per Trace

| mode | seed | status | push_pct | push_dvx_mean | push_vx_mean | nonpush_vx_mean | push_vy95 | pitch_vel95 | failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | HOLD_PUSH_INEFFECTIVE | 18.62 | -0.0139 | 0.0380 | -0.0115 | 0.2018 | 4.7960 | `push_does_not_accelerate, push_lateral_velocity_high, push_target_velocity_high` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | HOLD_PUSH_INEFFECTIVE | 31.03 | -0.0027 | 0.0295 | 0.0045 | 0.2249 | 4.9440 | `push_does_not_accelerate, push_lateral_velocity_high, push_target_velocity_high` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | HOLD_PUSH_INEFFECTIVE | 15.86 | -0.0315 | 0.0609 | -0.0073 | 0.1832 | 1.3384 | `push_does_not_accelerate, push_lateral_velocity_high` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | HOLD_PUSH_INEFFECTIVE | 25.52 | 0.0075 | 0.0382 | 0.0036 | 0.2182 | 3.7600 | `push_lateral_velocity_high, push_target_velocity_high` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | HOLD_PUSH_INEFFECTIVE | 18.62 | -0.0166 | 0.0345 | -0.0080 | 0.2003 | 5.2400 | `push_does_not_accelerate, push_lateral_velocity_high, push_target_velocity_high` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | HOLD_PUSH_INEFFECTIVE | 48.51 | -0.0207 | -0.0322 | -0.1278 | 0.2322 | 3.7600 | `push_does_not_accelerate, push_lateral_velocity_high, push_target_velocity_high` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | HOLD_PUSH_INEFFECTIVE | 19.31 | -0.0002 | 0.0123 | -0.0088 | 0.2011 | 2.5128 | `push_does_not_accelerate, push_lateral_velocity_high` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | HOLD_PUSH_INEFFECTIVE | 33.33 | 0.0054 | -0.0067 | -0.1163 | 0.2408 | 3.7600 | `push_lateral_velocity_high, push_target_velocity_high` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | HOLD_PUSH_INEFFECTIVE | 15.86 | 0.0005 | 0.0354 | -0.0025 | 0.2068 | 3.6340 | `push_does_not_accelerate, push_lateral_velocity_high` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | HOLD_PUSH_INEFFECTIVE | 35.86 | 0.0035 | 0.0135 | 0.0010 | 0.2107 | 3.7600 | `push_does_not_accelerate, push_lateral_velocity_high, push_target_velocity_high` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | HOLD_PUSH_INEFFECTIVE | 16.55 | -0.0203 | 0.0503 | -0.0069 | 0.1764 | 2.3379 | `push_does_not_accelerate, push_lateral_velocity_high` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | HOLD_PUSH_INEFFECTIVE | 22.76 | 0.0124 | 0.0277 | 0.0049 | 0.2173 | 3.7600 | `push_lateral_velocity_high, push_target_velocity_high` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | HOLD_PUSH_INEFFECTIVE | 17.24 | -0.0021 | 0.0161 | -0.0007 | 0.1694 | 4.9440 | `push_does_not_accelerate, push_lateral_velocity_high, push_target_velocity_high` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | HOLD_PUSH_INEFFECTIVE | 42.76 | 0.0028 | 0.0029 | 0.0254 | 0.2126 | 5.1660 | `push_does_not_accelerate, push_lateral_velocity_high, push_target_velocity_high` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | HOLD_PUSH_INEFFECTIVE | 17.24 | 0.0111 | 0.0124 | -0.0017 | 0.1997 | 2.4985 | `push_lateral_velocity_high` |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | HOLD_PUSH_INEFFECTIVE | 30.34 | 0.0121 | 0.0134 | 0.0150 | 0.2320 | 3.7600 | `push_lateral_velocity_high, push_target_velocity_high` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | HOLD_PUSH_INEFFECTIVE | 28.28 | -0.0049 | 0.0431 | -0.0084 | 0.1737 | 2.5000 | `push_does_not_accelerate, push_lateral_velocity_high` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | HOLD_PUSH_INEFFECTIVE | 39.31 | 0.0079 | 0.0149 | 0.0109 | 0.2370 | 4.0560 | `push_lateral_velocity_high, push_target_velocity_high` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | HOLD_PUSH_INEFFECTIVE | 27.59 | 0.0118 | 0.0295 | -0.0072 | 0.1926 | 2.5630 | `push_lateral_velocity_high` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | HOLD_PUSH_INEFFECTIVE | 28.28 | 0.0022 | 0.0183 | 0.0064 | 0.2012 | 3.7600 | `push_does_not_accelerate, push_lateral_velocity_high, push_target_velocity_high` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | HOLD_PUSH_INEFFECTIVE | 20.69 | -0.0212 | 0.0493 | -0.0086 | 0.1647 | 1.9042 | `push_does_not_accelerate, push_lateral_velocity_high` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | HOLD_PUSH_INEFFECTIVE | 44.83 | 0.0069 | 0.0017 | 0.0164 | 0.2291 | 4.9440 | `push_lateral_velocity_high, push_target_velocity_high` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | HOLD_PUSH_INEFFECTIVE | 20.69 | 0.0070 | 0.0207 | -0.0045 | 0.1593 | 2.2563 | `push_lateral_velocity_high` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | HOLD_PUSH_INEFFECTIVE | 34.48 | 0.0039 | 0.0107 | 0.0209 | 0.2091 | 3.7600 | `push_does_not_accelerate, push_lateral_velocity_high, push_target_velocity_high` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | HOLD_PUSH_INEFFECTIVE | 21.38 | -0.0040 | 0.0347 | -0.0091 | 0.1640 | 2.2511 | `push_does_not_accelerate, push_lateral_velocity_high` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | HOLD_PUSH_INEFFECTIVE | 30.34 | 0.0075 | 0.0116 | 0.0083 | 0.2289 | 5.0180 | `push_lateral_velocity_high, push_target_velocity_high` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | HOLD_PUSH_INEFFECTIVE | 22.76 | 0.0050 | 0.0265 | -0.0072 | 0.1652 | 3.0040 | `push_lateral_velocity_high` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | HOLD_PUSH_INEFFECTIVE | 31.03 | 0.0090 | 0.0145 | 0.0106 | 0.2164 | 4.9440 | `push_lateral_velocity_high, push_target_velocity_high` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 0 | HOLD_PUSH_INEFFECTIVE | 30.34 | -0.0019 | 0.0148 | 0.0038 | 0.1861 | 2.5195 | `push_does_not_accelerate, push_lateral_velocity_high` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | HOLD_PUSH_INEFFECTIVE | 31.72 | 0.0038 | 0.0007 | 0.0092 | 0.2132 | 3.7600 | `push_does_not_accelerate, push_lateral_velocity_high, push_target_velocity_high` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 0 | HOLD_PUSH_INEFFECTIVE | 21.38 | -0.0082 | 0.0392 | -0.0074 | 0.1682 | 2.0242 | `push_does_not_accelerate, push_lateral_velocity_high` |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | HOLD_PUSH_INEFFECTIVE | 38.62 | 0.0176 | 0.0031 | 0.0209 | 0.2031 | 2.5182 | `push_lateral_velocity_high` |

## Interpretation

- This analyzes existing traces only; it does not run simulation or training.
- `push_future_vx_delta_m_s` is the local forward velocity change after the configured lookahead.
- If push is frequent but the velocity delta is near zero or negative, the current propulsion primitive is ineffective rather than merely under-scheduled.
