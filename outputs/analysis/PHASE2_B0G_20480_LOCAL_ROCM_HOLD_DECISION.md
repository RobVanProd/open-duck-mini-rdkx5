# Phase 2 B0G 20480 Local ROCm Hold

status: `HOLD_B0G_20480_TRACKING_REGRESSION`

## Scope

This was an offline local ROCm sim/training and CPU gate run only. No robot
tests, SSH, deploy, grounded replay, runtime behavior changes, or policy
overwrite were performed.

## Backend Result

The local RX 7900 XTX path completed a bounded B0G smoke run with the new
push-recovery left-knee tracking hook enabled:

```text
jax: 0.8.2
backend: rocm / gpu
device: RX 7900 XTX gfx1100
env:
  XLA_PYTHON_CLIENT_PREALLOCATE=false
  XLA_PYTHON_CLIENT_MEM_FRACTION=0.50
  XLA_FLAGS=--xla_gpu_autotune_level=0
```

Training run:

```text
run_dir:
  outputs/phase2_domain_randomization/stage_b0g_push_recovery_local_rocm_smoke/smoke_20260629T130541Z_gpu

status: PASS_SMOKE_RUN
returncode: 0
elapsed_s: 204.94
ppo_num_envs: 32
ppo_episode_length: 100
ppo step: 20480
```

Exported ONNX:

```text
outputs/phase2_domain_randomization/stage_b0g_push_recovery_local_rocm_smoke/smoke_20260629T130541Z_gpu/2026_06_29_090758_20480.onnx
sha256: 70fde5e93cfe7252ef14d8c953e9015051cde1747806f24adf2274f022491473
```

This is useful backend evidence: the local 7900 XTX can run the B0G hook at
small 32-env scale without the previous immediate ROCm evaluator-reset failure.
It is not comparable to the pinned A100/JAX 0.7.2 training stack and is not a
policy promotion by itself.

## Recipe

B0G started from the B0C rough-terrain restore checkpoint and used the new
localized push-recovery cost instead of global actuator tracking:

```text
restore checkpoint:
  outputs/phase2_domain_randomization/stage_b0c_rough_z002_push_tracking_margin_from_b0_gpu/smoke_20260629T062042Z_gpu/2026_06_29_022725_245760

global actuator_tracking_scale: 0.0
push_recovery_actuator_tracking_scale: -0.02
push_recovery_actuator_tracking_huber_delta: 0.03
push_recovery_tracking_window_steps: 25
push_recovery_tracking_joint_indices: 3
terrain_hfield_z_scale: 0.002
push magnitude: 0.05-0.10
push interval: 1.0-1.5 s
```

## Gate

The exported checkpoint was evaluated on CPU for correctness:

```text
gate:
  rough_terrain_backlash
  terrain_hfield_z_scale: 0.002
  corrected fitted bridge
  command_x: 0.08
  duration: 5 s
  seeds: 0-7
  gentle pushes: enabled
```

Result:

```text
PASS_CANDIDATE_SIM_GATE: 4/8
HOLD_CANDIDATE_TRACKING: 4/8
falls: 0/8
duration_complete: 8/8
mean track ratio: 0.4423
mean vx: 0.0354 m/s
max tracking p95: 0.2046 rad
mean tracking p95: 0.2011 rad
max velocity excess: 0.0000 rad/s
mean push recovery success: 0.9062
```

Per-seed tracking holds:

```text
seed 0: tracking p95 0.2031 rad
seed 2: tracking p95 0.2036 rad
seed 4: tracking p95 0.2013 rad
seed 5: tracking p95 0.2046 rad
```

Seed 4, the original B0C `lk097` localized miss, remains essentially
unchanged:

```text
B0C lk097 seed 4: 0.2013 rad
B0G 20480 seed 4: 0.2013 rad
```

## Decision

Do not promote B0G `20480`. Do not replace the B0C `lk097` near-pass line with
this checkpoint. The local B0G smoke proves the new hook can train/step on the
7900 XTX at small scale, but the resulting checkpoint regresses the 8-seed
rough-terrain gentle-push gate from the previous 7/8 near-pass to 4/8.

The next policy-producing attempt should still use the named A100
`phase2-b0g` workflow when a visible Colab/A100 session exists, or a longer
local ROCm run only after accepting that the local stack is JAX 0.8.2 and not
directly comparable to the pinned A100 path. Any next B0G run must be judged by
the corrected-bridge 8-seed gate, not by training reward.

Robot validation remains blocked.
