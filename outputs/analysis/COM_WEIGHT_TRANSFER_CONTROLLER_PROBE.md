# CoM Weight-Transfer Controller Probe

status: `PASS_COM_CONTROLLER_PROBE_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0, 2]`
candidate_count: `16`

## Limitations

- first implementation uses base_y/local_vy/contact as CoM proxies
- body_roll and stance-foot-relative base position are not yet modeled

## Top Controller Candidates

| controller | runs | falls | duration_complete | mean_vx | max_seed_vx | push_allowed_mean |
|---|---:|---:|---:|---:|---:|---:|
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx0p5_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0022 | 0.0045 | 0.67 |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0022 | 0.0044 | 0.67 |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0022 | 0.0044 | 0.67 |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0022 | 0.0044 | 0.67 |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0015 | 0.0030 | 0.00 |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx0p5_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0015 | 0.0030 | 0.00 |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0015 | 0.0030 | 0.00 |
| com_p0p56_lf0p35_uf0p25_lo0p02_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0015 | 0.0030 | 0.00 |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx0p5_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0011 | 0.0020 | 0.33 |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0011 | 0.0020 | 0.33 |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0011 | 0.0020 | 0.33 |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0011 | 0.0022 | 0.00 |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx1_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0011 | 0.0022 | 0.00 |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx0p5_ffp0p005_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0011 | 0.0022 | 0.00 |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy2_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0011 | 0.0022 | 0.00 |
| com_p0p56_lf0p35_uf0p25_lo0p01_byg0p02_lvg0p08_kpy3_kdy0p5_kpvx0p5_ffp0p01_sk0p08_sa0_shr0p06_srs0p5_pt0_pd1 | 2 | 0 | 2 | 0.0011 | 0.0019 | 0.33 |

## Interpretation

- This is a closed-loop controller probe, not policy training.
- Raw traces are ignored by git; compact summaries and scoring artifacts should be committed.
- A useful controller still must pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
- A hold should identify which state transition failed before any training branch starts.
