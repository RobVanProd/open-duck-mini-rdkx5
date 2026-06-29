# Phase 2 z=0.005 Support Local ROCm Hold

status: `HOLD_FULL_LOCAL_ROCM_COMPILE_NO_PROGRESS`

Date: `2026-06-29`

## Attempt

Workflow intent:

```text
phase2-z005-support
```

Local output directory:

```text
outputs/phase2_domain_randomization/stage_z005_support_local_rocm/smoke_20260629T162610Z_gpu
```

This records local ROCm attempts of the z=0.005 support-stability recipe while
no Colab/A100 session was visible. These used the Stage A2 restore checkpoint,
fitted corrected bridge, no pushes, rough terrain `z=0.005`, and the
support/backward-pitch stability terms documented in
`PHASE2_STAGEA2_GAIN099_Z005_SUPPORT_STABILITY_NEXT_RUN.md`.

## Attempt 1: gfx Override Failure

The first full-shape local attempt forced:

```text
HSA_OVERRIDE_GFX_VERSION=11.0.0
```

It failed before any PPO step or ONNX export:

```text
returncode: -6
status: HOLD_SMOKE_RUN
stderr: Check failed: Failed setting context: hipError_t(719)
```

No policy result was produced. This strongly suggests the gfx override is
harmful on this local 7900 XTX stack and should not be used for local runs.

## Attempt 2: No-Override Tiny Smoke

Without `HSA_OVERRIDE_GFX_VERSION`, a tiny same-recipe smoke passed:

```text
output_dir:
  outputs/phase2_domain_randomization/stage_z005_support_local_rocm_no_override_smoke/smoke_20260629T162805Z_gpu
status: PASS_SMOKE_RUN
step: 320
reward: 3.4303669929504395
returncode: 0
elapsed_s: 192.98
```

It produced an ONNX and a checkpoint, so basic local ROCm training startup is
usable when the gfx override is not forced.

## Attempt 3: No-Override Full Shape

A full-shape no-override local run was then started:

```text
output_dir:
  outputs/phase2_domain_randomization/stage_z005_support_local_rocm_no_override/smoke_20260629T163201Z_gpu
num_timesteps: 81920
ppo_num_envs: 64
```

It remained GPU-busy for more than 12 minutes but produced no checkpoint, no
TensorBoard event growth, and no stdout/stderr movement after startup. The
agent interrupted this owned process. No child process was left running, and
the terrain XML restored to the original hash:

```text
scene_rough_terrain_backlash.xml sha256:
  879768817f5ae5d2c01b5494f855686bb10d1ec444a404efeced8f5766574ffc
```

Treat this as a local full-shape ROCm compile/runtime practicality hold, not a
recipe result.

## Backend Check

Immediately after the gfx-override abort, a basic ROCm JAX arithmetic test
still passed:

```text
jax 0.8.2
backend gpu
devices [RocmDevice(id=0)]
sum(x*x) 357389824.0
```

So the failure is narrower than basic JAX GPU visibility.

## Next Action

Do not promote or gate anything from these local runs. Use the pinned
A100/Colab `phase2-z005-support` workflow when a visible session is available.
If local ROCm is used again, do not set `HSA_OVERRIDE_GFX_VERSION`; first find a
full-shape setting that reaches the first checkpoint in bounded time.
