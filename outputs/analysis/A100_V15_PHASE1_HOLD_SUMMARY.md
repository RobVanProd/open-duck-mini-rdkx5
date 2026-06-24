# A100 V15 Phase-1 Hold Summary

Date: 2026-06-24

status: `HOLD_V15_PHASE1_LOW_FORWARD_PROGRESS`

## Command Shape

The Colab A100 session ran only phase 1 of `movement_bootstrap_v15`.

```text
platform: gpu
JAX_PLATFORM_NAME: gpu
JAX_PLATFORMS: cuda
recipe: movement_bootstrap_v15
phase: phase1_no_bridge_high_entropy_gait_discovery
num_timesteps: 320000
ppo_num_envs: 256
ppo_batch_size: 256
actuator bridge: disabled
command x range: 0.06 to 0.10
zero_command_probability: 0
alive_scale: 0
imitation_scale: 0
```

## Training Result

Training completed and exported a policy/checkpoint.

```text
status: PASS_SMOKE_RUN
returncode: 0
elapsed_s: 501.13
checkpoint steps: 112640, 225280, 337920
exported ONNX: 2026_06_24_100138_337920.onnx
```

Reward improved but stayed negative:

```text
STEP 0:      reward -191.5916
STEP 112640: reward -190.9590
STEP 225280: reward -128.0599
STEP 337920: reward -100.1721
```

## Phase Gate

The automatic vanilla `x=0.08` candidate gate held:

```text
overall_status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
samples: 250
termination: duration_complete
mean_local_vx: 0.0009 m/s
track_ratio: 0.0111
reward_mean: 0.5420
body_pitch_p95: 0.0818 rad
base_height_min: 0.1534 m
max_action_saturation_pct: 0.0000
max_pitch_tracking_p95_rad: 0.0540
max_sent_target_velocity_p95_rad_s: 0.0988
```

## Interpretation

V15 phase 1 learned a quiet, stable standstill rather than a forward gait. It did
not fail from actuator velocity, action saturation, or pitch collapse:

```text
target velocity p95: far below the 2.5 to 3.75 rad/s fitted actuator envelope
action saturation: 0%
body pitch/base height: healthy
forward tracking: effectively zero
```

This means the current no-bridge high-entropy discovery recipe still falls into
the standstill basin. Do not run phases 2 or 3 from this checkpoint.

## Artifact Notes

The workflow exit bundle originally missed staged phase outputs after the phase
gate raised `HOLD_PHASE_FREEZE_OR_LOW_PROGRESS`. A manual recovery archive was
created and downloaded from the A100 session:

```text
remote archive: /content/v15_phase1_recovery_minimal_20260624T101118Z.tar.gz
sha256: 1f4fcaf5eeb5e448502e89633ad47be1eacfee6ca96bc3df19802756f3b53345
local recovery dir:
outputs/analysis/colab_cli/open-duck-a100-staged-curriculum-20260624T095254Z/recovery/v15_phase1_recovery_minimal_20260624T101118Z
```

The Colab workflow has been patched so staged smoke outputs and phase-gate
summaries are copied during `atexit` artifact bundling, including failure exits.

Robot status: parked. No robot SSH, deployment, runtime behavior change, or
hardware test was performed.
