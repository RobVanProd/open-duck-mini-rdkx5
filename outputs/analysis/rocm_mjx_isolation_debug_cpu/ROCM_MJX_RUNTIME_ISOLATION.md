# ROCm / MJX Runtime Isolation

gate_result: `HOLD_INSUFFICIENT_DATA`
smallest_failing_subtest: `debug_nans_infs_cpu_playground_reset`

## Executive Summary

- Basic JAX GPU: `NOT_RUN`
- JAX jit/scan GPU: `NOT_RUN`
- Minimal MJX GPU: `NOT_RUN`
- Playground reset GPU: `NOT_RUN`
- Playground one-step GPU: `NOT_RUN`
- Playground one-step JIT GPU: `NOT_RUN`
- Playground scan-step GPU: `NOT_RUN`
- Playground bridge GPU: `NOT_RUN`
- Closed-loop GPU: `NOT_RUN`
- Closed-loop CPU: `NOT_RUN`

This is an offline runtime/backend isolation report. No robot commands, SSH,
deployment, or training are involved.

## Matrix

| id | variant | platform | subtest | status | returncode | elapsed_s | progress |
|---|---|---|---|---|---:|---:|---|
| `debug_nans_infs_cpu_playground_reset` | `debug_nans_infs` | `cpu` | `playground_reset` | `FAIL` | `1` | 26.89 | NA |
| `debug_nans_infs_cpu_playground_scan_step_vanilla` | `debug_nans_infs` | `cpu` | `playground_scan_step_vanilla` | `FAIL` | `1` | 26.10 | NA |

## Failing Output Excerpts

### debug_nans_infs_cpu_playground_reset

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_debug_cpu/debug_nans_infs_cpu_playground_reset.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_debug_cpu/debug_nans_infs_cpu_playground_reset.stderr.txt`

```text
thon3.12/site-packages/mujoco/mjx/_src/collision_driver.py", line 437, in collision
    dist, pos, frame = func(m, d, key, contact.geom)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/mujoco/mjx/_src/collision_convex.py", line 74, in collide
    dist, pos, frame = jax.vmap(fn, in_axes=in_axes)(*infos)  # pytype: disable=wrong-keyword-args
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/mujoco/mjx/_src/collision_convex.py", line 946, in convex_convex
    dist, pos, n = _convex_convex(c1, c2)
                   ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/mujoco/mjx/_src/collision_convex.py", line 912, in _convex_convex
    dist, pos, normal = _sat_gaussmap(
                        ^^^^^^^^^^^^^^
  File "/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/mujoco/mjx/_src/collision_convex.py", line 846, in _sat_gaussmap
    edge_dist = jp.where(is_minkowski_face, edge_dist, -jp.inf)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/numpy/lax_numpy.py", line 2785, in where
    return util._where(condition, x, y)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/numpy/util.py", line 299, in _where
    condition, x_arr, y_arr = _broadcast_arrays(condition, x, y)
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/numpy/util.py", line 253, in _broadcast_arrays
    return [_broadcast_to(arg, result_shape, result_sharding) for arg in args]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/numpy/util.py", line 278, in _broadcast_to
    return lax.broadcast_in_dim(arr, shape, tuple(range(nlead, len(shape))),
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FloatingPointError: invalid value (inf) encountered in broadcast_in_dim
--------------------
For simplicity, JAX has removed its internal frames from the traceback of the following exception. Set JAX_TRACEBACK_FILTERING=off to include these.
```

### debug_nans_infs_cpu_playground_scan_step_vanilla

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_debug_cpu/debug_nans_infs_cpu_playground_scan_step_vanilla.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_debug_cpu/debug_nans_infs_cpu_playground_scan_step_vanilla.stderr.txt`

```text
thon3.12/site-packages/mujoco/mjx/_src/collision_driver.py", line 437, in collision
    dist, pos, frame = func(m, d, key, contact.geom)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/mujoco/mjx/_src/collision_convex.py", line 74, in collide
    dist, pos, frame = jax.vmap(fn, in_axes=in_axes)(*infos)  # pytype: disable=wrong-keyword-args
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/mujoco/mjx/_src/collision_convex.py", line 946, in convex_convex
    dist, pos, n = _convex_convex(c1, c2)
                   ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/mujoco/mjx/_src/collision_convex.py", line 912, in _convex_convex
    dist, pos, normal = _sat_gaussmap(
                        ^^^^^^^^^^^^^^
  File "/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/mujoco/mjx/_src/collision_convex.py", line 846, in _sat_gaussmap
    edge_dist = jp.where(is_minkowski_face, edge_dist, -jp.inf)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/numpy/lax_numpy.py", line 2785, in where
    return util._where(condition, x, y)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/numpy/util.py", line 299, in _where
    condition, x_arr, y_arr = _broadcast_arrays(condition, x, y)
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/numpy/util.py", line 253, in _broadcast_arrays
    return [_broadcast_to(arg, result_shape, result_sharding) for arg in args]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/numpy/util.py", line 278, in _broadcast_to
    return lax.broadcast_in_dim(arr, shape, tuple(range(nlead, len(shape))),
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FloatingPointError: invalid value (inf) encountered in broadcast_in_dim
--------------------
For simplicity, JAX has removed its internal frames from the traceback of the following exception. Set JAX_TRACEBACK_FILTERING=off to include these.
```

## Environment Variants Run

`debug_nans_infs`

Supported variants are `default`, `preallocate_false`,
`mem_fraction_050`, `mem_fraction_060`, `allocator_platform`,
`disable_jit`, `debug_nans_infs`, `miopen_fusion_disabled`,
`xla_disable_latency_scheduler`, `xla_disable_triton_gemm`,
and `xla_compiler_conservative`.

## Recommendation

Collect more isolation data before changing training or robot behavior.
