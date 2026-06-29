# Phase 2 z=0.005 Local ROCm Command-Buffer Result

status: `HOLD_LOCAL_8ENV_LOW_FORWARD_PROGRESS`

Date: `2026-06-29`

## Backend Finding

The local 7900 XTX path can run the z=0.005 support recipe when both are true:

```text
HSA_OVERRIDE_GFX_VERSION is unset
XLA_FLAGS=--xla_gpu_enable_command_buffer=
```

Without the command-buffer flag, the reduced `8`-env run failed during GPU graph
capture:

```text
rocblas_gemm_strided_batched_ex failed with rocblas_status_internal_error
```

With command buffers disabled, the `8`-env `20480`-timestep run completed:

```text
output_dir:
  outputs/phase2_domain_randomization/stage_z005_support_local_rocm_no_override_8env_20480_nocmdbuf/smoke_20260629T164854Z_gpu
status: PASS_SMOKE_RUN
elapsed_s: 446.6064
checkpoints:
  7680
  15360
  23040
```

However, a longer `8`-env `81920`-timestep attempt with the same command-buffer
flag failed before the first PPO step during evaluator reset:

```text
output_dir:
  outputs/phase2_domain_randomization/stage_z005_support_local_rocm_no_override_8env_81920_nocmdbuf/smoke_20260629T170558Z_gpu
status: HOLD_SMOKE_RUN
elapsed_s: 33.0128
error:
  rocblas_gemm_strided_batched_ex failed with rocblas_status_internal_error
```

This is a useful local backend path, but it is not the intended full
`64`-env Phase 2 workflow and should not replace the pinned A100/Colab path for
final policy-producing runs.

## Candidate Gate

Latest ONNX tested:

```text
outputs/phase2_domain_randomization/stage_z005_support_local_rocm_no_override_8env_20480_nocmdbuf/smoke_20260629T164854Z_gpu/2026_06_29_125557_23040.onnx
```

Immediate target gate:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.005
command_x: 0.08
bridge: corrected fitted
duration: 15s
seeds: 0-7 planned
```

Seed 0 already held:

```text
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
termination: duration_complete
track_ratio: 0.2234
mean vx: 0.0179 m/s
max tracking p95: 0.1948 rad
```

The remaining seeds were not run because the candidate cannot pass the required
8/8 gate after seed 0 fails. The leftover seed-1 worker was terminated.

## Interpretation

The command-buffer-disabled local ROCm path is useful for small exploratory
policy runs, but this 8-env reduced candidate did not preserve enough forward
motion on rough `z=0.005`. It is not a promotion candidate and should not be
robot-tested.

Next policy-producing attempt should use the pinned A100/Colab
`phase2-z005-support` full workflow when a visible session exists, or a local
ROCm recipe explicitly designed around the command-buffer workaround and then
gated from scratch.
