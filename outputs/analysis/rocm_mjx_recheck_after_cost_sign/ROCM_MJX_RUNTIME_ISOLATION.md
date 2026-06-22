# ROCm / MJX Runtime Isolation

gate_result: `HOLD_PLAYGROUND_GPU_STEP`
smallest_failing_subtest: `default_gpu_playground_one_step_vanilla`

## Executive Summary

- Basic JAX GPU: `PASS`
- JAX jit/scan GPU: `NOT_RUN`
- Minimal MJX GPU: `PASS`
- Playground reset GPU: `NOT_RUN`
- Playground one-step GPU: `FAIL`
- Playground one-step JIT GPU: `FAIL`
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
| `default_gpu_basic_jax` | `default` | `gpu` | `basic_jax` | `PASS` | `0` | 1.03 | NA |
| `default_gpu_minimal_mjx_step` | `default` | `gpu` | `minimal_mjx_step` | `PASS` | `0` | 8.41 | 1:PASS |
| `default_gpu_playground_one_step_vanilla` | `default` | `gpu` | `playground_one_step_vanilla` | `TIMEOUT` | `None` | 180.23 | NA |
| `default_gpu_playground_one_step_jit` | `default` | `gpu` | `playground_one_step_jit` | `FAIL` | `-6` | 55.72 | NA |

## Failing Output Excerpts

### default_gpu_playground_one_step_vanilla

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_recheck_after_cost_sign/default_gpu_playground_one_step_vanilla.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_recheck_after_cost_sign/default_gpu_playground_one_step_vanilla.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

### default_gpu_playground_one_step_jit

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_recheck_after_cost_sign/default_gpu_playground_one_step_jit.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_recheck_after_cost_sign/default_gpu_playground_one_step_jit.stderr.txt`

```text
t<>::destructor_impl()
    @     0x796224f560d0  xla::LRUCache<>::Clear()
    @     0x796224f5a532  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x796224f56385  std::default_delete<>::operator()()
    @     0x796224f5aa70  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x79622178845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @          0x1aac007  PyObject_ClearWeakRefs.warm
    @          0x1a89a88  func_dealloc.warm
    @     0x79622b148fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x79622b145f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x79622b145fd5  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x79622b145cbb  xla::LRUCache<>::Clear()
    @     0x79622b145a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x79622b148008  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x79622178845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @           0x45b024  handle_callback.llvm.6155425969336250027
    @          0x1b22206  subtype_dealloc.cold
    @          0x180137f  tupledealloc
    @     0x79622b148fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x79622b145f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x79622b146047  absl::lts_20250814::functional_internal::InvokeObject<>()
    @     0x796224ea04bf  absl::lts_20250814::container_internal::IterateOverFullSlots()
    @     0x79622b145ff3  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x79622b145cbb  xla::LRUCache<>::Clear()
    @     0x79622b145a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x79622b1492a8  std::pair<>::~pair()
    @     0x79622b144fe8  jax::WeakrefLRUCache::Clear()
    @     0x79622b147146  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x79622178845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1816073  _PyEval_EvalFrameDefault
    @          0x1ad68ff  atexit_callfuncs.llvm.9450642270383810775.warm
    @          0x190e896  Py_FinalizeEx
    @          0x198c54c  Py_RunMain
    @          0x198c198  pymain_main.llvm.11489439184168853189
    @          0x198bfac  main
    @     0x79622d62a601  (unknown)
    @     0x79622d62a718  __libc_start_main
    @          0x19a9269  _start
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
