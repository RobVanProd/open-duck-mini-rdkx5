# Closed-Loop Weight-Transfer Teacher Probe

status: `PASS_TEACHER_PROBE_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0, 2]`
candidate_count: `40`

## Top Teacher Candidates

| teacher | runs | falls | duration_complete | mean_vx | max_seed_vx |
|---|---:|---:|---:|---:|---:|
| teacher_p0p48_rs0p02_sk0p16_sa0_shr0p06_srs1_spg0p5_pt0_pd2_lgm0p5_byg0_plg0p08_clb0 | 2 | 0 | 2 | 0.0337 | 0.0377 |
| teacher_p0p48_rs0p02_sk0p16_sa0_shr0_srs1_spg1_pt0p03_pd2_lg0_byg1_plg0p12_clb0 | 2 | 0 | 2 | 0.0311 | 0.0324 |
| teacher_p0p48_rs0p02_sk0p12_sa0_shr0p06_srs1_spg1p5_pt0p03_pd1_lgm0p5_byg0p5_plg0p08_clb1 | 2 | 0 | 2 | 0.0285 | 0.0312 |
| teacher_p0p56_rs0_sk0p16_sa0p02_shr0_srs0_spg1_pt0p03_pd2_lg0_bygm1_plg0p12_clb1 | 2 | 0 | 2 | 0.0249 | 0.0289 |
| teacher_p0p56_rs0p02_sk0p16_sam0p02_shr0p06_srs1_spg1p5_pt0_pd2_lg0p5_byg0p5_plg0p12_clb0p5 | 2 | 0 | 2 | 0.0248 | 0.0296 |
| teacher_p0p56_rs0p04_sk0p12_sa0p02_shr0p06_srs0p5_spg0p5_ptm0p03_pd1_lgm1_byg0p5_plg0p12_clb1 | 2 | 0 | 2 | 0.0247 | 0.0258 |
| teacher_p0p48_rs0_sk0p16_sam0p02_shrm0p06_srs0p5_spg1_pt0p03_pd2_lgm0p5_bygm1_plg0p08_clb1 | 2 | 0 | 2 | 0.0240 | 0.0256 |
| teacher_p0p56_rs0p04_sk0p16_sam0p02_shr0_srs1_spg1_ptm0p03_pd2_lg1_bygm1_plg0p08_clb0p5 | 2 | 0 | 2 | 0.0232 | 0.0236 |
| teacher_p0p48_rs0p04_sk0p12_sa0p02_shr0p03_srs0_spg0p5_pt0p03_pd2_lg0p5_bygm0p5_plg0p06_clb1 | 2 | 0 | 2 | 0.0220 | 0.0266 |
| teacher_p0p64_rs0p04_sk0p16_sa0_shr0p03_srs1_spg1_pt0p06_pd1_lg1_bygm0p5_plg0p12_clb1 | 2 | 0 | 2 | 0.0193 | 0.0223 |
| teacher_p0p64_rs0p02_sk0p16_sa0_shr0_srs0_spg0p5_ptm0p03_pd2_lgm1_byg1_plg0p12_clb0p5 | 2 | 0 | 2 | 0.0178 | 0.0200 |
| teacher_p0p56_rs0p02_sk0p16_sam0p02_shr0_srs0_spg1_pt0_pd2_lg1_byg1_plg0p06_clb1 | 2 | 0 | 2 | 0.0175 | 0.0213 |
| teacher_p0p64_rs0p02_sk0p12_sa0_shr0p06_srs1_spg0p5_ptm0p03_pd2_lg1_bygm1_plg0p08_clb1 | 2 | 0 | 2 | 0.0172 | 0.0194 |
| teacher_p0p64_rs0_sk0p12_sam0p02_shrm0p06_srs0_spg1_pt0_pd1_lgm1_byg0_plg0p06_clb1 | 2 | 0 | 2 | 0.0168 | 0.0185 |
| teacher_p0p64_rs0p02_sk0p16_sam0p02_shrm0p03_srs0p5_spg0p5_pt0p06_pd1_lg0_byg1_plg0p08_clb0p5 | 2 | 0 | 2 | 0.0161 | 0.0185 |
| teacher_p0p48_rs0_sk0p12_sa0_shrm0p03_srs1_spg1p5_pt0p06_pd1_lg0_byg1_plg0p08_clb0p5 | 2 | 0 | 2 | 0.0161 | 0.0172 |
| teacher_p0p48_rs0_sk0p12_sa0_shrm0p03_srs0p5_spg0p5_pt0p03_pd2_lg0p5_bygm0p5_plg0p06_clb0p5 | 2 | 0 | 2 | 0.0159 | 0.0173 |
| teacher_p0p64_rs0_sk0p16_sam0p02_shr0_srs0p5_spg1_pt0_pd1_lgm0p5_byg0p5_plg0p08_clb1 | 2 | 0 | 2 | 0.0150 | 0.0171 |
| teacher_p0p56_rs0p04_sk0p12_sa0_shrm0p03_srs0p5_spg1p5_ptm0p03_pd2_lgm0p5_byg1_plg0p08_clb1 | 2 | 0 | 2 | 0.0146 | 0.0146 |
| teacher_p0p64_rs0_sk0p16_sam0p02_shr0_srs0_spg1_pt0p06_pd2_lgm1_byg0p5_plg0p08_clb1 | 2 | 0 | 2 | 0.0145 | 0.0164 |

## Interpretation

- This is a closed-loop teacher probe, not policy training.
- Raw traces are ignored by git; compact summaries and scoring artifacts should be committed.
- A useful teacher still must pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
