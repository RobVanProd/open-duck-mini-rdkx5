# Commanded Pitch-Rate Warm Start PPO Fine-Tune V1

status: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`
generated_at: `2026-06-26T19:49:41Z`

## Summary

The A100 Colab run successfully restored the
`ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint`, trained with the fitted
actuator bridge active for `215040` PPO timesteps, exported ONNX checkpoints,
and ran the configured x=0.0 and x=0.08 fitted-bridge gates.

The result is not robot-ready. The x=0.0 gate passed, but the x=0.08 gate held
because forward progress collapsed to near standstill.

## Training

```text
workflow: candidate-only
platform: A100 / CUDA
jax: 0.7.2
playground task: flat_terrain
restore checkpoint: outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint
timesteps: 215040
status: PASS_SMOKE_RUN
latest ONNX sha256: 54d707b9c970dc389b7ad73af53cb436cc70cdb6d4fefe00d7da54c53ec09942
```

Reward checkpoints:

```text
step 0:      reward 25.9197
step 71680:  reward 31.2525
step 143360: reward 28.6910
step 215040: reward 33.7780
```

## Gates

### x=0.0

```text
status: PASS_CANDIDATE_SIM_GATE
max action saturation: 0.0%
max pitch tracking p95: 0.0701 rad
max sent target velocity p95: 0.1561 rad/s
mean local vx, fitted: 0.0011 m/s
```

### x=0.08

```text
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
max action saturation: 0.0%
max pitch tracking p95: 0.0859 rad
max sent target velocity p95: 0.2737 rad/s
min command tracking ratio: 0.0118
mean local vx, fitted: 0.0010 m/s
mean local vx, stress: 0.0009 m/s
```

The fine-tuned policy is actuator-safe but effectively stationary at x=0.08.
This is a regression from the step-0 warm start, which moved at about
`0.0347 m/s` with track ratio `0.4343`.

## Interpretation

This run shows that a straightforward PPO fine-tune from the deployable BC
warm start does not preserve the forward-motion behavior. The objective as
configured can improve or maintain reward while collapsing x=0.08 behavior into
low-rate standstill. More PPO steps with this exact recipe are not justified.

The next training attempt should keep an explicit forward-motion preservation
term or teacher-action regularizer during early fine-tuning, then relax it only
after the candidate demonstrates nonzero x=0.08 command tracking under the
fitted actuator bridge.

No robot tests, SSH, deployment, runtime behavior changes, or policy deployment
were performed.
