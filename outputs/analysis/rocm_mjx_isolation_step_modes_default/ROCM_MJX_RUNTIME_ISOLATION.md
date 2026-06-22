# ROCm / MJX Runtime Isolation

gate_result: `HOLD_PLAYGROUND_GPU_STEP`
smallest_failing_subtest: `default_gpu_playground_one_step_jit`

## Executive Summary

- Basic JAX GPU: `NOT_RUN`
- JAX jit/scan GPU: `NOT_RUN`
- Minimal MJX GPU: `NOT_RUN`
- Playground reset GPU: `NOT_RUN`
- Playground one-step GPU: `NOT_RUN`
- Playground one-step JIT GPU: `FAIL`
- Playground scan-step GPU: `FAIL`
- Playground bridge GPU: `NOT_RUN`
- Closed-loop GPU: `NOT_RUN`
- Closed-loop CPU: `NOT_RUN`

This is an offline runtime/backend isolation report. No robot commands, SSH,
deployment, or training are involved.

## Matrix

| id | variant | platform | subtest | status | returncode | elapsed_s | progress |
|---|---|---|---|---|---:|---:|---|
| `default_gpu_playground_one_step_jit` | `default` | `gpu` | `playground_one_step_jit` | `FAIL` | `-6` | 57.94 | NA |
| `default_gpu_playground_scan_step_vanilla` | `default` | `gpu` | `playground_scan_step_vanilla` | `FAIL` | `-6` | 58.77 | NA |

## Failing Output Excerpts

### default_gpu_playground_one_step_jit

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_step_modes_default/default_gpu_playground_one_step_jit.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_step_modes_default/default_gpu_playground_one_step_jit.stderr.txt`

```text
t<>::destructor_impl()
    @     0x7647bc5560d0  xla::LRUCache<>::Clear()
    @     0x7647bc55a532  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7647bc556385  std::default_delete<>::operator()()
    @     0x7647bc55aa70  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x7647b8d8845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @          0x1aac007  PyObject_ClearWeakRefs.warm
    @          0x1a89a88  func_dealloc.warm
    @     0x7647c2748fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7647c2745f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x7647c2745fd5  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x7647c2745cbb  xla::LRUCache<>::Clear()
    @     0x7647c2745a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7647c2748008  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x7647b8d8845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @           0x45b024  handle_callback.llvm.6155425969336250027
    @          0x1b22206  subtype_dealloc.cold
    @          0x180137f  tupledealloc
    @     0x7647c2748fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7647c2745f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x7647c2746047  absl::lts_20250814::functional_internal::InvokeObject<>()
    @     0x7647bc4a04bf  absl::lts_20250814::container_internal::IterateOverFullSlots()
    @     0x7647c2745ff3  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x7647c2745cbb  xla::LRUCache<>::Clear()
    @     0x7647c2745a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7647c27492a8  std::pair<>::~pair()
    @     0x7647c2744fe8  jax::WeakrefLRUCache::Clear()
    @     0x7647c2747146  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x7647b8d8845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1816073  _PyEval_EvalFrameDefault
    @          0x1ad68ff  atexit_callfuncs.llvm.9450642270383810775.warm
    @          0x190e896  Py_FinalizeEx
    @          0x198c54c  Py_RunMain
    @          0x198c198  pymain_main.llvm.11489439184168853189
    @          0x198bfac  main
    @     0x7647c4a2a601  (unknown)
    @     0x7647c4a2a718  __libc_start_main
    @          0x19a9269  _start
```

### default_gpu_playground_scan_step_vanilla

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_step_modes_default/default_gpu_playground_scan_step_vanilla.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_step_modes_default/default_gpu_playground_scan_step_vanilla.stderr.txt`

```text
t<>::destructor_impl()
    @     0x76d358d560d0  xla::LRUCache<>::Clear()
    @     0x76d358d5a532  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x76d358d56385  std::default_delete<>::operator()()
    @     0x76d358d5aa70  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x76d35558845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @          0x1aac007  PyObject_ClearWeakRefs.warm
    @          0x1a89a88  func_dealloc.warm
    @     0x76d35ef48fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x76d35ef45f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x76d35ef45fd5  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x76d35ef45cbb  xla::LRUCache<>::Clear()
    @     0x76d35ef45a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x76d35ef48008  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x76d35558845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @           0x45b024  handle_callback.llvm.6155425969336250027
    @          0x1b22206  subtype_dealloc.cold
    @          0x180137f  tupledealloc
    @     0x76d35ef48fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x76d35ef45f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x76d35ef46047  absl::lts_20250814::functional_internal::InvokeObject<>()
    @     0x76d358ca04bf  absl::lts_20250814::container_internal::IterateOverFullSlots()
    @     0x76d35ef45ff3  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x76d35ef45cbb  xla::LRUCache<>::Clear()
    @     0x76d35ef45a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x76d35ef492a8  std::pair<>::~pair()
    @     0x76d35ef44fe8  jax::WeakrefLRUCache::Clear()
    @     0x76d35ef47146  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x76d35558845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1816073  _PyEval_EvalFrameDefault
    @          0x1ad68ff  atexit_callfuncs.llvm.9450642270383810775.warm
    @          0x190e896  Py_FinalizeEx
    @          0x198c54c  Py_RunMain
    @          0x198c198  pymain_main.llvm.11489439184168853189
    @          0x198bfac  main
    @     0x76d36122a601  (unknown)
    @     0x76d36122a718  __libc_start_main
    @          0x19a9269  _start
```

## Environment Variants Run

`default`

Supported variants are `default`, `preallocate_false`,
`mem_fraction_050`, `mem_fraction_060`, `allocator_platform`,
`disable_jit`, `debug_nans_infs`, `miopen_fusion_disabled`,
`xla_disable_latency_scheduler`, `xla_disable_triton_gemm`,
and `xla_compiler_conservative`.

## Recommendation

Minimal MJX works, but Playground stepping fails. Inspect Open Duck MJX model features on ROCm.
