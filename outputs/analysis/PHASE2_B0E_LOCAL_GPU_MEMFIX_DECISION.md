# Phase 2 B0E Local GPU Memory-Mitigation Check

status: `PASS_B0E_ROCM_MEMFIX_32ENV_PLUMBING`

## Purpose

The default local ROCm B0E scale matrix passed through `4` envs but failed at
`8`, `16`, and `32` envs during Brax evaluator reset with:

```text
rocblas_gemm_strided_batched_ex failed with rocblas_status_internal_error
```

This bounded check repeated the same B0E plumbing shape with JAX GPU memory
preallocation disabled and the JAX memory fraction capped.

This was offline-only. No robot tests, SSH, deploy, grounded replay, runtime
behavior changes, or policy overwrite were performed.

## Environment Override

```text
JAX_PLATFORM_NAME=gpu
JAX_PLATFORMS=rocm
XLA_PYTHON_CLIENT_PREALLOCATE=false
XLA_PYTHON_CLIENT_MEM_FRACTION=0.50
```

No MIOpen fusion, gfx override, allocator-platform, or compiler flag variants
were used in the passing B0E checks.

## Fixed B0E Recipe

All passing runs used the B0E motion-preserving tracking-margin recipe:

```text
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

| envs | timesteps | batch | status | return code | PPO step | output |
|---:|---:|---:|---|---:|---:|---|
| 8 | 160 | 80 | `PASS_SMOKE_RUN` | 0 | 800 | `smoke_20260629T091100Z_gpu` |
| 16 | 320 | 160 | `PASS_SMOKE_RUN` | 0 | 1600 | `smoke_20260629T092000Z_gpu_16env` |
| 32 | 640 | 320 | `PASS_SMOKE_RUN` | 0 | 3200 | `smoke_20260629T092500Z_gpu_32env` |

The same 8-env B0E shape failed under default allocation, but passed with the
memory cap. The 16/32-env checks also passed with the same cap.

## Evidence Hashes

```text
8 env ONNX:
  1c1877cee97aaf3e9f770662b3f3f7255234eb9ac52b0b01ab8f6c1707c8ffea
16 env ONNX:
  9695c3e4da6a3ec2bbf68fd64ce020c3005ff3ab1e86ae2f8babf98b1fecf472
32 env ONNX:
  27c1da2b3ad45d945ecddd5867a7a60ebe0219c27b45c6f50c4ae101aaaa6761
```

## Decision

`PASS_B0E_ROCM_MEMFIX_32ENV_PLUMBING`

The local ROCm B0E blocker was allocation-sensitive. With
`XLA_PYTHON_CLIENT_PREALLOCATE=false` and
`XLA_PYTHON_CLIENT_MEM_FRACTION=0.50`, the bounded B0E path reaches PPO/export
at 8, 16, and 32 envs.

This does not produce or promote a policy. It changes the next training option:
a local ROCm B0E run is now plausible if launched with the memory cap, while
the pinned CUDA/A100 `phase2-b0e` path remains the preferred high-throughput
route when a Colab session is visible.
