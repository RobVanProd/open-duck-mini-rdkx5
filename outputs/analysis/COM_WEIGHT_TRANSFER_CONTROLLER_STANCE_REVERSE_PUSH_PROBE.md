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
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p2_kpvxm2_ffpm0p02_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0020 | 0.0036 | 2.67 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvxm2_ffpm0p04_sk0p1_sa0_shr0p1_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0019 | 0.0038 | 2.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy1_kdy0p2_kpvxm2_ffpm0p02_sk0p1_sa0_shr0p1_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0019 | 0.0038 | 2.67 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy2_kdy0p2_kpvxm1_ffpm0p02_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0019 | 0.0038 | 0.33 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy2_kdy0p2_kpvxm1_ffpm0p02_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0017 | 0.0029 | 4.33 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy1_kdy0p2_kpvxm2_ffpm0p03_sk0p1_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0016 | 0.0037 | 2.33 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy1_kdy0p2_kpvxm2_ffpm0p04_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0016 | 0.0036 | 1.67 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvxm1_ffpm0p04_sk0p08_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0014 | 0.0029 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_kpy1_kdy0p2_kpvxm1_ffpm0p03_sk0p08_sa0_shr0p1_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0014 | 0.0029 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvxm2_ffpm0p04_sk0p1_sa0_shr0p08_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0014 | 0.0035 | 1.67 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy1_kdy0p2_kpvxm1_ffpm0p02_sk0p08_sa0_shr0p08_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0013 | 0.0027 | 0.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy2_kdy0p2_kpvxm2_ffpm0p03_sk0p08_sa0_shr0p08_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0012 | 0.0029 | 1.33 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p1_kpy2_kdy0p2_kpvxm1_ffpm0p03_sk0p1_sa0_shr0p08_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0009 | 0.0027 | 0.33 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvxm1_ffpm0p04_sk0p08_sa0_shr0p08_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0008 | 0.0028 | 1.00 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p2_kpvxm2_ffpm0p03_sk0p08_sa0_shr0p08_srs0p3_pt0_pd1 | 2 | 0 | 2 | 0.0008 | 0.0027 | 1.33 |
| com_lrstance_foot_relative_p0p56_lf0p3_uf0p2_lo0p01_byg0p03_lvg0p12_kpy2_kdy0p2_kpvxm2_ffpm0p04_sk0p08_sa0_shr0p08_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0001 | 0.0018 | 0.00 |

## Interpretation

- This is a closed-loop controller probe, not policy training.
- Raw traces are ignored by git; compact summaries and scoring artifacts should be committed.
- A useful controller still must pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
- A hold should identify which state transition failed before any training branch starts.
