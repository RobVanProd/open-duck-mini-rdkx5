# ROCm / MJX Runtime Isolation

gate_result: `HOLD_PLAYGROUND_GPU_STEP`
smallest_failing_subtest: `xla_disable_triton_gemm_softmax_gpu_playground_scan_step_vanilla`

## Executive Summary

- Basic JAX GPU: `NOT_RUN`
- JAX jit/scan GPU: `NOT_RUN`
- Minimal MJX GPU: `NOT_RUN`
- Playground reset GPU: `NOT_RUN`
- Playground one-step GPU: `NOT_RUN`
- Playground one-step JIT GPU: `NOT_RUN`
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
| `xla_disable_triton_gemm_softmax_gpu_playground_scan_step_vanilla` | `xla_disable_triton_gemm_softmax` | `gpu` | `playground_scan_step_vanilla` | `FAIL` | `1` | 0.27 | NA |
| `rocm_strict_ieee_gpu_playground_scan_step_vanilla` | `rocm_strict_ieee` | `gpu` | `playground_scan_step_vanilla` | `FAIL` | `-6` | 58.12 | NA |
| `xla_rocm_data_dir_gpu_playground_scan_step_vanilla` | `xla_rocm_data_dir` | `gpu` | `playground_scan_step_vanilla` | `FAIL` | `1` | 0.32 | NA |
| `xla_triton_strict_ieee_gpu_playground_scan_step_vanilla` | `xla_triton_strict_ieee` | `gpu` | `playground_scan_step_vanilla` | `FAIL` | `1` | 0.30 | NA |

## Failing Output Excerpts

### xla_disable_triton_gemm_softmax_gpu_playground_scan_step_vanilla

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_triton_strict_variants/xla_disable_triton_gemm_softmax_gpu_playground_scan_step_vanilla.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_triton_strict_variants/xla_disable_triton_gemm_softmax_gpu_playground_scan_step_vanilla.stderr.txt`

```text
F0621 23:39:05.948632 1243451 parse_flags_from_env.cc:234] Unknown flag in XLA_FLAGS: --xla_gpu_enable_triton_softmax=false
```

### rocm_strict_ieee_gpu_playground_scan_step_vanilla

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_triton_strict_variants/rocm_strict_ieee_gpu_playground_scan_step_vanilla.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_triton_strict_variants/rocm_strict_ieee_gpu_playground_scan_step_vanilla.stderr.txt`

```text
t<>::destructor_impl()
    @     0x75bd323560d0  xla::LRUCache<>::Clear()
    @     0x75bd3235a532  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x75bd32356385  std::default_delete<>::operator()()
    @     0x75bd3235aa70  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x75bd2eb8845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @          0x1aac007  PyObject_ClearWeakRefs.warm
    @          0x1a89a88  func_dealloc.warm
    @     0x75bd38548fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x75bd38545f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x75bd38545fd5  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x75bd38545cbb  xla::LRUCache<>::Clear()
    @     0x75bd38545a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x75bd38548008  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x75bd2eb8845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @           0x45b024  handle_callback.llvm.6155425969336250027
    @          0x1b22206  subtype_dealloc.cold
    @          0x180137f  tupledealloc
    @     0x75bd38548fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x75bd38545f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x75bd38546047  absl::lts_20250814::functional_internal::InvokeObject<>()
    @     0x75bd322a04bf  absl::lts_20250814::container_internal::IterateOverFullSlots()
    @     0x75bd38545ff3  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x75bd38545cbb  xla::LRUCache<>::Clear()
    @     0x75bd38545a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x75bd385492a8  std::pair<>::~pair()
    @     0x75bd38544fe8  jax::WeakrefLRUCache::Clear()
    @     0x75bd38547146  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x75bd2eb8845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1816073  _PyEval_EvalFrameDefault
    @          0x1ad68ff  atexit_callfuncs.llvm.9450642270383810775.warm
    @          0x190e896  Py_FinalizeEx
    @          0x198c54c  Py_RunMain
    @          0x198c198  pymain_main.llvm.11489439184168853189
    @          0x198bfac  main
    @     0x75bd3a82a601  (unknown)
    @     0x75bd3a82a718  __libc_start_main
    @          0x19a9269  _start
```

### xla_rocm_data_dir_gpu_playground_scan_step_vanilla

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_triton_strict_variants/xla_rocm_data_dir_gpu_playground_scan_step_vanilla.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_triton_strict_variants/xla_rocm_data_dir_gpu_playground_scan_step_vanilla.stderr.txt`

```text
F0621 23:40:04.385664 1244404 parse_flags_from_env.cc:234] Unknown flag in XLA_FLAGS: --xla_gpu_target_cuda_data_dir=/opt/rocm/lib
```

### xla_triton_strict_ieee_gpu_playground_scan_step_vanilla

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_triton_strict_variants/xla_triton_strict_ieee_gpu_playground_scan_step_vanilla.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_triton_strict_variants/xla_triton_strict_ieee_gpu_playground_scan_step_vanilla.stderr.txt`

```text
F0621 23:40:04.690244 1244448 parse_flags_from_env.cc:234] Unknown flags in XLA_FLAGS: --xla_gpu_enable_triton_softmax=false --xla_gpu_target_cuda_data_dir=/opt/rocm/lib
```

## Environment Variants Run

`xla_disable_triton_gemm_softmax`, `rocm_strict_ieee`, `xla_rocm_data_dir`, `xla_triton_strict_ieee`

Supported variants are `default`, `preallocate_false`,
`mem_fraction_050`, `mem_fraction_060`, `allocator_platform`,
`disable_jit`, `debug_nans_infs`, `miopen_fusion_disabled`,
`xla_disable_latency_scheduler`, `xla_disable_triton_gemm`,
`xla_disable_triton_gemm_softmax`, `xla_compiler_conservative`,
`rocm_strict_ieee`, `xla_rocm_data_dir`, and `xla_triton_strict_ieee`.

## Recommendation

Minimal MJX works, but Playground stepping fails. Inspect Open Duck MJX model features on ROCm.
