# Command Pitch-RL 2.25 Restore Smoke

status: `PASS_RESTORE_SMOKE_WITH_ABSOLUTE_CHECKPOINT_PATH`

This was a tiny local CPU training-plumbing smoke. It did not deploy, SSH, run
robot tests, or produce a candidate policy for robot validation.

## Purpose

Verify that the PPO step-0 checkpoint from the command-conditioned
pitch-rate-limited BC run can be restored by the Open Duck Playground PPO
runner with the fitted actuator bridge active.

## First Attempt

```text
restore_checkpoint_path:
  outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint
status:
  HOLD_SMOKE_RUN
reason:
  Brax runner could not resolve the relative checkpoint path
error:
  ValueError: checkpoint path does not exist
```

The wrapper launches `runner.py` from the Playground context, so relative paths
must be treated as runner-context paths. For local restore runs, use an
absolute checkpoint path.

## Passing Attempt

```text
restore_checkpoint_path:
  /home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint
status:
  PASS_SMOKE_RUN
platform:
  cpu
num_timesteps:
  1024
ppo_num_envs:
  32
ppo_episode_length:
  128
fitted bridge:
  enabled
target_rate_scale:
  -0.001
actuator_tracking_scale:
  -0.01
zero_command_probability:
  0.25
```

The run completed one tiny update and saved a smoke checkpoint:

```text
STEP: 4096 reward: 33.37058639526367 reward_std: 22.846797943115234
Saving checkpoint:
  /home/lsd/robots/Open_Duck_Playground/outputs/analysis/cmd_pitch_rl_2p25_restore_smoke_abs/smoke_20260626T190637Z_cpu/2026_06_26_150718_4096
```

That smoke checkpoint is a transient plumbing artifact and is not promoted.
The useful result is that restore/fine-tune plumbing works when the checkpoint
path is absolute.

## Decision

Use this step-0 checkpoint for the next real GPU fine-tune:

```text
outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint
```

When launching through local smoke tooling, pass it as an absolute path. When
launching through Colab, use the path visible inside the Colab runtime after
the repo/checkpoint is uploaded.
