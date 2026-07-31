# PPO Behavior-Prior A100 Fine-Tune Decision

status: `HOLD_BEHAVIOR_PRIOR_PPO_REJECTED_BY_CHECKPOINT_SWEEP`

## Summary

A conservative A100 PPO fine-tune was run from the command-conditioned DAgger
seed-5 x0 step-0 checkpoint with the DAgger MLP enabled as a behavior prior.
The run completed on CUDA/JAX and exported one ONNX checkpoint, but the compact
checkpoint-promotion sweep rejected it.

This was offline only. No robot tests, deploy, SSH, or runtime behavior changes
were performed.

## Recipe

```text
base checkpoint:
  outputs/analysis/ppo_bc_command_conditioned_dagger_seed5_x0_step0_checkpoint

behavior prior:
  outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate/candidate_mlp.npz

behavior prior scale:
  -0.2

PPO learning rate:
  0.00005

PPO clip epsilon:
  0.1

PPO entropy cost:
  0.001

PPO max grad norm:
  0.5

actuator bridge:
  enabled
```

## Training Result

```text
platform: A100 / CUDA / JAX 0.7.2
status: PASS_SMOKE_RUN
exported checkpoint: step 40960
step 0 reward: 10.2949
step 40960 reward: 14.1327
```

Artifact bundle:

```text
outputs/analysis/ppo_behavior_prior_a100_finetune/open_duck_behavior_prior_a100_artifacts.tar.gz
sha256: 6d0b7f768321612eb6964498e41cb7a5ad515f4b5858814c42c84c5312306c6d
```

## Promotion Sweep

The new checkpoint-promotion sweep was run for `x=0.0` and `x=0.08` with the
fitted actuator bridge:

```text
artifact: outputs/analysis/ppo_behavior_prior_a100_finetune/CHECKPOINT_SWEEP.md
status: HOLD_REJECT_CANDIDATE_CHECKPOINT
```

Per-command results:

```text
x=0.0:
  status: HOLD_CANDIDATE_ACTION_SATURATION
  samples: 50
  max pitch tracking p95: 0.3685 rad
  action saturation: 100%
  mean vx: -0.1194 m/s

x=0.08:
  status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
  samples: 50
  mean vx: 0.0109 m/s
  track ratio: 0.1362
  max pitch tracking p95: 0.2109 rad
  max pitch target velocity p95: 1.0248 rad/s
```

## Interpretation

The behavior prior and conservative PPO settings did not prevent the PPO update
from breaking the candidate gates. Compared with the PPO-only A100 run, the
result is still a reward-increasing but gate-failing policy.

Do not continue this exact behavior-prior PPO recipe. The next learning change
needs a stronger gate-aligned mechanism, such as:

```text
- selecting checkpoints by compact gate sweep during training, not reward
- constraining updates against action saturation explicitly
- using DAgger/rollout correction instead of PPO-only fine-tuning
- testing smaller or adaptive PPO updates before full A100 runs
```

Robot validation remains blocked.
