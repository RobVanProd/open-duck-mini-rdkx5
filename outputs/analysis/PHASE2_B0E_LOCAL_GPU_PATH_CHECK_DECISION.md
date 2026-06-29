# Phase 2 B0E Local GPU Path Check

status: `PASS_B0E_GPU_1ENV_PLUMBING`

## Purpose

After the B0E 32-env and 16-env local ROCm attempts failed during evaluator
reset, a deliberately tiny 1-env GPU run was used to determine whether B0E was
completely broken on local ROCm or whether the failure was scale-dependent.

This was offline-only. No robot tests, SSH, deploy, grounded replay, runtime
behavior changes, or policy overwrite were performed.

## Configuration

```text
platform: gpu
JAX_PLATFORMS: rocm
task: rough_terrain_backlash
terrain hfield z scale: 0.002
envs: 1
timesteps: 20
episode_length: 20
export_min_step: 1
restore checkpoint:
  outputs/phase2_domain_randomization/stage_b0c_rough_z002_push_tracking_margin_from_b0_gpu/smoke_20260629T062042Z_gpu/2026_06_29_022725_245760
```

Recipe shape:

```text
actuator_tracking_scale: -0.015
restore_policy_kl_scale: 1.5
tracking_lin_vel_scale: 3.0
tracking_sigma: 0.01
forward_progress_scale: 2.5
command_progress_scale: 1.5
command_progress_shortfall_scale: -4.0
command_progress_required_ratio: 0.45
mild DR: enabled
mild pushes: enabled
corrected actuator bridge: enabled
```

## Result

```text
status: PASS_SMOKE_RUN
returncode: 0
elapsed_s: 172.0
reached PPO step: 100
reward: 1.9270
checkpoint:
  2026_06_29_044139_100
```

The terrain XML override was restored after the run:

```text
scene_rough_terrain_backlash.xml restored: true
restored sha256:
  879768817f5ae5d2c01b5494f855686bb10d1ec444a404efeced8f5766574ffc
```

## Evidence Hashes

```text
manifest:
  24551880b4250f742b23c5d762262e173d63c444c3f6db8a5635259b2d16eaa2

stderr:
  3c2b683c24e8aca15951c65d2b899d4daac7689e5593e4772b49195e4da9779c

stdout:
  b2b7e2593c15ac35fbfb54fa201d60325bce575ceae2b068d03476dd168b8c4d
```

## Decision

`PASS_B0E_GPU_1ENV_PLUMBING`

B0E is not universally broken on local ROCm. The 1-env path reaches PPO and
exports, while the 16-env and 32-env paths fail at `jax.jit(eval_env.reset)`
with `rocblas_status_internal_error`. The local blocker is therefore
scale-dependent ROCm evaluator reset, not B0E command wiring.

Do not promote the 1-env checkpoint or treat it as a policy result. The next
policy-producing path remains the pinned CUDA/A100 `phase2-b0e` workflow, or a
local ROCm retry only after a backend fix or a specifically bounded scale
matrix.
