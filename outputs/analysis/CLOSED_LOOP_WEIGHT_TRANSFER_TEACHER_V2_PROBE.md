# Closed-Loop Weight-Transfer Teacher Probe

status: `PASS_TEACHER_PROBE_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0, 2]`
candidate_count: `32`

## Top Teacher Candidates

| teacher | runs | falls | duration_complete | mean_vx | max_seed_vx |
|---|---:|---:|---:|---:|---:|
| teacher_p0p48_rs0p02_sk0p16_sam0p02_spg1_pd1_lgm1_byg1_plg0p06_clb1 | 2 | 0 | 2 | 0.0305 | 0.0310 |
| teacher_p0p48_rs0_sk0p16_sa0_spg0p5_pd2_lgm0p5_bygm1_plg0p08_clb0p5 | 2 | 0 | 2 | 0.0286 | 0.0303 |
| teacher_p0p56_rs0p04_sk0p16_sa0_spg0p5_pd1_lgm0p5_byg1_plg0p06_clb0 | 2 | 0 | 2 | 0.0275 | 0.0299 |
| teacher_p0p56_rs0_sk0p16_sa0p02_spg0p5_pd1_lgm0p5_bygm1_plg0p06_clb0p5 | 2 | 0 | 2 | 0.0245 | 0.0271 |
| teacher_p0p56_rs0_sk0p16_sam0p02_spg0p5_pd2_lg1_bygm1_plg0p08_clb0p5 | 2 | 0 | 2 | 0.0226 | 0.0232 |
| teacher_p0p56_rs0_sk0p16_sa0_spg0p5_pd1_lg1_byg0p5_plg0p06_clb0 | 2 | 0 | 2 | 0.0221 | 0.0252 |
| teacher_p0p56_rs0p04_sk0p16_sam0p02_spg1_pd1_lgm1_bygm0p5_plg0p12_clb1 | 2 | 0 | 2 | 0.0219 | 0.0242 |
| teacher_p0p48_rs0p02_sk0p12_sa0p02_spg1_pd2_lgm1_byg0_plg0p12_clb0p5 | 2 | 0 | 2 | 0.0218 | 0.0219 |
| teacher_p0p48_rs0p02_sk0p12_sa0p02_spg1_pd1_lgm0p5_bygm0p5_plg0p12_clb1 | 2 | 0 | 2 | 0.0211 | 0.0224 |
| teacher_p0p56_rs0p04_sk0p16_sam0p02_spg0p5_pd2_lgm1_bygm1_plg0p08_clb1 | 2 | 0 | 2 | 0.0199 | 0.0237 |
| teacher_p0p64_rs0p02_sk0p16_sa0p02_spg1_pd1_lgm0p5_byg1_plg0p08_clb0 | 2 | 0 | 2 | 0.0197 | 0.0209 |
| teacher_p0p48_rs0p02_sk0p12_sam0p02_spg0p5_pd2_lg0p5_bygm0p5_plg0p06_clb1 | 2 | 0 | 2 | 0.0187 | 0.0196 |
| teacher_p0p56_rs0p02_sk0p16_sam0p02_spg1_pd2_lg1_bygm1_plg0p12_clb0 | 2 | 0 | 2 | 0.0182 | 0.0186 |
| teacher_p0p56_rs0p02_sk0p12_sam0p02_spg0p5_pd1_lg0_bygm0p5_plg0p06_clb1 | 2 | 0 | 2 | 0.0168 | 0.0176 |
| teacher_p0p48_rs0p02_sk0p12_sa0p02_spg0p5_pd2_lg0_byg0p5_plg0p08_clb0 | 2 | 0 | 2 | 0.0139 | 0.0147 |
| teacher_p0p56_rs0p02_sk0p12_sa0p02_spg1_pd1_lg0p5_byg0p5_plg0p12_clb0p5 | 2 | 0 | 2 | 0.0137 | 0.0193 |
| teacher_p0p64_rs0p04_sk0p16_sam0p02_spg0p5_pd1_lg0_bygm0p5_plg0p08_clb0 | 2 | 0 | 2 | 0.0130 | 0.0157 |
| teacher_p0p64_rs0p02_sk0p16_sam0p02_spg1p5_pd2_lg0p5_byg1_plg0p12_clb0p5 | 2 | 0 | 2 | 0.0118 | 0.0158 |
| teacher_p0p64_rs0p02_sk0p12_sa0p02_spg1_pd2_lg0p5_bygm0p5_plg0p06_clb0p5 | 2 | 0 | 2 | 0.0115 | 0.0140 |
| teacher_p0p56_rs0_sk0p08_sa0p02_spg1p5_pd1_lg1_bygm0p5_plg0p06_clb1 | 2 | 0 | 2 | 0.0114 | 0.0129 |

## Interpretation

- This is a closed-loop teacher probe, not policy training.
- Raw traces are ignored by git; compact summaries and scoring artifacts should be committed.
- A useful teacher still must pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
