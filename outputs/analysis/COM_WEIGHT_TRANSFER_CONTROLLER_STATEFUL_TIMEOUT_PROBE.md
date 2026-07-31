# CoM Weight-Transfer Controller Probe

status: `PASS_COM_CONTROLLER_PROBE_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0, 2]`
candidate_count: `32`

## Limitations

- controller uses base_y or stance-foot-relative base_y as lateral CoM proxies
- controller can optionally use stance-foot-relative sagittal position as a push term
- body_roll and true center-of-mass projection are not yet modeled
- stance-foot-relative mode uses contact phase's stance foot site y, not a true CoM projection

## Top Controller Candidates

| controller | runs | falls | duration_complete | mean_vx | max_seed_vx | push_allowed_mean |
|---|---:|---:|---:|---:|---:|---:|
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p2_lo0p03_byg0p05_lvg0p12_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0p01_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0010 | 0.0012 | 1.33 |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0010 | 0.0010 | 0.67 |
| com_lrstance_foot_relative_p0p56_lf0p45_uf0p3_lo0p03_byg0p035_lvg0p12_so0_kpy3_kdy0p5_kpx1_kpvx1_ffp0p015_sap0p01_sk0p12_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0011 | 0.0008 | 0.67 |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p3_lo0p03_byg0p035_lvg0p08_som0p02_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0011 | 0.0010 | 0.33 |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p03_byg0p035_lvg0p12_so0_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0_sk0p12_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0012 | 0.0008 | 0.33 |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p03_byg0p05_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0p01_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0013 | 0.0007 | 1.00 |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p03_byg0p05_lvg0p08_so0_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p015_sap0_sk0p08_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0013 | 0.0006 | 1.00 |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p05_lvg0p12_so0_kpy3_kdy0p5_kpx0_kpvx1_ffp0p015_sap0p01_sk0p08_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0014 | 0.0005 | 1.00 |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p02_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0018 | 0.0007 | 0.67 |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p03_byg0p05_lvg0p08_so0_kpy4_kdy0p5_kpx0_kpvx1_ffp0p015_sap0p01_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0018 | 0.0010 | 1.67 |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p3_lo0p02_byg0p05_lvg0p12_so0_kpy4_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0_sk0p12_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0018 | 0.0010 | 0.67 |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p02_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0p01_sk0p08_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0018 | 0.0007 | 0.33 |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p03_byg0p035_lvg0p08_so0_kpy4_kdy0p5_kpx0_kpvx1_ffp0p005_sap0_sk0p12_sa0_shr0p04_srs0p5_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0018 | 0.0008 | 0.00 |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p03_byg0p035_lvg0p08_so0_kpy4_kdy0p5_kpx1_kpvx1_ffp0p005_sap0p01_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0018 | 0.0008 | 0.00 |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p03_byg0p035_lvg0p08_som0p02_kpy4_kdy0p5_kpx0_kpvx0p5_ffp0p015_sap0p01_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0018 | 0.0008 | 0.00 |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p2_lo0p02_byg0p05_lvg0p12_so0_kpy3_kdy0p5_kpx0_kpvx0p5_ffp0p015_sap0_sk0p12_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0018 | 0.0007 | 0.33 |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p03_byg0p035_lvg0p12_som0p02_kpy4_kdy0p5_kpx1_kpvx1_ffp0p005_sap0p01_sk0p12_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0019 | 0.0008 | 0.00 |
| com_lrstance_foot_relative_p0p64_lf0p35_uf0p2_lo0p03_byg0p035_lvg0p12_so0_kpy4_kdy0p5_kpx0_kpvx0p5_ffp0p005_sap0_sk0p12_sa0_shr0p06_srs0p5_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0019 | 0.0008 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p02_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx1_kpvx0p5_ffp0p005_sap0p01_sk0p08_sa0_shr0p06_srs0p3_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0019 | 0.0007 | 0.33 |
| com_lrstance_foot_relative_p0p64_lf0p45_uf0p3_lo0p02_byg0p035_lvg0p12_som0p02_kpy3_kdy0p5_kpx0_kpvx1_ffp0p005_sap0_sk0p08_sa0_shr0p04_srs0p3_gs1_sf1_pt0_pd1 | 2 | 0 | 2 | -0.0019 | 0.0007 | 0.33 |

## Interpretation

- This is a closed-loop controller probe, not policy training.
- Raw traces are ignored by git; compact summaries and scoring artifacts should be committed.
- A useful controller still must pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
- A hold should identify which state transition failed before any training branch starts.
