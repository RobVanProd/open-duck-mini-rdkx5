# CoM Weight-Transfer Controller Probe

status: `PASS_COM_CONTROLLER_PROBE_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0, 2]`
candidate_count: `24`

## Limitations

- controller uses base_y or stance-foot-relative base_y as lateral CoM proxies
- controller can optionally use stance-foot-relative sagittal position as a push term
- body_roll and true center-of-mass projection are not yet modeled
- stance-foot-relative mode uses contact phase's stance foot site y, not a true CoM projection

## Top Controller Candidates

| controller | runs | falls | duration_complete | mean_vx | max_seed_vx | push_allowed_mean |
|---|---:|---:|---:|---:|---:|---:|
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p02_kpy2_kdy0p2_kpx1_kpvx2_ffp0p02_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0024 | 0.0045 | 3.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p04_kpy2_kdy0p2_kpx2_kpvx1_ffp0p03_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0024 | 0.0045 | 3.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0_kpy2_kdy0p2_kpx2_kpvx2_ffp0p03_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0024 | 0.0045 | 3.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p04_kpy2_kdy0p2_kpx2_kpvx2_ffp0p03_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0020 | 0.0035 | 2.67 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_so0p02_kpy2_kdy0p2_kpx1_kpvx1_ffp0p03_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0020 | 0.0035 | 2.67 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_so0_kpy2_kdy0p2_kpx1_kpvx1_ffp0p02_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0020 | 0.0035 | 2.67 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_so0p02_kpy2_kdy0p2_kpx2_kpvx1_ffp0p02_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0020 | 0.0035 | 2.67 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p04_kpy2_kdy0p2_kpx0_kpvx2_ffp0p02_sap0_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0020 | 0.0035 | 3.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_so0p02_kpy2_kdy0p2_kpx0_kpvx1_ffp0p03_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0019 | 0.0036 | 0.33 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_so0p02_kpy2_kdy0p2_kpx2_kpvx2_ffp0p02_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0018 | 0.0035 | 0.33 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_so0p02_kpy2_kdy0p2_kpx2_kpvx1_ffp0p02_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0018 | 0.0035 | 0.33 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_so0p02_kpy1_kdy0p2_kpx1_kpvx2_ffp0p02_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0017 | 0.0032 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_so0p02_kpy1_kdy0p2_kpx0_kpvx2_ffp0p02_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0017 | 0.0032 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_so0p04_kpy1_kdy0p2_kpx0_kpvx1_ffp0p02_sapm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0017 | 0.0032 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_so0p04_kpy1_kdy0p2_kpx1_kpvx1_ffp0p02_sap0_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0017 | 0.0032 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_so0_kpy1_kdy0p2_kpx0_kpvx1_ffp0p03_sap0_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0017 | 0.0032 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_so0_kpy2_kdy0p2_kpx1_kpvx1_ffp0p02_sap0_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0017 | 0.0033 | 0.67 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_so0_kpy1_kdy0p2_kpx2_kpvx1_ffp0p03_sap0_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0012 | 0.0029 | 1.67 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_so0p04_kpy1_kdy0p2_kpx2_kpvx1_ffp0p02_sap0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0012 | 0.0029 | 2.33 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_so0p04_kpy1_kdy0p2_kpx0_kpvx1_ffp0p02_sap0_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0012 | 0.0028 | 1.00 |

## Interpretation

- This is a closed-loop controller probe, not policy training.
- Raw traces are ignored by git; compact summaries and scoring artifacts should be committed.
- A useful controller still must pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
- A hold should identify which state transition failed before any training branch starts.
