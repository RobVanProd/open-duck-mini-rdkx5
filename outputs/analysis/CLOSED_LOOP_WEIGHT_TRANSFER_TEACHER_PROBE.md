# Closed-Loop Weight-Transfer Teacher Probe

status: `PASS_TEACHER_PROBE_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0, 2]`
candidate_count: `24`

## Top Teacher Candidates

| teacher | runs | falls | duration_complete | mean_vx | max_seed_vx |
|---|---:|---:|---:|---:|---:|
| teacher_p0p48_rs0p06_sk0p16_sam0p02_spg1_pd1_lg0_clb0 | 2 | 0 | 2 | 0.0232 | 0.0243 |
| teacher_p0p56_rs0p06_sk0p16_sa0_spg0p5_pd0_lg0p5_clb0p5 | 2 | 0 | 2 | 0.0221 | 0.0270 |
| teacher_p0p48_rs0p04_sk0p16_sam0p02_spg0p5_pd2_lg0p5_clb1 | 2 | 0 | 2 | 0.0209 | 0.0226 |
| teacher_p0p56_rs0p06_sk0p16_sam0p02_spg1p5_pd1_lg0_clb0 | 2 | 0 | 2 | 0.0200 | 0.0203 |
| teacher_p0p64_rs0p02_sk0p16_sa0p02_spg0p5_pd1_lg0_clb0 | 2 | 0 | 2 | 0.0172 | 0.0194 |
| teacher_p0p64_rs0p06_sk0p16_sa0p02_spg1p5_pd0_lg0p5_clb0 | 2 | 0 | 2 | 0.0171 | 0.0215 |
| teacher_p0p48_rs0p02_sk0p12_sa0_spg1p5_pd2_lg0p5_clb0p5 | 2 | 0 | 2 | 0.0157 | 0.0198 |
| teacher_p0p64_rs0p06_sk0p12_sa0p02_spg1_pd0_lg1_clb1 | 2 | 0 | 2 | 0.0141 | 0.0146 |
| teacher_p0p64_rs0p02_sk0p16_sam0p02_spg0p5_pd1_lg0_clb1 | 2 | 0 | 2 | 0.0133 | 0.0143 |
| teacher_p0p64_rs0p04_sk0p16_sa0_spg1p5_pd1_lg1_clb0 | 2 | 0 | 2 | 0.0128 | 0.0145 |
| teacher_p0p56_rs0p04_sk0p12_sa0_spg1_pd1_lg0p5_clb0p5 | 2 | 0 | 2 | 0.0112 | 0.0127 |
| teacher_p0p48_rs0p02_sk0p12_sa0_spg1_pd0_lg0_clb0 | 2 | 0 | 2 | 0.0101 | 0.0119 |
| teacher_p0p56_rs0p06_sk0p12_sam0p02_spg1_pd2_lg1_clb0 | 2 | 0 | 2 | 0.0089 | 0.0101 |
| teacher_p0p56_rs0p06_sk0p12_sa0_spg0p5_pd1_lg0p5_clb0 | 2 | 0 | 2 | 0.0089 | 0.0101 |
| teacher_p0p64_rs0p02_sk0p08_sa0p02_spg1p5_pd2_lg0p5_clb1 | 2 | 0 | 2 | 0.0065 | 0.0102 |
| teacher_p0p64_rs0p02_sk0p12_sa0p02_spg1p5_pd0_lg1_clb0 | 2 | 0 | 2 | 0.0065 | 0.0084 |
| teacher_p0p64_rs0p02_sk0p08_sa0p02_spg0p5_pd2_lg0p5_clb1 | 2 | 0 | 2 | 0.0063 | 0.0096 |
| teacher_p0p48_rs0p02_sk0p08_sa0p02_spg1p5_pd0_lg0_clb0p5 | 2 | 0 | 2 | 0.0061 | 0.0074 |
| teacher_p0p48_rs0p04_sk0p08_sa0p02_spg1p5_pd2_lg0p5_clb1 | 2 | 0 | 2 | 0.0060 | 0.0067 |
| teacher_p0p48_rs0p02_sk0p08_sa0_spg0p5_pd2_lg0p5_clb0p5 | 2 | 0 | 2 | 0.0051 | 0.0081 |

## Interpretation

- This is a closed-loop teacher probe, not policy training.
- Raw traces are ignored by git; compact summaries and scoring artifacts should be committed.
- A useful teacher still must pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
