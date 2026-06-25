# Closed-Loop Weight-Transfer Teacher Probe

status: `PASS_TEACHER_PROBE_RAN`
command_x: `0.04`
duration_s: `3.0`
seeds: `[0, 2]`
candidate_count: `3`

## Top Teacher Candidates

| teacher | runs | falls | duration_complete | mean_vx | max_seed_vx |
|---|---:|---:|---:|---:|---:|
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_ssps0p5_mfs0p25_ffp0p01_pt0_pd1_lgm1_bygm1_plg0p06_clb1 | 2 | 0 | 2 | 0.0112 | 0.0121 |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_ssps0_mfs0p25_ffp0p01_pt0_pd1_lgm1_bygm1_plg0p06_clb1 | 2 | 0 | 2 | 0.0108 | 0.0115 |
| teacher_ssm1_p0p56_rs0p02_sk0p08_sa0_shr0p06_srs0p5_spg1_ssps1_mfs0p25_ffp0p01_pt0_pd1_lgm1_bygm1_plg0p06_clb1 | 2 | 0 | 2 | 0.0091 | 0.0098 |

## Interpretation

- This is a closed-loop teacher probe, not policy training.
- Raw traces are ignored by git; compact summaries and scoring artifacts should be committed.
- A useful teacher still must pass `tools/score_target_candidates_objective.py` over 100-150 tick windows.
