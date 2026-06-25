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
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0312 | 0.0489 | 51.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0251 | 0.0259 | 56.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0250 | 0.0261 | 58.00 |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0245 | 0.0285 | 52.00 |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0235 | 0.0264 | 58.00 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0234 | 0.0272 | 50.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0233 | 0.0239 | 48.67 |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0232 | 0.0243 | 57.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0230 | 0.0268 | 56.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0227 | 0.0383 | 49.00 |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0226 | 0.0315 | 56.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0220 | 0.0286 | 56.33 |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0219 | 0.0386 | 45.33 |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0216 | 0.0337 | 50.00 |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0213 | 0.0308 | 47.33 |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0211 | 0.0391 | 43.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0210 | 0.0320 | 49.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0209 | 0.0240 | 51.67 |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0209 | 0.0296 | 52.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0208 | 0.0322 | 48.67 |

## Interpretation

- This is an offline finite-horizon teacher probe, not policy training.
- Raw traces are ignored by git; compact summaries and score artifacts should be committed.
- A useful candidate must still pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
