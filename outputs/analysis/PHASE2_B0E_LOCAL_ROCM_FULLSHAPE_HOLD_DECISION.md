# Phase 2 B0E Local ROCm Full-Shape Hold

status: `HOLD_B0E_ROCM_FULLSHAPE_EVALUATOR_RESET`

## Purpose

After `XLA_PYTHON_CLIENT_PREALLOCATE=false` and
`XLA_PYTHON_CLIENT_MEM_FRACTION=0.50` moved the local ROCm B0E plumbing
boundary through 32 envs on tiny `episode_length=20` runs, this checked whether
the same memory cap makes the real B0E training/evaluator shape usable.

This was offline-only. No robot tests, SSH, deploy, grounded replay, runtime
behavior changes, or policy overwrite were performed.

## Shared Environment

```text
JAX_PLATFORM_NAME=gpu
JAX_PLATFORMS=rocm
XLA_PYTHON_CLIENT_PREALLOCATE=false
XLA_PYTHON_CLIENT_MEM_FRACTION=0.50
```

## Shared Recipe

All checks used B0E:

```text
task: rough_terrain_backlash
terrain hfield z scale: 0.002
restore checkpoint:
  outputs/phase2_domain_randomization/stage_b0c_rough_z002_push_tracking_margin_from_b0_gpu/smoke_20260629T062042Z_gpu/2026_06_29_022725_245760
corrected actuator bridge: enabled
mild DR: enabled
mild pushes: enabled
behavior prior: enabled
actuator_tracking_scale: -0.015
restore_policy_kl_scale: 1.5
```

## Results

| shape | envs | episode length | evals | timesteps | status | return code | PPO step | manifest hash |
|---|---:|---:|---:|---:|---|---:|---:|---|
| full evaluator | 32 | 750 | 2 | 81920 | `HOLD_SMOKE_RUN` | 1 | none | `25fbe5f5e2a2ab6f7493c494e60735fad35e2ed17b4c7ce7d39c3d8070d66b21` |
| full evaluator | 16 | 750 | 2 | 40960 | `HOLD_SMOKE_RUN` | 1 | none | `afed98b9158eb5d699ba481ec2146c4d3984b37da0715f48409055249441c9fc` |
| full evaluator | 8 | 750 | 2 | 20480 | `HOLD_SMOKE_RUN` | 1 | none | `de53dcd6c269776e745c9faaccbcb1d487591990102ef757f080a0f1528bdde3` |
| no eval requested | 32 | 750 | 0 | 20480 | `HOLD_SMOKE_RUN` | 1 | none | `d80c5c8246bf075e8902464b9124e02a71f0d7c0d5a2659c84a3df5721cdd82b` |

All failed before PPO update/export at the same Brax evaluator reset path:

```text
jax.jit(eval_env.reset):
  rocblas_gemm_strided_batched_ex failed with rocblas_status_internal_error
```

Setting `ppo_num_evals=0` does not bypass evaluator construction in this stack.

## Decision

`HOLD_B0E_ROCM_FULLSHAPE_EVALUATOR_RESET`

The local ROCm memory cap is enough for tiny B0E plumbing checks, but it is not
enough for the real 750-step evaluator shape required by the Phase 2 gate. Do
not launch policy-producing B0E runs locally on this ROCm path unless the
evaluator reset issue is fixed or the training stack is changed.

The next policy-producing path remains the pinned CUDA/A100 `phase2-b0e`
workflow. If no cloud session is available, local work should be limited to CPU
correctness checks, tooling, and documentation.
