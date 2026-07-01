# Foot-Placement MPC Teacher Probe

status: `PASS_FOOT_PLACEMENT_MPC_PROBE_RAN`
command_x: `0.0`
duration_s: `2.0`
seeds: `[5]`
terrain_override: `{'enabled': True, 'hfield_z_scale': 0.002, 'source_xml': '/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_rough_terrain_backlash.xml', 'temp_xml': '/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/.codex_eval_72f2qwf1_hfield_z0.002.xml'}`
candidate_count: `1`

## Limitations

- first implementation uses joint-space approximations for swing-foot placement
- not a full nonlinear MPC solver
- passing still requires external 100-150 tick score artifacts

## Top Candidates

| candidate | runs | falls | complete | mean_vx | max_seed_vx | push_allowed_mean |
|---|---:|---:|---:|---:|---:|---:|
| fpm_is1_p0p56_ly0_fpx0_fpg0_sma0_shp0_skp0_sap0_sbx0_sg0_vxg0_pl0_pp1_tvl2_plg10_pyg10_pms0_yg0_yvg0_rg0_vyg0_byg0 | 1 | 1 | 0 | -0.3643 | -0.3643 | 44.19 |

## Interpretation

- This is an offline finite-horizon teacher probe, not policy training.
- Raw traces are ignored by git; compact summaries and score artifacts should be committed.
- A useful candidate must still pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
