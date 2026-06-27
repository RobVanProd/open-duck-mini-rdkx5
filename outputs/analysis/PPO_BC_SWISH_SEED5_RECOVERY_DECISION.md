# PPO BC Swish Seed-5 Recovery Decision

status: `HOLD_SEED5_RECOVERY_TRACE_RELABEL_INSUFFICIENT`

Do not start PPO from the seed-5 recovery warm-start; the targeted relabel did not remove the seed-5 reverse/fall mode.

## Artifacts

- relabel: `outputs/analysis/PPO_SWISH_SEED5_RELABEL_BLEND.md`
- manifest: `outputs/analysis/PPO_SWISH_SEED5_RECOVERY_MANIFEST.md`
- bc_fit: `outputs/analysis/PPO_LOC_SWISH_SEED5_RECOVERY_BC_STUDENT.md`
- export_fidelity: `outputs/analysis/PPO_BC_SWISH_SEED5_RECOVERY_STEP0_EXPORT_FIDELITY.md`
- gate: `outputs/analysis/PPO_BC_SWISH_SEED5_RECOVERY_STEP0_VALIDATION_FITTED_BACKLASH.md`
- seed5_trace: `outputs/analysis/PPO_BC_SWISH_SEED5_RECOVERY_TRACE_GATE.md`
- seed5_analysis: `outputs/analysis/PPO_BC_SWISH_SEED5_RECOVERY_FAILURE_ANALYSIS.md`

## Recovery Dataset

- entries: `26`
- samples: `9342`
- added relabeled seed-5 samples: `74`

## BC Fit

- samples: `9342`
- MAE: `0.011601`
- p95 abs error: `0.035147`
- max abs error: `0.266879`
- target-rate p95: `2.2326` rad/s
- target-rate max: `4.3247` rad/s

## Gate Comparison

| metric | prior swish step0 | seed-5 recovery step0 |
|---|---:|---:|
| falls | 1 / 8 | 1 / 8 |
| duration complete | 7 / 8 | 7 / 8 |
| mean vx | 0.0115 | 0.0120 |
| mean track ratio | 0.1441 | 0.1496 |
| min samples | 74 | 75 |
| max pitch velocity p95 mean | 3.7281 | 3.9029 |
| max tracking p95 mean | 0.2659 | 0.2733 |

## Seed 5 Before/After

| metric | before | after |
|---|---:|---:|
| samples | 74 | 75 |
| mean vx | -0.1976 | -0.1893 |
| min vx | -1.4579 | -1.5043 |
| base height min | 0.0717 | 0.0777 |
| final pitch | -1.4801 | -1.4773 |
| target velocity p95 | 1.7630 | 1.8172 |
| joint tracking p95 | 0.1760 | 0.1679 |
| double support pct | 75.6757% | 80.0000% |
| nearest distance p95 | 1.0276 | 0.6022 |
| nearest action L1 p95 | 0.0783 | 0.0409 |

## Interpretation

- The 74 relabeled seed-5 samples improved nearest-manifest distance but did not change the closed-loop failure mode.
- Seed 5 remains a reverse/fall basin with low target velocity, comparable tracking, high double support, and backward pitch collapse.
- Because the gate still has 1/8 falls and tracking holds, this checkpoint is not a valid PPO start point under the current stop rule.
- The next recovery branch needs stronger closed-loop recovery data or loss shaping around reverse velocity, backward pitch, and double-support collapse; simple one-trace relabeling is insufficient.

## Stop Rule

Do not start PPO from this checkpoint. The next valid step is a stronger seed-5 recovery dataset or loss branch, followed by another step-0 8-seed fitted gate.
