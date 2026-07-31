# Policy vs Behavior Prior

status: `PASS_POLICY_TEACHER_CLOSE`

Offline comparison only. No training, SSH, deploy, robot test, or runtime
behavior change was performed.

## Inputs

- manifest: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_manifest.json`
- behavior prior NPZ: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz`
- samples: `10322`

## Policy Summary

| policy | teacher L1 mean | teacher L1 p95 | manifest L1 p95 | action abs p95 | saturation % |
|---|---:|---:|---:|---:|---:|
| `candidate` | 0.0000 | 0.0000 | 0.0402 | 0.7491 | 0.00 |
| `2026_07_11_021243_81920` | 0.0252 | 0.0641 | 0.0751 | 0.7708 | 0.00 |
| `2026_07_11_021603_163840` | 0.0170 | 0.0482 | 0.0663 | 0.7548 | 0.00 |
| `2026_07_11_021632_245760` | 0.0167 | 0.0469 | 0.0663 | 0.7518 | 0.00 |

## Interpretation

The compared policies remain close to the behavior-prior teacher on the teacher dataset; gate regression is more likely closed-loop instability than offline teacher mismatch.
