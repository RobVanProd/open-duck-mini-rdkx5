# Policy vs Behavior Prior

status: `WARN_POLICY_TEACHER_DIVERGENCE`

Offline comparison only. No training, SSH, deploy, robot test, or runtime
behavior change was performed.

## Inputs

- manifest: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_manifest.json`
- behavior prior NPZ: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate/candidate_mlp.npz`
- samples: `10322`

## Policy Summary

| policy | teacher L1 mean | teacher L1 p95 | manifest L1 p95 | action abs p95 | saturation % |
|---|---:|---:|---:|---:|---:|
| `candidate` | 0.0000 | 0.0000 | 0.0242 | 0.7510 | 0.00 |
| `2026_06_27_102952_0` | 0.0000 | 0.0000 | 0.0242 | 0.7510 | 0.00 |
| `2026_06_27_103207_40960` | 0.0414 | 0.1409 | 0.1438 | 0.7321 | 0.00 |

## Interpretation

At least one policy has a large p95 action difference from the behavior-prior teacher on the teacher dataset. If that policy also regresses gate behavior, the PPO update is not preserving the deployable behavior prior.
