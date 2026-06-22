# ROCm / MJX Runtime Isolation

gate_result: `HOLD_PLAYGROUND_GPU_STEP`
smallest_failing_subtest: `default_gpu_playground_one_step_vanilla`

## Executive Summary

- Basic JAX GPU: `NOT_RUN`
- JAX jit/scan GPU: `NOT_RUN`
- Minimal MJX GPU: `NOT_RUN`
- Playground reset GPU: `PASS`
- Playground one-step GPU: `FAIL`
- Playground one-step JIT GPU: `FAIL`
- Playground scan-step GPU: `FAIL`
- Playground sanitized scan-step GPU: `NOT_RUN`
- Playground bridge GPU: `NOT_RUN`
- Closed-loop GPU: `NOT_RUN`
- Closed-loop CPU: `NOT_RUN`

This is an offline runtime/backend isolation report. No robot commands, SSH,
deployment, or training are involved.

## Matrix

| id | variant | platform | subtest | status | returncode | elapsed_s | progress |
|---|---|---|---|---|---:|---:|---|
| `default_gpu_playground_reset` | `default` | `gpu` | `playground_reset` | `PASS` | `0` | 43.10 | NA |
| `default_gpu_playground_one_step_vanilla` | `default` | `gpu` | `playground_one_step_vanilla` | `TIMEOUT` | `None` | 180.21 | NA |
| `default_gpu_playground_one_step_jit` | `default` | `gpu` | `playground_one_step_jit` | `FAIL` | `-6` | 56.90 | NA |
| `default_gpu_playground_scan_step_vanilla` | `default` | `gpu` | `playground_scan_step_vanilla` | `TIMEOUT` | `None` | 180.28 | NA |

## Failing Output Excerpts

### default_gpu_playground_one_step_vanilla

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_after_power_reset/default_gpu_playground_one_step_vanilla.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_after_power_reset/default_gpu_playground_one_step_vanilla.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

### default_gpu_playground_one_step_jit

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_after_power_reset/default_gpu_playground_one_step_jit.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_after_power_reset/default_gpu_playground_one_step_jit.stderr.txt`

```text
t<>::destructor_impl()
    @     0x7e13fbb560d0  xla::LRUCache<>::Clear()
    @     0x7e13fbb5a532  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7e13fbb56385  std::default_delete<>::operator()()
    @     0x7e13fbb5aa70  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x7e13f838845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @          0x1aac007  PyObject_ClearWeakRefs.warm
    @          0x1a89a88  func_dealloc.warm
    @     0x7e1401d48fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7e1401d45f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x7e1401d45fd5  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x7e1401d45cbb  xla::LRUCache<>::Clear()
    @     0x7e1401d45a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7e1401d48008  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x7e13f838845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @           0x45b024  handle_callback.llvm.6155425969336250027
    @          0x1b22206  subtype_dealloc.cold
    @          0x180137f  tupledealloc
    @     0x7e1401d48fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7e1401d45f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x7e1401d46047  absl::lts_20250814::functional_internal::InvokeObject<>()
    @     0x7e13fbaa04bf  absl::lts_20250814::container_internal::IterateOverFullSlots()
    @     0x7e1401d45ff3  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x7e1401d45cbb  xla::LRUCache<>::Clear()
    @     0x7e1401d45a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7e1401d492a8  std::pair<>::~pair()
    @     0x7e1401d44fe8  jax::WeakrefLRUCache::Clear()
    @     0x7e1401d47146  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x7e13f838845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1816073  _PyEval_EvalFrameDefault
    @          0x1ad68ff  atexit_callfuncs.llvm.9450642270383810775.warm
    @          0x190e896  Py_FinalizeEx
    @          0x198c54c  Py_RunMain
    @          0x198c198  pymain_main.llvm.11489439184168853189
    @          0x198bfac  main
    @     0x7e140402a601  (unknown)
    @     0x7e140402a718  __libc_start_main
    @          0x19a9269  _start
```

### default_gpu_playground_scan_step_vanilla

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_after_power_reset/default_gpu_playground_scan_step_vanilla.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_after_power_reset/default_gpu_playground_scan_step_vanilla.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

## Environment Variants Run

`default`

Supported variants are `default`, `preallocate_false`,
`mem_fraction_050`, `mem_fraction_060`, `allocator_platform`,
`disable_jit`, `debug_nans_infs`, `miopen_fusion_disabled`,
`xla_disable_latency_scheduler`, `xla_disable_triton_gemm`,
`xla_disable_triton_gemm_softmax`, `xla_compiler_conservative`,
`rocm_strict_ieee`, `xla_rocm_data_dir`, and `xla_triton_strict_ieee`.

## Recommendation

Minimal MJX works, but Playground stepping fails. Inspect Open Duck MJX model features on ROCm.
