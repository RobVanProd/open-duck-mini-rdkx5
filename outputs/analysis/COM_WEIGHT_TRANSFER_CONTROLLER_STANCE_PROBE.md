# CoM Weight-Transfer Controller Probe

status: `PASS_COM_CONTROLLER_PROBE_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0, 2]`
candidate_count: `16`

## Limitations

- controller uses base_y or stance-foot-relative base_y as lateral CoM proxies
- body_roll and stance-foot-relative sagittal position are not yet modeled
- stance-foot-relative mode uses contact phase's stance foot site y, not a true CoM projection

## Top Controller Candidates

| controller | runs | falls | duration_complete | mean_vx | max_seed_vx | push_allowed_mean |
|---|---:|---:|---:|---:|---:|---:|
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0016 | 0.0033 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p03_byg0p02_lvg0p08_kpy2_kdy0p2_kpvx0p5_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0015 | 0.0030 | 0.33 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p03_byg0p02_lvg0p1_kpy2_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0014 | 0.0031 | 0.33 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p08_kpy2_kdy0p2_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0013 | 0.0030 | 2.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p02_lvg0p1_kpy1_kdy0p5_kpvx0p5_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0012 | 0.0027 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p03_byg0p02_lvg0p1_kpy2_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0012 | 0.0029 | 1.33 |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p03_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0012 | 0.0029 | 0.67 |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p01_byg0p02_lvg0p08_kpy1_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0011 | 0.0029 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p02_byg0p02_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0010 | 0.0031 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0010 | 0.0031 | 0.33 |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p1_kpy1_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0010 | 0.0026 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p1_kpy2_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0009 | 0.0021 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0003 | 0.0018 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | -0.0001 | 0.0011 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p2_lo0p01_byg0p02_lvg0p1_kpy2_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | -0.0001 | 0.0011 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p35_uf0p25_lo0p01_byg0p03_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | -0.0001 | 0.0011 | 0.00 |

## Interpretation

- This is a closed-loop controller probe, not policy training.
- Raw traces are ignored by git; compact summaries and scoring artifacts should be committed.
- A useful controller still must pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
- A hold should identify which state transition failed before any training branch starts.
