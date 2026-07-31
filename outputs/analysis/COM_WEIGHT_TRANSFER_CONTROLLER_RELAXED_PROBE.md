# CoM Weight-Transfer Controller Probe

status: `PASS_COM_CONTROLLER_PROBE_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0, 2]`
candidate_count: `12`

## Limitations

- first implementation uses base_y/local_vy/contact as CoM proxies
- body_roll and stance-foot-relative base position are not yet modeled

## Top Controller Candidates

| controller | runs | falls | duration_complete | mean_vx | max_seed_vx | push_allowed_mean |
|---|---:|---:|---:|---:|---:|---:|
| com_p0p56_lf0p3_uf0p2_lo0p03_byg0p04_lvg0p12_kpy2_kdy0p2_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0025 | 0.0046 | 2.67 |
| com_p0p56_lf0p3_uf0p2_lo0p03_byg0p04_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0025 | 0.0046 | 2.67 |
| com_p0p56_lf0p3_uf0p2_lo0p03_byg0p03_lvg0p12_kpy2_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0024 | 0.0050 | 2.00 |
| com_p0p56_lf0p3_uf0p2_lo0p03_byg0p04_lvg0p12_kpy2_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0024 | 0.0048 | 3.67 |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p04_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0023 | 0.0043 | 1.33 |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p04_lvg0p1_kpy2_kdy0p2_kpvx1_ffp0p02_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0022 | 0.0041 | 1.33 |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy2_kdy0p2_kpvx1_ffp0p02_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0022 | 0.0041 | 1.33 |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p04_lvg0p12_kpy2_kdy0p5_kpvx1_ffp0p02_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0018 | 0.0032 | 2.00 |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p12_kpy2_kdy0p5_kpvx1_ffp0p02_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0018 | 0.0032 | 2.00 |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy2_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0017 | 0.0031 | 1.33 |
| com_p0p56_lf0p3_uf0p2_lo0p03_byg0p03_lvg0p12_kpy1_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0013 | 0.0028 | 0.33 |
| com_p0p56_lf0p3_uf0p2_lo0p02_byg0p03_lvg0p1_kpy1_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0010 | 0.0020 | 1.00 |

## Interpretation

- This is a closed-loop controller probe, not policy training.
- Raw traces are ignored by git; compact summaries and scoring artifacts should be committed.
- A useful controller still must pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
- A hold should identify which state transition failed before any training branch starts.
