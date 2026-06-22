# ROCm / MJX Runtime Isolation

gate_result: `HOLD_PLAYGROUND_GPU_STEP`
smallest_failing_subtest: `preallocate_false_gpu_playground_direct_mjx_step`

## Executive Summary

- Basic JAX GPU: `NOT_RUN`
- JAX jit/scan GPU: `NOT_RUN`
- Minimal MJX GPU: `NOT_RUN`
- Playground reset GPU: `NOT_RUN`
- Playground direct MJX step GPU: `FAIL`
- Playground direct MJX step JIT GPU: `NOT_RUN`
- Playground one-step GPU: `NOT_RUN`
- Playground one-step JIT GPU: `NOT_RUN`
- Playground scan-step GPU: `NOT_RUN`
- Playground sanitized scan-step GPU: `NOT_RUN`
- Playground bridge GPU: `NOT_RUN`
- Closed-loop GPU: `NOT_RUN`
- Closed-loop CPU: `NOT_RUN`

This is an offline runtime/backend isolation report. No robot commands, SSH,
deployment, or training are involved.

## Matrix

| id | variant | platform | subtest | status | returncode | elapsed_s | progress |
|---|---|---|---|---|---:|---:|---|
| `preallocate_false_gpu_playground_direct_mjx_step` | `preallocate_false` | `gpu` | `playground_direct_mjx_step` | `TIMEOUT` | `None` | 120.16 | NA |
| `mem_fraction_050_gpu_playground_direct_mjx_step` | `mem_fraction_050` | `gpu` | `playground_direct_mjx_step` | `TIMEOUT` | `None` | 120.21 | NA |
| `mem_fraction_060_gpu_playground_direct_mjx_step` | `mem_fraction_060` | `gpu` | `playground_direct_mjx_step` | `TIMEOUT` | `None` | 120.21 | NA |
| `allocator_platform_gpu_playground_direct_mjx_step` | `allocator_platform` | `gpu` | `playground_direct_mjx_step` | `TIMEOUT` | `None` | 120.21 | NA |
| `rocm_strict_ieee_gpu_playground_direct_mjx_step` | `rocm_strict_ieee` | `gpu` | `playground_direct_mjx_step` | `TIMEOUT` | `None` | 120.22 | NA |
| `xla_compiler_conservative_gpu_playground_direct_mjx_step` | `xla_compiler_conservative` | `gpu` | `playground_direct_mjx_step` | `TIMEOUT` | `None` | 120.20 | NA |

## Failing Output Excerpts

### preallocate_false_gpu_playground_direct_mjx_step

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_direct_step_variants/preallocate_false_gpu_playground_direct_mjx_step.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_direct_step_variants/preallocate_false_gpu_playground_direct_mjx_step.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

### mem_fraction_050_gpu_playground_direct_mjx_step

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_direct_step_variants/mem_fraction_050_gpu_playground_direct_mjx_step.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_direct_step_variants/mem_fraction_050_gpu_playground_direct_mjx_step.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

### mem_fraction_060_gpu_playground_direct_mjx_step

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_direct_step_variants/mem_fraction_060_gpu_playground_direct_mjx_step.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_direct_step_variants/mem_fraction_060_gpu_playground_direct_mjx_step.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

### allocator_platform_gpu_playground_direct_mjx_step

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_direct_step_variants/allocator_platform_gpu_playground_direct_mjx_step.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_direct_step_variants/allocator_platform_gpu_playground_direct_mjx_step.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

### rocm_strict_ieee_gpu_playground_direct_mjx_step

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_direct_step_variants/rocm_strict_ieee_gpu_playground_direct_mjx_step.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_direct_step_variants/rocm_strict_ieee_gpu_playground_direct_mjx_step.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

### xla_compiler_conservative_gpu_playground_direct_mjx_step

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_direct_step_variants/xla_compiler_conservative_gpu_playground_direct_mjx_step.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_direct_step_variants/xla_compiler_conservative_gpu_playground_direct_mjx_step.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

## Environment Variants Run

`preallocate_false`, `mem_fraction_050`, `mem_fraction_060`, `allocator_platform`, `rocm_strict_ieee`, `xla_compiler_conservative`

Supported variants are `default`, `preallocate_false`,
`mem_fraction_050`, `mem_fraction_060`, `allocator_platform`,
`disable_jit`, `debug_nans_infs`, `tensor_parallel_one`,
`gfx1100_override`, `gfx1100_mem_safe`, `miopen_fusion_disabled`,
`xla_disable_latency_scheduler`, `xla_disable_triton_gemm`,
`xla_disable_triton_gemm_softmax`, `xla_compiler_conservative`,
`rocm_strict_ieee`, `xla_rocm_data_dir`, and `xla_triton_strict_ieee`.

## Recommendation

Minimal MJX works, but Playground stepping fails. Inspect Open Duck MJX model features on ROCm.
