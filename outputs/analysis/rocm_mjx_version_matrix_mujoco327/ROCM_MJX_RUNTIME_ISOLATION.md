# ROCm / MJX Runtime Isolation

gate_result: `HOLD_PLAYGROUND_GPU_STEP`
smallest_failing_subtest: `default_gpu_playground_reset`

## Executive Summary

- Basic JAX GPU: `PASS`
- JAX jit/scan GPU: `NOT_RUN`
- Minimal MJX GPU: `PASS`
- Playground reset GPU: `FAIL`
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
| `default_gpu_basic_jax` | `default` | `gpu` | `basic_jax` | `PASS` | `0` | 2.02 | NA |
| `default_gpu_minimal_mjx_step` | `default` | `gpu` | `minimal_mjx_step` | `PASS` | `0` | 9.55 | 1:PASS |
| `default_gpu_playground_contract_only` | `default` | `gpu` | `playground_contract_only` | `PASS` | `0` | 3.25 | NA |
| `default_gpu_playground_reset` | `default` | `gpu` | `playground_reset` | `FAIL` | `1` | 35.44 | NA |
| `default_gpu_playground_direct_mjx_step` | `default` | `gpu` | `playground_direct_mjx_step` | `FAIL` | `1` | 35.15 | NA |
| `default_cpu_basic_jax` | `default` | `cpu` | `basic_jax` | `PASS` | `0` | 0.87 | NA |
| `default_cpu_minimal_mjx_step` | `default` | `cpu` | `minimal_mjx_step` | `PASS` | `0` | 5.59 | 1:PASS |
| `default_cpu_playground_contract_only` | `default` | `cpu` | `playground_contract_only` | `PASS` | `0` | 1.94 | NA |
| `default_cpu_playground_reset` | `default` | `cpu` | `playground_reset` | `FAIL` | `1` | 27.06 | NA |
| `default_cpu_playground_direct_mjx_step` | `default` | `cpu` | `playground_direct_mjx_step` | `FAIL` | `1` | 27.44 | NA |

## Failing Output Excerpts

### default_gpu_playground_reset

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_version_matrix_mujoco327/default_gpu_playground_reset.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_version_matrix_mujoco327/default_gpu_playground_reset.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground-rocm-mujoco327/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
Traceback (most recent call last):
  File "<string>", line 92, in <module>
  File "/home/lsd/robots/open-duck-mini-rdkx5/../Open_Duck_Playground/playground/open_duck_mini_v2/joystick.py", line 347, in reset
    geoms_colliding(data, geom_id, self._floor_geom_id)
  File "/home/lsd/robots/envs/open-duck-playground-rocm-mujoco327/lib/python3.12/site-packages/mujoco_playground/_src/collision.py", line 38, in geoms_colliding
    return get_collision_info(state._impl.contact, geom1, geom2)[0] < 0  # pylint: disable=protected-access
                              ^^^^^^^^^^^
AttributeError: 'Data' object has no attribute '_impl'
```

### default_gpu_playground_direct_mjx_step

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_version_matrix_mujoco327/default_gpu_playground_direct_mjx_step.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_version_matrix_mujoco327/default_gpu_playground_direct_mjx_step.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground-rocm-mujoco327/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
Traceback (most recent call last):
  File "<string>", line 93, in <module>
  File "/home/lsd/robots/open-duck-mini-rdkx5/../Open_Duck_Playground/playground/open_duck_mini_v2/joystick.py", line 347, in reset
    geoms_colliding(data, geom_id, self._floor_geom_id)
  File "/home/lsd/robots/envs/open-duck-playground-rocm-mujoco327/lib/python3.12/site-packages/mujoco_playground/_src/collision.py", line 38, in geoms_colliding
    return get_collision_info(state._impl.contact, geom1, geom2)[0] < 0  # pylint: disable=protected-access
                              ^^^^^^^^^^^
AttributeError: 'Data' object has no attribute '_impl'
```

### default_cpu_playground_reset

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_version_matrix_mujoco327/default_cpu_playground_reset.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_version_matrix_mujoco327/default_cpu_playground_reset.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground-rocm-mujoco327/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
Traceback (most recent call last):
  File "<string>", line 92, in <module>
  File "/home/lsd/robots/open-duck-mini-rdkx5/../Open_Duck_Playground/playground/open_duck_mini_v2/joystick.py", line 347, in reset
    geoms_colliding(data, geom_id, self._floor_geom_id)
  File "/home/lsd/robots/envs/open-duck-playground-rocm-mujoco327/lib/python3.12/site-packages/mujoco_playground/_src/collision.py", line 38, in geoms_colliding
    return get_collision_info(state._impl.contact, geom1, geom2)[0] < 0  # pylint: disable=protected-access
                              ^^^^^^^^^^^
AttributeError: 'Data' object has no attribute '_impl'
```

### default_cpu_playground_direct_mjx_step

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_version_matrix_mujoco327/default_cpu_playground_direct_mjx_step.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_version_matrix_mujoco327/default_cpu_playground_direct_mjx_step.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground-rocm-mujoco327/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
Traceback (most recent call last):
  File "<string>", line 93, in <module>
  File "/home/lsd/robots/open-duck-mini-rdkx5/../Open_Duck_Playground/playground/open_duck_mini_v2/joystick.py", line 347, in reset
    geoms_colliding(data, geom_id, self._floor_geom_id)
  File "/home/lsd/robots/envs/open-duck-playground-rocm-mujoco327/lib/python3.12/site-packages/mujoco_playground/_src/collision.py", line 38, in geoms_colliding
    return get_collision_info(state._impl.contact, geom1, geom2)[0] < 0  # pylint: disable=protected-access
                              ^^^^^^^^^^^
AttributeError: 'Data' object has no attribute '_impl'
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
