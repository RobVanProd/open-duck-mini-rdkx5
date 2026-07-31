# Foot-Placement MPC Teacher Probe

status: `PASS_FOOT_PLACEMENT_MPC_PROBE_RAN`
command_x: `0.08`
duration_s: `2.0`
seeds: `[0, 5]`
terrain_override: `{'enabled': True, 'hfield_z_scale': 0.005, 'source_xml': '/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_rough_terrain_backlash.xml', 'temp_xml': '/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/.codex_eval_ao8pdqc4_hfield_z0.005.xml'}`
candidate_count: `16`

## Limitations

- first implementation uses joint-space approximations for swing-foot placement
- not a full nonlinear MPC solver
- passing still requires external 100-150 tick score artifacts

## Top Candidates

| candidate | runs | falls | complete | mean_vx | max_seed_vx | push_allowed_mean |
|---|---:|---:|---:|---:|---:|---:|
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0p04_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 2 | 1 | 1 | -0.1772 | 0.0026 | 6.00 |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 2 | 1 | 1 | -0.1774 | 0.0023 | 6.00 |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 2 | 1 | 1 | -0.1774 | 0.0023 | 6.00 |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0p04_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 2 | 1 | 1 | -0.1774 | 0.0023 | 6.00 |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0p04_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 2 | 1 | 1 | -0.1774 | 0.0023 | 6.00 |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 2 | 1 | 1 | -0.1774 | 0.0023 | 6.00 |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 2 | 1 | 1 | -0.1774 | 0.0023 | 6.00 |
| fpm_ism1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0p04_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 2 | 1 | 1 | -0.1774 | 0.0023 | 6.00 |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0p04_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 2 | 1 | 1 | -0.1815 | -0.0034 | 6.00 |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 2 | 1 | 1 | -0.1816 | -0.0037 | 6.00 |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 2 | 1 | 1 | -0.1816 | -0.0037 | 6.00 |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0p04_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 2 | 1 | 1 | -0.1816 | -0.0037 | 6.00 |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0_pl0p04_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 2 | 1 | 1 | -0.1816 | -0.0037 | 6.00 |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 2 | 1 | 1 | -0.1816 | -0.0037 | 6.00 |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0_ppm1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 2 | 1 | 1 | -0.1816 | -0.0037 | 6.00 |
| fpm_is1_p0p6_ly0p02_fpx0p03_fpg1_sma0p005_shp0p02_skp0_sap0_sbx0_sg0_vxg0p8_pl0p04_pp1_tvl2_plg0p2_pyg0p2_pms0p25_yg0p25_yvg0p2_rg1_vyg1_byg0p8 | 2 | 1 | 1 | -0.1817 | -0.0039 | 7.00 |

## Interpretation

- This is an offline finite-horizon teacher probe, not policy training.
- Raw traces are ignored by git; compact summaries and score artifacts should be committed.
- A useful candidate must still pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
