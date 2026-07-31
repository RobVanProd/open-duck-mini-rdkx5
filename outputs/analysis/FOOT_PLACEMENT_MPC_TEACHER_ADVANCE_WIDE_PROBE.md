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
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0080 | 0.0139 | 46.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0080 | 0.0093 | 42.00 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0077 | 0.0123 | 41.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0076 | 0.0104 | 43.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0065 | 0.0108 | 46.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0064 | 0.0111 | 39.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0051 | 0.0112 | 41.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0043 | 0.0070 | 46.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0042 | 0.0086 | 39.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sap0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0034 | 0.0084 | 35.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0022 | 0.0029 | 44.00 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 2 | 0 | 2 | 0.0015 | 0.0045 | 44.00 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0011 | 0.0036 | 46.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 2 | 1 | 1 | -0.0527 | 0.0095 | 47.31 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg0p5_byg0p5 | 2 | 1 | 1 | -0.0672 | 0.0072 | 51.46 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0p04_skpm0p04_sapm0p04_rg1p5_vyg1_byg0p5 | 2 | 1 | 1 | -0.0764 | -0.0002 | 36.35 |

## Interpretation

- This is an offline finite-horizon teacher probe, not policy training.
- Raw traces are ignored by git; compact summaries and score artifacts should be committed.
- A useful candidate must still pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
