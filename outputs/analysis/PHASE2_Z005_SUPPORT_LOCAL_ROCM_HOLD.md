# Phase 2 z=0.005 Support Local ROCm Hold

status: `HOLD_LOCAL_ROCM_CONTEXT_719`

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

This was a bounded local ROCm attempt of the z=0.005 support-stability recipe
while no Colab/A100 session was visible. It used the Stage A2 restore
checkpoint, fitted corrected bridge, no pushes, rough terrain `z=0.005`, and
the support/backward-pitch stability terms documented in
`PHASE2_STAGEA2_GAIN099_Z005_SUPPORT_STABILITY_NEXT_RUN.md`.

## Result

The run failed before any PPO step or ONNX export:

```text
returncode: -6
status: HOLD_SMOKE_RUN
stderr: Check failed: Failed setting context: hipError_t(719)
```

No policy result was produced. Treat this as a local ROCm/JAX/MJX runtime hold,
not as evidence for or against the Phase 2 recipe.

## Backend Check

Immediately after the abort, a basic ROCm JAX arithmetic test still passed:

```text
jax 0.8.2
backend gpu
devices [RocmDevice(id=0)]
sum(x*x) 357389824.0
```

So the failure is narrower than basic JAX GPU visibility. The local GPU can
initialize and execute a simple device computation, but the full Playground
training startup path failed while activating the ROCm context.

## Next Action

Do not promote or gate anything from this run. Use the pinned A100/Colab
`phase2-z005-support` workflow when a visible session is available, or debug the
local ROCm context path separately.
