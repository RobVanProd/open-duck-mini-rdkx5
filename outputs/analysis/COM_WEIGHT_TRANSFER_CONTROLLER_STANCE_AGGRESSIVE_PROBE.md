# CoM Weight-Transfer Controller Probe

status: `PASS_COM_CONTROLLER_PROBE_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0, 2]`
candidate_count: `24`

## Limitations

- controller uses base_y or stance-foot-relative base_y as lateral CoM proxies
- body_roll and stance-foot-relative sagittal position are not yet modeled
- stance-foot-relative mode uses contact phase's stance foot site y, not a true CoM projection

## Top Controller Candidates

| controller | runs | falls | duration_complete | mean_vx | max_seed_vx | push_allowed_mean |
|---|---:|---:|---:|---:|---:|---:|
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p03_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0023 | 0.0041 | 3.33 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx2_ffp0p03_sk0p1_sa0_shr0p1_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0022 | 0.0039 | 0.33 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p04_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0022 | 0.0039 | 2.67 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p04_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0021 | 0.0039 | 3.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx2_ffp0p04_sk0p1_sa0_shr0p1_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0021 | 0.0036 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p02_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0019 | 0.0035 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p12_kpy1_kdy0p2_kpvx2_ffp0p02_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0019 | 0.0035 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx2_ffp0p04_sk0p1_sa0_shr0p08_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0019 | 0.0035 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p02_sk0p1_sa0_shr0p1_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0019 | 0.0036 | 0.67 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx2_ffp0p04_sk0p1_sa0_shr0p1_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0018 | 0.0036 | 1.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_kpy2_kdy0p2_kpvx2_ffp0p04_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0017 | 0.0033 | 0.67 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p02_byg0p03_lvg0p12_kpy2_kdy0p2_kpvx2_ffp0p03_sk0p1_sa0_shr0p08_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0015 | 0.0033 | 3.33 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx2_ffp0p04_sk0p08_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0014 | 0.0029 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p04_sk0p08_sa0_shr0p1_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0014 | 0.0029 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p01_byg0p03_lvg0p12_kpy1_kdy0p2_kpvx2_ffp0p03_sk0p08_sa0_shr0p1_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0014 | 0.0029 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvx1_ffp0p02_sk0p08_sa0_shr0p1_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0014 | 0.0029 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx2_ffp0p04_sk0p08_sa0_shr0p1_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0012 | 0.0031 | 1.67 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p2_kpvx2_ffp0p02_sk0p08_sa0_shr0p08_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0011 | 0.0029 | 1.67 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p25_lo0p02_byg0p03_lvg0p12_kpy2_kdy0p2_kpvx1_ffp0p03_sk0p08_sa0_shr0p08_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0010 | 0.0026 | 2.33 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_kpy2_kdy0p2_kpvx2_ffp0p04_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0009 | 0.0026 | 0.33 |

## Interpretation

- This is a closed-loop controller probe, not policy training.
- Raw traces are ignored by git; compact summaries and scoring artifacts should be committed.
- A useful controller still must pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
- A hold should identify which state transition failed before any training branch starts.
