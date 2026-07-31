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
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg0p2_pyg0p35_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0100 | 0.0150 | 32.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0098 | 0.0167 | 33.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0096 | 0.0145 | 33.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0094 | 0.0228 | 35.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0093 | 0.0166 | 29.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0092 | 0.0121 | 33.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg0p2_pyg0p35_pms0p6_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0092 | 0.0131 | 31.33 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg0p2_pyg0p35_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0092 | 0.0119 | 32.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0089 | 0.0140 | 32.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0087 | 0.0105 | 32.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0087 | 0.0136 | 29.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg0p2_pyg0p35_pms0p6_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0087 | 0.0118 | 29.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_ppm1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0085 | 0.0117 | 31.67 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0084 | 0.0136 | 30.33 |
| fpm_is1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg0p2_pyg0p35_pms0p4_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0083 | 0.0188 | 36.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_ppm1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0083 | 0.0162 | 33.00 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p03_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0080 | 0.0132 | 37.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p06_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvg0_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0080 | 0.0098 | 33.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p4_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0078 | 0.0130 | 36.67 |
| fpm_ism1_p0p56_ly0p015_fpx0p03_fpg1p2_sma0p04_shp0_skp0_sap0_sbx0p02_sg1p2_vxg1_pl0p05_pp1_plg0p2_pyg0p35_pms0p6_yg0_yvgm0p5_rg1p5_vyg1_byg0p5 | 2 | 0 | 2 | 0.0077 | 0.0162 | 33.33 |

## Interpretation

- This is an offline finite-horizon teacher probe, not policy training.
- Raw traces are ignored by git; compact summaries and score artifacts should be committed.
- A useful candidate must still pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
