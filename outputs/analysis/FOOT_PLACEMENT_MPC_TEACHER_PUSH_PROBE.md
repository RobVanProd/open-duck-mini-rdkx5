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
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sap0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0150 | 0.0313 | 41.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0116 | 0.0263 | 39.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sap0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0095 | 0.0221 | 43.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0086 | 0.0325 | 58.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0086 | 0.0229 | 45.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sap0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0085 | 0.0292 | 60.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sapm0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0079 | 0.0187 | 49.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sapm0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0070 | 0.0197 | 51.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0053 | 0.0200 | 48.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0048 | 0.0234 | 59.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sapm0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0035 | 0.0168 | 51.00 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0035 | 0.0180 | 45.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sap0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0024 | 0.0141 | 56.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0009 | 0.0164 | 57.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p02_sapm0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | -0.0002 | 0.0079 | 45.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | -0.0004 | 0.0103 | 51.00 |

## Interpretation

- This is an offline finite-horizon teacher probe, not policy training.
- Raw traces are ignored by git; compact summaries and score artifacts should be committed.
- A useful candidate must still pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
