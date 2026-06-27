# Phase B Checkpoint Sweep Summary

Generated: `2026-06-22T18:30Z`

## Status

Selected archived `verify_scratch/odm_phase_b` ONNX checkpoints were evaluated
offline on a Colab NVIDIA L4 CUDA backend with the closed-loop actuator bridge
candidate gate at `x=0.08`.

Result: **no selected checkpoint is ready for robot validation**.

All selected checkpoints were actuator-safe but failed the nonzero-command
forward-progress gate. No robot tests, SSH, deploy, runtime changes, policy
overwrites, or training were performed.

## Evidence Location

Raw Colab artifacts are intentionally kept out of git:

```text
outputs/analysis/colab_cli/phase_b_eval_20260622T173551Z/final/
```

The final ignored bundle is:

```text
outputs/analysis/colab_cli/phase_b_eval_20260622T173551Z/final/phase_b_checkpoint_sweep_20260622T173551Z_artifacts.tar.gz
```

## Environment

- backend: Colab NVIDIA L4 / CUDA
- JAX: `0.7.2`
- JAX device: `cuda:0`
- MuJoCo: `3.9.0`
- MuJoCo MJX: `3.9.0`
- Playground package: `0.0.5`
- Playground repo commit: `d4d0a11`
- contract audit: `PASS`, `obs[1,101] -> actions[1,14]`

## `x=0.08` Candidate Gate

| policy | status | min track ratio | max pitch p95 rad | max target vel p95 rad/s | max action sat % | min height m | min reward | fitted vx m/s | stress vx m/s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `2026_06_02_175758_983040.onnx` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `-0.0082` | `0.0652` | `0.1919` | `0.0000` | `0.1527` | `0.5368` | `-0.0007` | `-0.0005` |
| `2026_06_02_175858_1474560.onnx` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `-0.0095` | `0.0787` | `0.2603` | `0.0000` | `0.1516` | `0.5344` | `-0.0008` | `-0.0007` |
| `2026_06_02_175919_1638400.onnx` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `-0.0100` | `0.0837` | `0.2893` | `0.0000` | `0.1514` | `0.5326` | `-0.0008` | `-0.0008` |
| `2026_06_02_180000_1966080.onnx` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `-0.0109` | `0.0902` | `0.3293` | `0.0000` | `0.1509` | `0.5233` | `-0.0009` | `-0.0009` |
| `2026_06_02_180020_2129920.onnx` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | `-0.0097` | `0.0976` | `0.3731` | `0.0000` | `0.1508` | `0.5197` | `-0.0008` | `-0.0007` |

## Interpretation

The selected archived policies are smooth and actuator-safe under the fitted
bridge, but they behave like near-standstill policies for a nonzero
`x=0.08` command. The failure is not target saturation, body collapse, or
actuator overload; it is lack of forward command tracking.

This matches the recent 50k and 300k candidate-training attempts: reducing
target dynamics without strengthening the locomotion objective tends to produce
stable standing rather than trackable forward walking.

## Next Decision

Do not run these policies on the robot.

Next offline work should change the training objective/curriculum before
launching another candidate:

- strengthen nonzero forward-progress reward or lower the tolerance/sigma that
  lets near-zero velocity score well at `x=0.08`
- evaluate command curriculum distribution so the policy cannot satisfy the
  training run mostly by standing
- keep actuator-delay/velocity-limit/randomized-lag bridge active
- keep target-rate/action-rate penalties, but avoid making smooth standing the
  easiest optimum
- continue to require `x=0.08` candidate gates to pass forward command tracking
  before any robot validation
