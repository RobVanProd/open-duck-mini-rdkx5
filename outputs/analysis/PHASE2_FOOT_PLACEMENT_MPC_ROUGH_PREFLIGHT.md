# Foot-Placement MPC Teacher Probe

status: `PASS_FOOT_PLACEMENT_MPC_PROBE_RAN`
command_x: `0.08`
duration_s: `3.0`
seeds: `[2, 4]`
candidate_count: `2`

## Limitations

- first implementation uses joint-space approximations for swing-foot placement
- not a full nonlinear MPC solver
- passing still requires external 100-150 tick score artifacts

## Top Candidates

| candidate | runs | falls | complete | mean_vx | max_seed_vx | push_allowed_mean |
|---|---:|---:|---:|---:|---:|---:|
| fpm_ism1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p005_shp0p02_skp0_sap0p02_sbx0_sg0_vxg0_pl0_pp1_tvl2p5_plg0p1_pyg0p1_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0054 | 0.0079 | 9.33 |
| fpm_is1_p0p56_ly0p025_fpx0p03_fpg1p2_sma0p005_shp0p02_skp0_sap0p02_sbx0_sg0_vxg0_pl0_pp1_tvl2p5_plg0p1_pyg0p1_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 1 | 1 | -0.0735 | -0.0010 | 14.98 |

## Interpretation

- This is an offline finite-horizon teacher probe, not policy training.
- Raw traces are ignored by git; compact summaries and score artifacts should be committed.
- A useful candidate must still pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
