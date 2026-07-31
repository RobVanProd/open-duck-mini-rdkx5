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
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0257 | 0.0356 | 46.00 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0250 | 0.0436 | 46.00 |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0226 | 0.0351 | 48.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0224 | 0.0287 | 47.00 |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0216 | 0.0330 | 49.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0212 | 0.0328 | 45.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0211 | 0.0228 | 48.67 |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0207 | 0.0252 | 48.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0205 | 0.0214 | 37.00 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0201 | 0.0327 | 48.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0200 | 0.0340 | 44.00 |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0195 | 0.0348 | 48.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0187 | 0.0311 | 35.67 |
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0181 | 0.0275 | 46.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0177 | 0.0232 | 39.00 |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0175 | 0.0231 | 46.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0174 | 0.0225 | 45.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0174 | 0.0184 | 33.67 |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_tvl3_plg1000_pyg1000_pms1_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0173 | 0.0358 | 39.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_tvl2p5_plg1000_pyg1000_pms1_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0170 | 0.0260 | 39.33 |

## Interpretation

- This is an offline finite-horizon teacher probe, not policy training.
- Raw traces are ignored by git; compact summaries and score artifacts should be committed.
- A useful candidate must still pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
