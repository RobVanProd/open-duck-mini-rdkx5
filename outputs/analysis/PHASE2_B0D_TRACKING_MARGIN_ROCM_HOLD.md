# Phase 2 B0D Tracking-Margin Continuation ROCm Hold

status: `HOLD_ROCM_RUNTIME`

## Purpose

Run a conservative B0D PPO continuation from the B0C final checkpoint to attack the
remaining corrected-bridge tracking margin directly in training rather than through
post-hoc ONNX action scaling.

## Recipe

- restore checkpoint:
  `outputs/phase2_domain_randomization/stage_b0c_rough_z002_push_tracking_margin_from_b0_gpu/smoke_20260629T062042Z_gpu/2026_06_29_022725_245760`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.002`
- corrected actuator bridge enabled
- bridge delay: `3-4` ticks
- bridge tau: `0.06-0.10 s`
- bridge velocity limit range: `2.0-3.25 rad/s`
- bridge per-joint variation: `0.05`
- restore-policy KL: `1.0`
- learning rate: `1.5e-5`
- actuator tracking scale: `-0.04`
- actuator tracking Huber delta: `0.03`
- behavior prior: enabled, scale `-0.35`
- domain randomization/noise/push settings otherwise matched B0C.

## Runs

### Default ROCm

Output:

`outputs/phase2_domain_randomization/stage_b0d_tracking_margin_from_b0c_gpu/smoke_20260629T073244Z_gpu`

Result:

- status: `HOLD_SMOKE_RUN`
- return code: `1`
- PPO steps: `0`
- failure:
  `rocblas_gemm_strided_batched_ex failed with: rocblas_status_internal_error`

### ROCm Memory Toggle Retry

Environment overrides:

- `XLA_PYTHON_CLIENT_PREALLOCATE=false`
- `XLA_PYTHON_CLIENT_MEM_FRACTION=0.60`
- `MIOPEN_DEBUG_FUSION_ENGINE_DISABLE=1`
- `HSA_OVERRIDE_GFX_VERSION=11.0.0`

Output:

`outputs/phase2_domain_randomization/stage_b0d_tracking_margin_from_b0c_rocm_memfix_gpu/smoke_20260629T073401Z_gpu`

Result:

- status: `HOLD_SMOKE_RUN`
- return code: `-6`
- PPO steps: `0`
- failure:
  `ROCM_ERROR_ILLEGAL_ADDRESS` while setting the ROCm context.

## Interpretation

B0D was not tested. Both attempts failed before any PPO step, so these results do not
support or reject the tracking-margin recipe. They only show that the local ROCm/JAX/MJX
training path was unstable at this point in the session.

Do not compare B0D to B0C as a policy result. The next valid B0D attempt needs either:

- a clean ROCm runtime reset and rerun of the same recipe, or
- a CUDA/Colab/A100 run using the pinned training stack, or
- a deliberately small CPU smoke only for command/path validation.

No robot test, SSH, deploy, grounded replay, or runtime behavior change was performed.
