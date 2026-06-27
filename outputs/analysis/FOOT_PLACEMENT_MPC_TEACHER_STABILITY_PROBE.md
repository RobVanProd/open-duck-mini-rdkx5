# Foot-Placement MPC Teacher Probe

status: `PASS_FOOT_PLACEMENT_MPC_PROBE_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0, 2]`
candidate_count: `64`

## Limitations

- first implementation uses joint-space approximations for swing-foot placement
- not a full nonlinear MPC solver
- passing still requires external 100-150 tick score artifacts

## Top Candidates

| candidate | runs | falls | complete | mean_vx | max_seed_vx | push_allowed_mean |
|---|---:|---:|---:|---:|---:|---:|
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p5_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0044 | 0.0056 | 43.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p5_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0044 | 0.0056 | 43.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p15_pms0p5_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0042 | 0.0062 | 52.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p25_pms0p5_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0042 | 0.0062 | 52.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0041 | 0.0053 | 39.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0041 | 0.0053 | 39.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p15_pms0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0038 | 0.0077 | 46.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p25_pms0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0038 | 0.0077 | 46.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0038 | 0.0039 | 36.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0038 | 0.0039 | 36.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p5_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0037 | 0.0037 | 41.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p5_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0037 | 0.0037 | 41.00 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p15_pms0p25_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0037 | 0.0051 | 46.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p25_pms0p25_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0037 | 0.0051 | 46.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p15_pms0p5_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0035 | 0.0058 | 50.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p12_pyg0p25_pms0p5_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0035 | 0.0058 | 50.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p5_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0035 | 0.0039 | 38.00 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p5_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0035 | 0.0039 | 38.00 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p15_pms0p5_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0035 | 0.0071 | 46.00 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg0p08_pyg0p25_pms0p5_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0035 | 0.0071 | 46.00 |

## Interpretation

- This is an offline finite-horizon teacher probe, not policy training.
- Raw traces are ignored by git; compact summaries and score artifacts should be committed.
- A useful candidate must still pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
