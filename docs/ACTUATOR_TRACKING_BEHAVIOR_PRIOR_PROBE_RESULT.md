# Actuator Tracking Behavior Prior Probe Result

Date: 2026-06-27

Status: `HOLD_REJECT_CANDIDATE_CHECKPOINT`

This was an offline A100 candidate-only run. No robot test, SSH, deploy, or
runtime behavior change was performed.

## Run

The run used the command-conditioned DAgger seed-5/x=0 student as a behavior
prior and restored from the PPO-compatible step-0 checkpoint:

```text
candidate_name: actuator_tracking_behavior_prior_probe
num_timesteps: 32768
restore_checkpoint: outputs/analysis/ppo_bc_command_conditioned_dagger_seed5_x0_step0_checkpoint
behavior_prior: outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate/candidate_mlp.npz
behavior_prior_scale: -0.2
actuator_tracking_scale: -0.01
target_rate_scale: -0.001
```

The A100 training run completed:

```text
status: PASS_SMOKE_RUN
elapsed_s: 540.15
step 0 reward: 16.7091
step 40960 reward: 20.6604
latest ONNX sha256: 0a8359c826449e14ddd887e5136e2650ab02a92a8de280f92c1a9e7be532464a
```

## Sweep Result

The remote Colab sweep wedged in a GPU eval worker after training completed, so
the exported ONNX checkpoints were swept locally on CPU with the same compact
gate:

```text
commands: 0.0, 0.08
duration: 1.0 s
bridge: fitted
```

| checkpoint | x | status | max pitch vel p95 | max tracking p95 | track ratio | mean vx |
|---|---:|---|---:|---:|---:|---:|
| step 0 | 0.00 | `HOLD_CANDIDATE_TRACKING` | 1.4147 | 0.1904 | NA | 0.0042 |
| step 0 | 0.08 | `HOLD_CANDIDATE_TRACKING` | 1.9323 | 0.2233 | 0.2692 | 0.0215 |
| step 40960 | 0.00 | `HOLD_CANDIDATE_TRACKING` | 0.6348 | 0.1970 | NA | 0.0104 |
| step 40960 | 0.08 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 1.2288 | 0.2182 | 0.1043 | 0.0083 |

## Interpretation

The actuator-tracking behavior-prior PPO probe did not produce a robot
candidate.

The step-0 checkpoint still had the only meaningful compact x=0.08 forward
motion, but it failed the tracking gate. The trained step-40960 checkpoint
reduced target velocity and increased reward, but it also reduced forward
progress. This repeats the now-established failure pattern: PPO reward can
improve while the deployability gates regress.

Next training work should not be another small scalar reward tweak. It needs a
stronger deployable-policy mechanism such as teacher-action continuity during
PPO, rollout correction from the working selector, or a gate-aligned objective
that directly preserves forward progress while reducing tracking error.

## Workflow Follow-Up

The Colab workflow now defaults post-training checkpoint selection sweeps to CPU
through `--candidate-checkpoint-sweep-jax-platform cpu`. This keeps PPO training
on GPU while avoiding the A100 MJX eval-worker wedge observed in this run.
