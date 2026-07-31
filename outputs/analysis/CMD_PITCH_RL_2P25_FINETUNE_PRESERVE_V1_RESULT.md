# Commanded Pitch-Rate Warm Start PPO Fine-Tune Preserve V1

status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
generated_at: `2026-06-26T20:55:00Z`

## Summary

The conservative A100 Colab fine-tune successfully restored
`ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint`, trained with the fitted
actuator bridge active, exported ONNX checkpoints, and ran the configured
x=0.0 and x=0.08 fitted-bridge gates.

This was a preservation-oriented PPO attempt: lower learning rate, smaller PPO
clip, one update per batch, lower target-rate/tracking penalties, and a shorter
run than the first full fine-tune. It still regressed the x=0.08 walking
behavior into near standstill.

## Training

```text
workflow: candidate-only
platform: A100 / CUDA
jax: 0.7.2
playground task: flat_terrain
restore checkpoint: outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint
timesteps exported: 92160
status: PASS_SMOKE_RUN
latest ONNX sha256: f0219ae8f2e292c4f343fef5f48518fc8529cc1843c40ecf1cf044dc54f53267
```

Preservation settings:

```text
learning_rate: 3e-5
clipping_epsilon: 0.05
max_grad_norm: 0.2
ppo_num_updates_per_batch: 1
target_rate_scale: -0.0005
actuator_tracking_scale: -0.005
forward_progress_scale: 6
forward_shortfall_scale: -3
action_rate_scale: -0.005
action_magnitude_scale: -0.005
stand_still_scale: -0.2
zero_command_probability: 0.25
command_x_range: 0.04 to 0.08
```

Reward checkpoints:

```text
step 0:     reward 27.8232
step 30720: reward 33.3058
step 61440: reward 31.8035
step 92160: reward 36.0918
```

## Gates

### x=0.0

```text
status: PASS_CANDIDATE_SIM_GATE
max action saturation: 0.0%
max pitch tracking p95: 0.0613 rad
max sent target velocity p95: 0.2732 rad/s
mean fitted local vx: 0.0005 m/s
```

### x=0.08

```text
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
max action saturation: 0.0%
max pitch tracking p95: 0.0763 rad
max sent target velocity p95: 0.4493 rad/s
mean fitted local vx: 0.0004 m/s
fitted command tracking ratio: 0.0045
stress command tracking ratio: 0.0018
```

The conservative fine-tuned policy is stable and actuator-safe, but effectively
stationary at x=0.08. It regressed from the step-0 warm start, which moved at
about `0.0347 m/s` with track ratio `0.4343`.

## Interpretation

This run rules out a simple "PPO was too aggressive" explanation for the first
fine-tune failure. Even with conservative PPO updates, the current reward path
can improve reported training reward while erasing the warm-start forward gait.

The next useful training change is not another scalar learning-rate or clip
tweak. The fine-tune needs an explicit behavior-preservation mechanism, such as
a teacher-action regularizer or state-conditioned behavior-prior term, so early
PPO updates cannot replace the source-VX walking behavior with low-rate
standstill before learning a better fitted-bridge controller.

No robot tests, SSH, deployment, runtime behavior changes, or policy deployment
were performed.
