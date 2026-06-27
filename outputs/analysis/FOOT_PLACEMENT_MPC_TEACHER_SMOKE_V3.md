# Foot-Placement MPC Teacher Probe

status: `PASS_FOOT_PLACEMENT_MPC_PROBE_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0, 2]`
candidate_count: `8`

## Limitations

- first implementation uses joint-space approximations for swing-foot placement
- not a full nonlinear MPC solver
- passing still requires external 100-150 tick score artifacts

## Top Candidates

| candidate | runs | falls | complete | mean_vx | max_seed_vx | push_allowed_mean |
|---|---:|---:|---:|---:|---:|---:|
| fpm_is1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sap0p02_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0084 | 0.0161 | 35.67 |
| fpm_is1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sapm0p02_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0074 | 0.0148 | 32.33 |
| fpm_is1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sap0p02_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0065 | 0.0127 | 28.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sapm0p02_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0062 | 0.0148 | 34.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sap0p02_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0059 | 0.0138 | 26.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sapm0p02_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0056 | 0.0140 | 32.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sap0p02_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0047 | 0.0116 | 32.00 |
| fpm_is1_p0p56_ly0p015_fpx0p015_fpg0p8_shp0p02_skpm0p02_sapm0p02_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0047 | 0.0097 | 30.00 |

## Interpretation

- This is an offline finite-horizon teacher probe, not policy training.
- Raw traces are ignored by git; compact summaries and score artifacts should be committed.
- A useful candidate must still pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
