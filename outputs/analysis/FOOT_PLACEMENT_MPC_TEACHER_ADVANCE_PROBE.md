# Foot-Placement MPC Teacher Probe

status: `PASS_FOOT_PLACEMENT_MPC_PROBE_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0, 2]`
candidate_count: `16`

## Limitations

- first implementation uses joint-space approximations for swing-foot placement
- not a full nonlinear MPC solver
- passing still requires external 100-150 tick score artifacts

## Top Candidates

| candidate | runs | falls | complete | mean_vx | max_seed_vx | push_allowed_mean |
|---|---:|---:|---:|---:|---:|---:|
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0087 | 0.0174 | 46.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0087 | 0.0157 | 45.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0081 | 0.0160 | 44.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0075 | 0.0115 | 44.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0068 | 0.0162 | 36.00 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0065 | 0.0173 | 41.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0061 | 0.0072 | 48.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0060 | 0.0119 | 47.00 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0051 | 0.0110 | 42.00 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0048 | 0.0109 | 40.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0048 | 0.0097 | 49.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0047 | 0.0153 | 39.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0044 | 0.0120 | 46.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p02_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0042 | 0.0101 | 35.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0040 | 0.0089 | 52.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 2 | 1 | 1 | -0.0715 | -0.0027 | 39.89 |

## Interpretation

- This is an offline finite-horizon teacher probe, not policy training.
- Raw traces are ignored by git; compact summaries and score artifacts should be committed.
- A useful candidate must still pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
