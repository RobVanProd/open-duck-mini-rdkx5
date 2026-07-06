# Phase 2 Stage A Rate175 Behavior-Prior CPU Smoke

status: `PASS_WIRING_SMOKE_NOT_PROMOTABLE`
generated_at: `2026-07-06T09:21:00Z`

Offline only. No robot, SSH, deploy, grounded replay, or runtime behavior change was performed.

## Purpose

This smoke run verifies that the corrected Phase 2 Stage A command path can restore from the true Phase 1 rate175 trainable checkpoint, keep the default PPO network shape, enable the behavior-prior continuity hook, and run on the corrected actuator bridge.

This is not a Phase 2 curriculum result. It is a tiny local CPU wiring check and is not promotable to full gates or hardware.

## Inputs

- task: `flat_terrain_backlash`
- platform: `cpu`
- timesteps: `320`
- PPO envs: `2`
- pushes: `disabled`
- corrected actuator bridge: `enabled`
- restore checkpoint: `outputs/analysis/ppo_bc_command_conditioned_rate175_step0_checkpoint`
- restore-policy KL scale: `4.0`
- behavior prior MLP: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz`
- behavior prior scale: `-0.6`
- behavior prior huber delta: `0.05`
- Phase 1 step-0 ONNX sha256: `432acd77dbd2d672516ddb886687661334da455c97bb0708541db8ff54a2bd61`
- behavior prior MLP sha256: `312f1ef0ba758af5fdeae900ce0a34dab659fe348a9f389988ddaaaa15659497`

## Result

- smoke status: `PASS_SMOKE_RUN`
- return code: `0`
- elapsed: `90.01s`
- output dir: `outputs/phase2_domain_randomization/stage_a_rate175_behavior_prior_cpu_smoke/smoke_20260706T091913Z_cpu`
- exported ONNX: `outputs/phase2_domain_randomization/stage_a_rate175_behavior_prior_cpu_smoke/smoke_20260706T091913Z_cpu/2026_07_06_052007_512.onnx`
- exported ONNX sha256: `f3f7f717ec29372220c0b1c73ce841eb777afd8f7b311eced0b2a564d6d75abb`
- final reward line: `STEP: 512 reward: 4.824737548828125 reward_std: 3.2537131309509277`

## Command Evidence

The runner stdout confirms:

- `Enabled restore-policy KL loss: scale=4.0`
- restore path: `outputs/analysis/ppo_bc_command_conditioned_rate175_step0_checkpoint`
- default PPO MLP export shape, not phase-modulated network args
- observation size: `101`
- action output shape: `(1, 14)`
- actuator order matches the Open Duck Mini v2 14-actuator contract

The manifest records:

- `JAX_PLATFORM_NAME=cpu`
- `JAX_PLATFORMS=cpu`
- `--no-push_enable`
- `--enable_behavior_prior`
- `--enable_actuator_bridge`
- actuator bridge delay fixed at `3` ticks
- actuator bridge velocity limit range `2.0..3.25 rad/s`

## Decision

`PASS_WIRING_SMOKE_NOT_PROMOTABLE`

The corrected Stage A rate175 behavior-prior command path is runnable. This unblocks the authoritative Colab/T4 Stage A run from the true Phase 1 warm-start, but it does not satisfy a Phase 2 gate and must not be promoted.

Next required step: run the valid Stage A GPU job from `ppo_bc_command_conditioned_rate175_step0_checkpoint`, then sweep exported checkpoints before any Stage B/C decision.
