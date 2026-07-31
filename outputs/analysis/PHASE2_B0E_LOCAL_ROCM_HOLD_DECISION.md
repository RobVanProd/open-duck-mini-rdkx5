# Phase 2 B0E Local ROCm Hold

status: `HOLD_LOCAL_ROCM_EVALUATOR_RESET`

## Purpose

B0E was a motion-preserving tracking-margin follow-up to B0D. B0D reduced
forward motion while leaving the compact corrected-bridge tracking p95 near the
B0C parent, so B0E weakened the actuator-tracking penalty and strengthened
forward-progress terms while restoring from the B0C checkpoint.

This was an offline sim-only attempt. No robot tests, SSH, deploy, grounded
replay, runtime behavior changes, or policy overwrite were performed.

## B0E Recipe

- restore checkpoint:
  `outputs/phase2_domain_randomization/stage_b0c_rough_z002_push_tracking_margin_from_b0_gpu/smoke_20260629T062042Z_gpu/2026_06_29_022725_245760`
- corrected actuator bridge: enabled
- actuator tracking scale: `-0.015`
- restore-policy KL scale: `1.5`
- PPO learning rate: `0.000012`
- PPO clip epsilon: `0.04`
- PPO max grad norm: `0.20`
- forward progress scale: `2.5`
- tracking lin-vel scale: `3.0`
- tracking sigma: `0.01`
- command progress scale: `1.5`
- command progress shortfall scale: `-4.0`
- command progress required ratio: `0.45`
- rough terrain backlash: enabled
- mild domain randomization and mild pushes: enabled

## Local Attempts

| attempt | envs | status | return code | elapsed | failure |
|---|---:|---|---:|---:|---|
| `stage_b0e_motion_preserving_tracking_local_gpu_32env` | 32 | `HOLD_SMOKE_RUN` | 1 | 33.1 s | `rocblas_gemm_strided_batched_ex failed with rocblas_status_internal_error` |
| `stage_b0e_motion_preserving_tracking_local_gpu_16env` | 16 | `HOLD_SMOKE_RUN` | 1 | 49.8 s | `rocblas_gemm_strided_batched_ex failed with rocblas_status_internal_error` |

Both failures occurred during Brax evaluator construction at
`jax.jit(eval_env.reset)`, before any PPO update or exported checkpoint. B0E
therefore has not been tested as a policy recipe and should not be compared
against B0C/B0D gate metrics.

## CPU Path Check

A deliberately tiny CPU-only plumbing check was run after the ROCm failures:

```text
path:
  outputs/phase2_domain_randomization/stage_b0e_motion_preserving_tracking_cpu_path_check/smoke_20260629T082956Z_cpu

configuration:
  platform: cpu
  envs: 1
  timesteps: 20
  episode_length: 20
  export_min_step: 1

status:
  PASS_SMOKE_RUN

result:
  reached PPO step 100
  saved checkpoint 2026_06_29_043048_100
```

This CPU pass is not a policy result and is not promotable. It only confirms
that the B0E command wiring, restore checkpoint, behavior prior, domain
randomization flags, push flags, and actuator-bridge flags are structurally
valid outside the local ROCm evaluator-reset failure.

## Evidence Hashes

```text
32env manifest:
  2bd1dd5d2d6b6092f94fd0a7619bd45145890055178ad2096bcc0c6156af27ab

32env stderr:
  6b2e344febf21e701c8fcd10ca1b31fc0c454421113371ce967044b3ea9f42fb

16env manifest:
  831fefd37655a3e26a89eb5f35200e4ac55ffe2ce23a53cadb0a066f87e2ba03

16env stderr:
  8d3d9d46888820007f80f56fbaf60484bb1211822c3e7e5cbaf407a40fa4ed28

CPU path-check manifest:
  888658162e4e2a3352703b59d4e468e455150411634a4ef196a786ed3b17f08b

CPU path-check stderr:
  a9ae14f07bdb3dd0e4b0a99b0d669a35ba35518ad4852f46a2998b4ae0045a74

CPU path-check stdout:
  2e4162efaf9e542caea583c93265efa78d9dcf201a2aa248108661a4bc61f4cc
```

## Decision

`HOLD_LOCAL_ROCM_EVALUATOR_RESET`

Do not keep retrying B0E locally on the same ROCm path without a backend change.
The next valid ways forward are:

- run B0E on a visible CUDA/A100 Colab session with the pinned workflow, or
- use CPU only for further command-plumbing checks, not for policy results, or
- fix the local ROCm evaluator-reset failure and then retry the bounded B0E
  smoke.

B0C remains the better parent than B0D for compact `x=0.08` until B0E or a
successor actually completes training and passes the corrected-bridge gates.
