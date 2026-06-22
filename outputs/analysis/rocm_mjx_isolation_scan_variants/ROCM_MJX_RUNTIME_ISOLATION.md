# ROCm / MJX Runtime Isolation

gate_result: `HOLD_PLAYGROUND_GPU_STEP`
smallest_failing_subtest: `debug_nans_infs_gpu_playground_scan_step_vanilla`

## Executive Summary

- Basic JAX GPU: `NOT_RUN`
- JAX jit/scan GPU: `NOT_RUN`
- Minimal MJX GPU: `NOT_RUN`
- Playground reset GPU: `NOT_RUN`
- Playground one-step GPU: `NOT_RUN`
- Playground one-step JIT GPU: `NOT_RUN`
- Playground scan-step GPU: `FAIL`
- Playground bridge GPU: `NOT_RUN`
- Closed-loop GPU: `NOT_RUN`
- Closed-loop CPU: `NOT_RUN`

This is an offline runtime/backend isolation report. No robot commands, SSH,
deployment, or training are involved.

## Matrix

| id | variant | platform | subtest | status | returncode | elapsed_s | progress |
|---|---|---|---|---|---:|---:|---|
| `debug_nans_infs_gpu_playground_scan_step_vanilla` | `debug_nans_infs` | `gpu` | `playground_scan_step_vanilla` | `FAIL` | `1` | 22.96 | NA |
| `miopen_fusion_disabled_gpu_playground_scan_step_vanilla` | `miopen_fusion_disabled` | `gpu` | `playground_scan_step_vanilla` | `FAIL` | `-6` | 59.54 | NA |
| `xla_compiler_conservative_gpu_playground_scan_step_vanilla` | `xla_compiler_conservative` | `gpu` | `playground_scan_step_vanilla` | `TIMEOUT` | `None` | 120.31 | NA |

## Failing Output Excerpts

### debug_nans_infs_gpu_playground_scan_step_vanilla

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_scan_variants/debug_nans_infs_gpu_playground_scan_step_vanilla.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_scan_variants/debug_nans_infs_gpu_playground_scan_step_vanilla.stderr.txt`

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

### miopen_fusion_disabled_gpu_playground_scan_step_vanilla

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_scan_variants/miopen_fusion_disabled_gpu_playground_scan_step_vanilla.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_scan_variants/miopen_fusion_disabled_gpu_playground_scan_step_vanilla.stderr.txt`

```text
    @     0x7ef70d756173  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x7ef70d7560d0  xla::LRUCache<>::Clear()
    @     0x7ef70d75a532  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7ef70d756385  std::default_delete<>::operator()()
    @     0x7ef70d75aa70  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x7ef709f8845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @          0x1aac007  PyObject_ClearWeakRefs.warm
    @          0x1a89a88  func_dealloc.warm
    @     0x7ef713948fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7ef713945f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x7ef713945fd5  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x7ef713945cbb  xla::LRUCache<>::Clear()
    @     0x7ef713945a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7ef713948008  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x7ef709f8845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @           0x45b024  handle_callback.llvm.6155425969336250027
    @          0x1b22206  subtype_dealloc.cold
    @          0x180137f  tupledealloc
    @     0x7ef713948fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7ef713945f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x7ef713946047  absl::lts_20250814::functional_internal::InvokeObject<>()
    @     0x7ef70d6a04bf  absl::lts_20250814::container_internal::IterateOverFullSlots()
    @     0x7ef713945ff3  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x7ef713945cbb  xla::LRUCache<>::Clear()
    @     0x7ef713945a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7ef7139492a8  std::pair<>::~pair()
    @     0x7ef713944fe8  jax::WeakrefLRUCache::Clear()
    @     0x7ef713947146  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x7ef709f8845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1816073  _PyEval_EvalFrameDefault
    @          0x1ad68ff  atexit_callfuncs.llvm.9450642270383810775.warm
    @          0x190e896  Py_FinalizeEx
    @          0x198c54c  Py_RunMain
    @          0x198c198  pymain_main.llvm.11489439184168853189
    @          0x198bfac  main
    @     0x7ef715e2a601  (unknown)
```

### xla_compiler_conservative_gpu_playground_scan_step_vanilla

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_scan_variants/xla_compiler_conservative_gpu_playground_scan_step_vanilla.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_scan_variants/xla_compiler_conservative_gpu_playground_scan_step_vanilla.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

## Environment Variants Run

`debug_nans_infs`, `miopen_fusion_disabled`, `xla_compiler_conservative`

Supported variants are `default`, `preallocate_false`,
`mem_fraction_050`, `mem_fraction_060`, `allocator_platform`,
`disable_jit`, `debug_nans_infs`, `miopen_fusion_disabled`,
`xla_disable_latency_scheduler`, `xla_disable_triton_gemm`,
and `xla_compiler_conservative`.

## Recommendation

Minimal MJX works, but Playground stepping fails. Inspect Open Duck MJX model features on ROCm.
