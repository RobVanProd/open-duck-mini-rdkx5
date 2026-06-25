# Foot-Placement MPC Teacher Probe

status: `PASS_FOOT_PLACEMENT_MPC_PROBE_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0, 2]`
candidate_count: `72`

## Limitations

- first implementation uses joint-space approximations for swing-foot placement
- not a full nonlinear MPC solver
- passing still requires external 100-150 tick score artifacts

## Top Candidates

| candidate | runs | falls | complete | mean_vx | max_seed_vx | push_allowed_mean |
|---|---:|---:|---:|---:|---:|---:|
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0155 | 0.0294 | 31.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0134 | 0.0242 | 32.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_ygm0p8_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0118 | 0.0180 | 28.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_ygm0p8_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0118 | 0.0180 | 28.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_ygm0p8_yvg0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0118 | 0.0180 | 28.00 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_ygm0p8_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0118 | 0.0202 | 29.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_ygm0p8_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0118 | 0.0202 | 29.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_ygm0p8_yvg0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0118 | 0.0202 | 29.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_ygm0p8_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0112 | 0.0220 | 24.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_ygm0p8_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0112 | 0.0220 | 24.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_ygm0p8_yvg0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0112 | 0.0220 | 24.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0112 | 0.0159 | 34.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0101 | 0.0190 | 32.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0095 | 0.0206 | 33.00 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0085 | 0.0118 | 28.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0084 | 0.0170 | 33.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0082 | 0.0121 | 30.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0080 | 0.0094 | 22.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0079 | 0.0166 | 32.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_plg1000_pyg1000_pms1_yg0_yvg0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0077 | 0.0152 | 33.67 |

## Interpretation

- This is an offline finite-horizon teacher probe, not policy training.
- Raw traces are ignored by git; compact summaries and score artifacts should be committed.
- A useful candidate must still pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
