# Movement Bootstrap V15C A100 Reduced No-Sentinel Summary

status: `HOLD_REMOTE_NO_SENTINEL_REDUCED_PPO`

## Context

V15 phase 1 was relaunched on A100 with a reduced PPO configuration after V15B
proved the step-0 export guard was active but still disappeared after the first
eval callback:

```text
recipe: movement_bootstrap_v15
phase: phase1_no_bridge_high_entropy_gait_discovery
session: open-duck-a100-v15c
timesteps_scale: 0.25
ppo_num_envs: 64
ppo_batch_size: 64
ppo_num_minibatches: 2
ppo_num_updates_per_batch: 2
export_min_step: 1
robot_touched: false
```

The remote Colab session became idle without writing the workflow `.exit`
sentinel, a final manifest, a checkpoint, an ONNX export, or an artifact bundle.
The local poller did not terminate promptly even though the remote session was
idle, so the stale local poller and Colab session were stopped manually.

## Recovered Artifacts

Recovered local evidence:

```text
outputs/analysis/colab_cli/open-duck-a100-v15c-staged-curriculum-20260624T071940Z/remote_live.log
outputs/analysis/colab_cli/open-duck-a100-v15c-staged-curriculum-20260624T071940Z/REMOTE_PATHS.txt
outputs/analysis/colab_cli/open-duck-a100-v15c-staged-curriculum-20260624T071940Z/console_start.log
```

No ONNX, checkpoint, final manifest, stdout/stderr artifact copy, or packaged
artifact bundle was produced.

## Log Finding

The captured remote log reached the reduced phase-1 runner command:

```text
JAX_PLATFORM_NAME=gpu /usr/bin/python3 /content/Open_Duck_Playground/playground/open_duck_mini_v2/runner.py ... --num_timesteps 80000 --ppo_num_envs 64 --ppo_batch_size 64 --ppo_num_minibatches 2 --ppo_num_updates_per_batch 2 ...
```

Unlike V15B, the captured log does not show a `STEP: 0` reward line. The last
local `remote_live.log` timestamp was `2026-06-24 03:23:45` local time, and the
Colab session later reported `IDLE`.

## Interpretation

The reduced A100 run shows the no-sentinel failure is not only the step-0 ONNX
export handoff and not only the original larger PPO batch/env configuration.
This is now an A100/Colab/JAX training-infrastructure hold, not evidence about
V15 policy quality.

Do not spend more full A100 time on V15 until the cloud training process can
survive a tiny known-good PPO smoke. The next useful offline step is to isolate
the A100 training path with a minimal runner smoke or use a different backend
for the next recipe iteration.

Robot validation remains blocked.
