# ROCm / MJX Runtime Isolation

gate_result: `HOLD_PLAYGROUND_GPU_STEP`
smallest_failing_subtest: `default_gpu_playground_scan_step_sanitized`

## Executive Summary

- Basic JAX GPU: `NOT_RUN`
- JAX jit/scan GPU: `NOT_RUN`
- Minimal MJX GPU: `NOT_RUN`
- Playground reset GPU: `NOT_RUN`
- Playground one-step GPU: `NOT_RUN`
- Playground one-step JIT GPU: `NOT_RUN`
- Playground scan-step GPU: `NOT_RUN`
- Playground sanitized scan-step GPU: `FAIL`
- Playground bridge GPU: `NOT_RUN`
- Closed-loop GPU: `NOT_RUN`
- Closed-loop CPU: `NOT_RUN`

This is an offline runtime/backend isolation report. No robot commands, SSH,
deployment, or training are involved.

## Matrix

| id | variant | platform | subtest | status | returncode | elapsed_s | progress |
|---|---|---|---|---|---:|---:|---|
| `default_gpu_playground_xml_contact_audit` | `default` | `gpu` | `playground_xml_contact_audit` | `PASS` | `0` | 1.15 | NA |
| `default_gpu_playground_reset_state_finite` | `default` | `gpu` | `playground_reset_state_finite` | `PASS` | `0` | 68.67 | NA |
| `default_gpu_playground_scan_step_sanitized` | `default` | `gpu` | `playground_scan_step_sanitized` | `FAIL` | `-6` | 87.43 | NA |
| `default_cpu_playground_xml_contact_audit` | `default` | `cpu` | `playground_xml_contact_audit` | `PASS` | `0` | 1.12 | NA |
| `default_cpu_playground_reset_state_finite` | `default` | `cpu` | `playground_reset_state_finite` | `PASS` | `0` | 40.64 | NA |
| `default_cpu_playground_scan_step_sanitized` | `default` | `cpu` | `playground_scan_step_sanitized` | `PASS` | `0` | 41.98 | 1:PASS |

## Failing Output Excerpts

### default_gpu_playground_scan_step_sanitized

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_sanitized_state/default_gpu_playground_scan_step_sanitized.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_sanitized_state/default_gpu_playground_scan_step_sanitized.stderr.txt`

```text
t<>::destructor_impl()
    @     0x77a51d9560d0  xla::LRUCache<>::Clear()
    @     0x77a51d95a532  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x77a51d956385  std::default_delete<>::operator()()
    @     0x77a51d95aa70  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x77a51a18845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @          0x1aac007  PyObject_ClearWeakRefs.warm
    @          0x1a89a88  func_dealloc.warm
    @     0x77a523b48fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x77a523b45f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x77a523b45fd5  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x77a523b45cbb  xla::LRUCache<>::Clear()
    @     0x77a523b45a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x77a523b48008  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x77a51a18845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @           0x45b024  handle_callback.llvm.6155425969336250027
    @          0x1b22206  subtype_dealloc.cold
    @          0x180137f  tupledealloc
    @     0x77a523b48fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x77a523b45f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x77a523b46047  absl::lts_20250814::functional_internal::InvokeObject<>()
    @     0x77a51d8a04bf  absl::lts_20250814::container_internal::IterateOverFullSlots()
    @     0x77a523b45ff3  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x77a523b45cbb  xla::LRUCache<>::Clear()
    @     0x77a523b45a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x77a523b492a8  std::pair<>::~pair()
    @     0x77a523b44fe8  jax::WeakrefLRUCache::Clear()
    @     0x77a523b47146  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x77a51a18845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1816073  _PyEval_EvalFrameDefault
    @          0x1ad68ff  atexit_callfuncs.llvm.9450642270383810775.warm
    @          0x190e896  Py_FinalizeEx
    @          0x198c54c  Py_RunMain
    @          0x198c198  pymain_main.llvm.11489439184168853189
    @          0x198bfac  main
    @     0x77a52602a601  (unknown)
    @     0x77a52602a718  __libc_start_main
    @          0x19a9269  _start
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
