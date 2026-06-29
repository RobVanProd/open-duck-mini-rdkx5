# Phase 2 B0D Local GPU Scale Hold

status: `HOLD_LOCAL_ROCM_SCALE`

## Purpose

Scale the B0D rough-terrain corrected-bridge continuation beyond the tiny
8-env recovery smoke on the local RX 7900 XTX.

This was offline sim training only. It did not touch the robot.

## Input

- restore checkpoint:
  `outputs/phase2_domain_randomization/stage_b0c_rough_z002_push_tracking_margin_from_b0_gpu/smoke_20260629T062042Z_gpu/2026_06_29_022725_245760`
- platform: `gpu`
- JAX platform: `rocm`
- device verified before run: `rocm:0 AMD Radeon RX 7900 XTX`
- timesteps: `40960`
- envs: `64`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.002`
- corrected actuator bridge enabled
- actuator tracking scale: `-0.04`
- actuator tracking Huber delta: `0.03`
- restore-policy KL: `1.0`
- behavior prior enabled, scale `-0.35`

## Result

Output:

`outputs/phase2_domain_randomization/stage_b0d_tracking_margin_local_gpu_scale/smoke_20260629T075435Z_gpu`

Observed:

- status: `HOLD_SMOKE_RUN`
- return code: `-6`
- elapsed: `47.89 s`
- PPO steps: `0`
- checkpoints: none
- terrain override restored to original hash
- robot_touched: `false`

Failure excerpt:

```text
Failed setting context: ROCM_ERROR_ILLEGAL_ADDRESS
```

The stdout reached env construction and printed the expected `101` observation
contract before failing inside ROCm/JAX execution.

## Interpretation

The local ROCm backend is healthy enough for discovery and a tiny 8-env B0D
smoke, but it is not stable at the 64-env B0D scale used here. This is an
infrastructure/runtime hold, not a policy result.

B0D remains untested as a meaningful training recipe. The next valid full
training attempt should use a CUDA/A100 Colab session, or a smaller local
scale ladder if the workstation backend is being debugged deliberately.

## Decision

`HOLD_LOCAL_ROCM_SCALE`

Do not promote any output from this run. No robot test, SSH, deploy, grounded
replay, or robot runtime behavior change was performed.
