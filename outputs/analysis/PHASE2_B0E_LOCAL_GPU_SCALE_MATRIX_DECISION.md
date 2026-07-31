# Phase 2 B0E Local GPU Scale Matrix

status: `HOLD_LOCAL_ROCM_SCALE_BOUNDARY_4_PASS_8_FAIL`

## Purpose

B0E passed a 1-env local ROCm path check but failed at 16 and 32 envs during
Brax evaluator reset. This bounded scale matrix tested the missing small env
counts to identify the local ROCm boundary before spending more time on the
wrong backend path.

This was offline-only. No robot tests, SSH, deploy, grounded replay, runtime
behavior changes, or policy overwrite were performed.

## Fixed Recipe

All matrix runs used the B0E motion-preserving tracking-margin recipe:

```text
platform: gpu
JAX_PLATFORMS: rocm
task: rough_terrain_backlash
terrain hfield z scale: 0.002
restore checkpoint:
  outputs/phase2_domain_randomization/stage_b0c_rough_z002_push_tracking_margin_from_b0_gpu/smoke_20260629T062042Z_gpu/2026_06_29_022725_245760

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

Each run used `episode_length=20`, `unroll_length=10`,
`num_minibatches=1`, and `num_updates_per_batch=1`. These are plumbing
diagnostics only; none of the emitted checkpoints are policy candidates.

## Results

| envs | timesteps | status | return code | PPO step | elapsed | evidence |
|---:|---:|---|---:|---:|---:|---|
| 1 | 20 | `PASS_SMOKE_RUN` | 0 | 100 | 172.0 s | `PHASE2_B0E_LOCAL_GPU_PATH_CHECK_DECISION.md` |
| 2 | 40 | `PASS_SMOKE_RUN` | 0 | 200 | 122.4 s | `smoke_20260629T084544Z_gpu` |
| 4 | 80 | `PASS_SMOKE_RUN` | 0 | 400 | 122.1 s | `smoke_20260629T084814Z_gpu` |
| 8 | 160 | `HOLD_SMOKE_RUN` | 1 | none | 33.0 s | `smoke_20260629T085048Z_gpu` |
| 16 | 10240 | `HOLD_SMOKE_RUN` | 1 | none | 49.8 s | `PHASE2_B0E_LOCAL_ROCM_HOLD_DECISION.md` |
| 32 | 20480 | `HOLD_SMOKE_RUN` | 1 | none | 33.1 s | `PHASE2_B0E_LOCAL_ROCM_HOLD_DECISION.md` |

The 8-env failure matches the 16/32-env failure mode:

```text
jax.jit(eval_env.reset):
  rocblas_gemm_strided_batched_ex failed with rocblas_status_internal_error
```

## Evidence Hashes

```text
2 env manifest:
  9d668fd52364e7900a385baf7e1c92f32365f5a6236705f989d266d48df3a4f8
2 env stderr:
  745d48d982166319780d8dd0319a475dd913aa0588d8fd283b00a8d53a648b9d
2 env stdout:
  1fcd30bce6d7335d8134575a0245c3257537d7ead1d6721aab2ab67400b66d95

4 env manifest:
  e5a905d212f9af59d67f2c6ad8e7b0683b830ad4285faea3c2cb07ef36678922
4 env stderr:
  f1204644024c247b114608bdc36d43f0ae43177d8f270c145bde6c9c6cbcd254
4 env stdout:
  f6d3e0e4df7e0efcc7280a5aa6d8c15c21b3e9681ce958f711d4eb4ecbe725a5

8 env manifest:
  64d86be39087236a05f26ace9f5675908fba52117ea71a5ec670efeb3d4fc21b
8 env stderr:
  848c9947998403957d24820a116ae4de4629c0ae467d1b043e52017643d9a1ff
8 env stdout:
  e5d8da36e65068975d4cb22fd7a53c187ec30170d1a5e73d19907128aed3b7f3
```

## Decision

`HOLD_LOCAL_ROCM_SCALE_BOUNDARY_4_PASS_8_FAIL`

B0E is valid and can run on local ROCm at tiny scale, but the current local ROCm
backend fails at evaluator reset once the matrix reaches 8 envs. Four envs is
not enough throughput for the requested Phase 2 robustness training. The next
policy-producing run should therefore remain the pinned CUDA/A100
`phase2-b0e` workflow unless the local ROCm evaluator reset issue is fixed.

Do not promote any checkpoint from this matrix. The matrix only establishes the
local backend boundary.
