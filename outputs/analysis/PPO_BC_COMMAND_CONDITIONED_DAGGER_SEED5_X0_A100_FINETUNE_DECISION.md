# PPO BC Command-Conditioned DAgger Seed-5 x0 A100 Fine-Tune Decision

status: `HOLD_PPO_WARMSTART_FINETUNE_REGRESSED`

## Summary

The A100 PPO fine-tune restored the command-conditioned DAgger seed-5 x0
step-0 checkpoint successfully and trained without a CUDA runtime failure.
The run exported ONNX checkpoints at steps `30720`, `61440`, and `92160`.

The fine-tuned checkpoints are not robot candidates. The final checkpoint
collapses into low forward progress at `x=0.08` and also breaks the repaired
`x=0.0` hard seed.

## Inputs

```text
base checkpoint:
  outputs/analysis/ppo_bc_command_conditioned_dagger_seed5_x0_step0_checkpoint

base ONNX:
  outputs/analysis/ppo_bc_command_conditioned_dagger_seed5_x0_step0.onnx

A100 final ONNX:
  outputs/analysis/ppo_bc_command_conditioned_dagger_seed5_x0_a100_finetune/2026_06_27_082546_92160.onnx

artifact bundle:
  outputs/analysis/ppo_bc_command_conditioned_dagger_seed5_x0_a100_finetune/open_duck_warmstart_a100_artifacts.tar.gz
```

Artifact bundle SHA256:

```text
48cece5bcb8be8d32b92fbeb8040f2c65ccebec1e5c166cb763497f4df39db0c
```

## A100 Training Result

```text
JAX: 0.7.2
backend: CUDA
device: NVIDIA A100-SXM4-40GB
status: PASS_SMOKE_RUN
restore checkpoint: PASS
robot touched: false
deploy performed: false
```

Training reward increased:

```text
step 0:     10.5533
step 30720: 13.7810
step 61440: 14.0193
step 92160: 16.2665
```

However, the exported ONNX samples in the training stdout were visibly
saturated to `-1` / `+1`, and fitted-bridge candidate gates rejected the
result.

## Colab Gate Caveat

The Colab per-seed gates in the artifact bundle all report:

```text
HOLD_ENV_INSTANTIATION_TIMEOUT
```

Those are not model-quality results. The Colab script did not pass
`--sim-preflight-timeout-s`, so each gate timed out during the 90 second
Playground contract preflight before a rollout was produced.

Local CPU re-gates with a longer preflight were used for the decision below.

## Local Gate Checks

Final checkpoint, `x=0.08`, seed 0, fitted bridge:

```text
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
duration: 10 s
mean vx: 0.0011 m/s
track ratio: 0.0138
max pitch tracking p95: 0.0794 rad
max sent target velocity p95: 0.6377 rad/s
base height min: 0.1536 m
action saturation: 0%
```

Final checkpoint, `x=0.0`, seed 5, fitted bridge:

```text
status: HOLD_CANDIDATE_FALL_OR_TERMINATION
samples: 37
termination: fall_or_nan
mean vx: -0.2623 m/s
base height min: 0.0501 m
max pitch tracking p95: 0.4952 rad
action saturation: 100%
```

Earliest PPO export, step `30720`, `x=0.08`, seed 0, fitted bridge:

```text
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
duration: 10 s
mean vx: 0.0009 m/s
track ratio: 0.0112
max pitch tracking p95: 0.0613 rad
max sent target velocity p95: 0.3091 rad/s
action saturation: 0%
```

## Interpretation

The restore path and A100 CUDA stack are usable, but this PPO recipe quickly
destroys the useful forward behavior. The failure is not a runtime crash and
not a checkpoint-format problem. It is an objective/optimization failure:
reward increased while candidate gate behavior regressed into standstill and
hard-seed instability.

Do not continue this exact PPO recipe.

## Next Recommendation

Use the selector/DAgger evidence to build a better warm-start or training
objective before running another large GPU job:

```text
- preserve x=0 seed-5 stability as an explicit gate during training
- evaluate exported checkpoints before selecting the final reward checkpoint
- add candidate-gate metrics into the training selection loop
- avoid reward-only checkpoint choice when ONNX actions saturate
- consider behavior-prior / DAgger-style rollout correction before PPO
```

No robot tests, deploy, SSH, or runtime behavior changes were performed.
