# ROCm / MJX Runtime Isolation

gate_result: `HOLD_PLAYGROUND_GPU_STEP`
smallest_failing_subtest: `default_gpu_playground_direct_mjx_step`

## Executive Summary

- Basic JAX GPU: `PASS`
- JAX jit/scan GPU: `NOT_RUN`
- Minimal MJX GPU: `PASS`
- Playground reset GPU: `PASS`
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
| `default_gpu_basic_jax` | `default` | `gpu` | `basic_jax` | `PASS` | `0` | 3.30 | NA |
| `default_gpu_minimal_mjx_step` | `default` | `gpu` | `minimal_mjx_step` | `PASS` | `0` | 17.67 | 1:PASS |
| `default_gpu_playground_contract_only` | `default` | `gpu` | `playground_contract_only` | `PASS` | `0` | 5.16 | NA |
| `default_gpu_playground_reset` | `default` | `gpu` | `playground_reset` | `PASS` | `0` | 71.27 | NA |
| `default_gpu_playground_direct_mjx_step` | `default` | `gpu` | `playground_direct_mjx_step` | `TIMEOUT` | `None` | 120.28 | NA |
| `default_cpu_basic_jax` | `default` | `cpu` | `basic_jax` | `PASS` | `0` | 1.23 | NA |
| `default_cpu_minimal_mjx_step` | `default` | `cpu` | `minimal_mjx_step` | `PASS` | `0` | 9.30 | 1:PASS |
| `default_cpu_playground_contract_only` | `default` | `cpu` | `playground_contract_only` | `PASS` | `0` | 2.76 | NA |
| `default_cpu_playground_reset` | `default` | `cpu` | `playground_reset` | `PASS` | `0` | 55.44 | NA |
| `default_cpu_playground_direct_mjx_step` | `default` | `cpu` | `playground_direct_mjx_step` | `PASS` | `0` | 61.25 | NA |

## Failing Output Excerpts

### default_gpu_playground_direct_mjx_step

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_version_matrix_playground005/default_gpu_playground_direct_mjx_step.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_version_matrix_playground005/default_gpu_playground_direct_mjx_step.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground-rocm-playground005/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground-rocm-playground005/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

## Environment Variants Run

`default`

Supported variants are `default`, `preallocate_false`,
`mem_fraction_050`, `mem_fraction_060`, `allocator_platform`,
`disable_jit`, `debug_nans_infs`, `tensor_parallel_one`,
`gfx1100_override`, `gfx1100_mem_safe`, `miopen_fusion_disabled`,
`xla_disable_latency_scheduler`, `xla_disable_triton_gemm`,
`xla_disable_triton_gemm_softmax`, `xla_compiler_conservative`,
`rocm_strict_ieee`, `xla_rocm_data_dir`, and `xla_triton_strict_ieee`.

## Recommendation

Minimal MJX works, but Playground stepping fails. Inspect Open Duck MJX model features on ROCm.
