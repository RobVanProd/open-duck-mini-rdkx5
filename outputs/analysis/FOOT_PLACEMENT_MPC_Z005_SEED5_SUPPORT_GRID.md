# Foot-Placement MPC Teacher Probe

status: `PASS_FOOT_PLACEMENT_MPC_PROBE_RAN`
command_x: `0.0`
duration_s: `2.0`
seeds: `[5]`
terrain_override: `{'enabled': True, 'hfield_z_scale': 0.005, 'source_xml': '/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_rough_terrain_backlash.xml', 'temp_xml': '/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/.codex_eval_m9qvl818_hfield_z0.005.xml'}`
candidate_count: `24`

## Limitations

- first implementation uses joint-space approximations for swing-foot placement
- not a full nonlinear MPC solver
- passing still requires external 100-150 tick score artifacts

## Top Candidates

| candidate | runs | falls | complete | mean_vx | max_seed_vx | push_allowed_mean |
|---|---:|---:|---:|---:|---:|---:|
| fpm_is1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0_yvg0_rg0_vyg1_byg0p8 | 1 | 1 | 0 | -0.3424 | -0.3424 | 43.18 |
| fpm_ism1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0_yvg0_rg0_vyg1_byg0p8 | 1 | 1 | 0 | -0.3424 | -0.3424 | 40.91 |
| fpm_is1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0_yvg0_rg0_vyg1_byg0 | 1 | 1 | 0 | -0.3427 | -0.3427 | 44.44 |
| fpm_ism1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0_yvg0_rg0_vyg1_byg0 | 1 | 1 | 0 | -0.3427 | -0.3427 | 35.56 |
| fpm_is1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0_yvg0_rg1_vyg0_byg0 | 1 | 1 | 0 | -0.3474 | -0.3474 | 45.45 |
| fpm_ism1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0_yvg0_rg1_vyg0_byg0 | 1 | 1 | 0 | -0.3474 | -0.3474 | 0.00 |
| fpm_is1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0p4_yvg0_rg1_vyg0_byg0 | 1 | 1 | 0 | -0.3490 | -0.3490 | 46.51 |
| fpm_ism1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0p4_yvg0_rg1_vyg0_byg0 | 1 | 1 | 0 | -0.3490 | -0.3490 | 0.00 |
| fpm_is1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0p4_yvg0_rg0_vyg0_byg0p8 | 1 | 1 | 0 | -0.3494 | -0.3494 | 46.51 |
| fpm_ism1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0p4_yvg0_rg0_vyg0_byg0p8 | 1 | 1 | 0 | -0.3494 | -0.3494 | 0.00 |
| fpm_is1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0_yvg0_rg0_vyg0_byg0 | 1 | 1 | 0 | -0.3495 | -0.3495 | 45.45 |
| fpm_ism1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0_yvg0_rg0_vyg0_byg0 | 1 | 1 | 0 | -0.3495 | -0.3495 | 0.00 |
| fpm_is1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0_yvg0_rg0_vyg0_byg0p8 | 1 | 1 | 0 | -0.3506 | -0.3506 | 45.45 |
| fpm_ism1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0_yvg0_rg0_vyg0_byg0p8 | 1 | 1 | 0 | -0.3506 | -0.3506 | 0.00 |
| fpm_is1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0p4_yvg0_rg0_vyg1_byg0p8 | 1 | 1 | 0 | -0.3547 | -0.3547 | 41.86 |
| fpm_ism1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0p4_yvg0_rg0_vyg1_byg0p8 | 1 | 1 | 0 | -0.3547 | -0.3547 | 41.86 |
| fpm_is1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0p4_yvg0_rg1_vyg0_byg0p8 | 1 | 1 | 0 | -0.3593 | -0.3593 | 45.24 |
| fpm_ism1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0p4_yvg0_rg1_vyg0_byg0p8 | 1 | 1 | 0 | -0.3593 | -0.3593 | 0.00 |
| fpm_is1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0p4_yvg0_rg0_vyg0_byg0 | 1 | 1 | 0 | -0.3637 | -0.3637 | 44.19 |
| fpm_ism1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0p4_yvg0_rg0_vyg0_byg0 | 1 | 1 | 0 | -0.3637 | -0.3637 | 0.00 |

## Interpretation

- This is an offline finite-horizon teacher probe, not policy training.
- Raw traces are ignored by git; compact summaries and score artifacts should be committed.
- A useful candidate must still pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
