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
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0097 | 0.0189 | 32.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0096 | 0.0143 | 28.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0090 | 0.0166 | 32.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0085 | 0.0118 | 28.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0083 | 0.0089 | 24.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0082 | 0.0121 | 30.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0080 | 0.0094 | 22.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0079 | 0.0166 | 32.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0069 | 0.0127 | 35.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0047 | 0.0100 | 27.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0046 | 0.0091 | 34.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0041 | 0.0088 | 27.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0033 | 0.0084 | 24.00 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 2 | 1 | 1 | -0.0560 | 0.0070 | 34.22 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg0p5_byg0p5 | 2 | 1 | 1 | -0.0608 | 0.0067 | 28.22 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_rg1p5_vyg1_byg0p5 | 2 | 1 | 1 | -0.0694 | 0.0025 | 29.66 |

## Interpretation

- This is an offline finite-horizon teacher probe, not policy training.
- Raw traces are ignored by git; compact summaries and score artifacts should be committed.
- A useful candidate must still pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
