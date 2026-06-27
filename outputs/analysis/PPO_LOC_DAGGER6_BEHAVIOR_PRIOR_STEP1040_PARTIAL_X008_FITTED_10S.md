# PPO-Loc DAgger-6 Behavior-Prior Step-1040 Partial Gate

Offline CPU-only candidate check. This did not SSH, deploy, train further,
touch the robot, or modify runtime behavior.

## Context

A tiny PPO smoke was run from the PPO-compatible DAgger-6 step-0 checkpoint with
the DAgger-6 PPO-loc BC student enabled as a behavior prior:

```text
restore checkpoint: outputs/analysis/ppo_loc_dagger6_recovery_step0_checkpoint
behavior prior: outputs/analysis/ppo_loc_dagger6_recovery_student_candidate/candidate_mlp.npz
behavior prior scale: -0.05
behavior prior huber delta: 0.05
training steps: 1040
bridge: fitted actuator bridge during training
```

The smoke completed and exported a step-1040 ONNX under `/tmp`, but the
subsequent fitted-bridge seed sweep was interrupted before all eight seeds
completed. Treat this as a partial diagnostic only.

## Partial Gate

```text
artifact: outputs/analysis/ppo_loc_dagger6_behavior_prior_step1040_partial_x008_fitted_10s.json
command_x: 0.08
duration: 10 s
bridge: fitted
completed seeds: 0, 1, 2
partial: true
```

| seed | status | samples | mean vx | track ratio | base height min | max tracking p95 |
|---:|---|---:|---:|---:|---:|---:|
| 0 | HOLD_CANDIDATE_LOW_FORWARD_PROGRESS | 500 | 0.0122 | 0.1520 | 0.1536 | 0.2077 |
| 1 | HOLD_CANDIDATE_FALL_OR_TERMINATION | 29 | 0.0232 | 0.2898 | 0.0877 | 0.3221 |
| 2 | HOLD_CANDIDATE_LOW_FORWARD_PROGRESS | 500 | 0.0111 | 0.1388 | 0.1525 | 0.2038 |

## Interpretation

This partial result matches the same failure shape as the no-prior tiny PPO
fine-tune: low forward progress on duration-complete seeds and an early
collapse on seed 1. It does not justify another robot-side step and does not
promote the behavior-prior step-1040 ONNX as a candidate.

The behavior prior may still be useful in a longer or better-shaped PPO recipe,
but this small diagnostic does not show that `scale=-0.05` is enough to preserve
the walking manifold while improving recovery.
