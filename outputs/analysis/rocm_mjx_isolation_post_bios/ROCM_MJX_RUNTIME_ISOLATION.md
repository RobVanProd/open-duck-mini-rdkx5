# ROCm / MJX Runtime Isolation

gate_result: `HOLD_PLAYGROUND_GPU_STEP`
smallest_failing_subtest: `default_gpu_playground_direct_mjx_step`

## Executive Summary

- Basic JAX GPU: `PASS`
- JAX jit/scan GPU: `PASS`
- Minimal MJX GPU: `PASS`
- Playground reset GPU: `PASS`
- Playground direct MJX step GPU: `FAIL`
- Playground direct MJX step JIT GPU: `FAIL`
- Playground one-step GPU: `FAIL`
- Playground one-step JIT GPU: `FAIL`
- Playground scan-step GPU: `FAIL`
- Playground sanitized scan-step GPU: `FAIL`
- Playground bridge GPU: `FAIL`
- Closed-loop GPU: `FAIL`
- Closed-loop CPU: `PASS`

This is an offline runtime/backend isolation report. No robot commands, SSH,
deployment, or training are involved.

## Matrix

| id | variant | platform | subtest | status | returncode | elapsed_s | progress |
|---|---|---|---|---|---:|---:|---|
| `default_gpu_basic_jax` | `default` | `gpu` | `basic_jax` | `PASS` | `0` | 1.74 | NA |
| `default_gpu_jax_jit_scan` | `default` | `gpu` | `jax_jit_scan` | `PASS` | `0` | 1.09 | 1:PASS, 2:PASS, 10:PASS |
| `default_gpu_minimal_mjx_step` | `default` | `gpu` | `minimal_mjx_step` | `PASS` | `0` | 9.34 | 1:PASS, 2:PASS, 10:PASS |
| `default_gpu_playground_contract_only` | `default` | `gpu` | `playground_contract_only` | `PASS` | `0` | 2.94 | NA |
| `default_gpu_playground_xml_contact_audit` | `default` | `gpu` | `playground_xml_contact_audit` | `PASS` | `0` | 0.82 | NA |
| `default_gpu_playground_reset` | `default` | `gpu` | `playground_reset` | `PASS` | `0` | 42.42 | NA |
| `default_gpu_playground_reset_state_finite` | `default` | `gpu` | `playground_reset_state_finite` | `PASS` | `0` | 43.55 | NA |
| `default_gpu_playground_direct_mjx_step` | `default` | `gpu` | `playground_direct_mjx_step` | `TIMEOUT` | `None` | 120.17 | NA |
| `default_gpu_playground_direct_mjx_step_jit` | `default` | `gpu` | `playground_direct_mjx_step_jit` | `FAIL` | `-6` | 50.60 | NA |
| `default_gpu_playground_one_step_vanilla` | `default` | `gpu` | `playground_one_step_vanilla` | `TIMEOUT` | `None` | 120.22 | NA |
| `default_gpu_playground_one_step_jit` | `default` | `gpu` | `playground_one_step_jit` | `FAIL` | `-6` | 54.24 | NA |
| `default_gpu_playground_multi_step_vanilla` | `default` | `gpu` | `playground_multi_step_vanilla` | `TIMEOUT` | `None` | 120.15 | NA |
| `default_gpu_playground_scan_step_vanilla` | `default` | `gpu` | `playground_scan_step_vanilla` | `FAIL` | `-6` | 55.19 | NA |
| `default_gpu_playground_scan_step_sanitized` | `default` | `gpu` | `playground_scan_step_sanitized` | `FAIL` | `-6` | 55.82 | NA |
| `default_gpu_playground_multi_step_bridge` | `default` | `gpu` | `playground_multi_step_bridge` | `FAIL` | `-6` | 55.35 | NA |
| `default_gpu_closed_loop_policy_eval_gpu` | `default` | `gpu` | `closed_loop_policy_eval_gpu` | `FAIL` | `-6` | 55.14 | NA |
| `default_cpu_basic_jax` | `default` | `cpu` | `basic_jax` | `PASS` | `0` | 0.89 | NA |
| `default_cpu_jax_jit_scan` | `default` | `cpu` | `jax_jit_scan` | `PASS` | `0` | 0.90 | 1:PASS, 2:PASS, 10:PASS |
| `default_cpu_minimal_mjx_step` | `default` | `cpu` | `minimal_mjx_step` | `PASS` | `0` | 6.26 | 1:PASS, 2:PASS, 10:PASS |
| `default_cpu_playground_contract_only` | `default` | `cpu` | `playground_contract_only` | `PASS` | `0` | 1.99 | NA |
| `default_cpu_playground_xml_contact_audit` | `default` | `cpu` | `playground_xml_contact_audit` | `PASS` | `0` | 0.78 | NA |
| `default_cpu_playground_reset` | `default` | `cpu` | `playground_reset` | `PASS` | `0` | 34.10 | NA |
| `default_cpu_playground_reset_state_finite` | `default` | `cpu` | `playground_reset_state_finite` | `PASS` | `0` | 34.60 | NA |
| `default_cpu_playground_direct_mjx_step` | `default` | `cpu` | `playground_direct_mjx_step` | `PASS` | `0` | 37.54 | NA |
| `default_cpu_playground_direct_mjx_step_jit` | `default` | `cpu` | `playground_direct_mjx_step_jit` | `PASS` | `0` | 37.92 | NA |
| `default_cpu_playground_one_step_vanilla` | `default` | `cpu` | `playground_one_step_vanilla` | `PASS` | `0` | 41.04 | NA |
| `default_cpu_playground_one_step_jit` | `default` | `cpu` | `playground_one_step_jit` | `PASS` | `0` | 38.34 | NA |
| `default_cpu_playground_multi_step_vanilla` | `default` | `cpu` | `playground_multi_step_vanilla` | `PASS` | `0` | 76.84 | 1:PASS, 2:PASS, 10:PASS |
| `default_cpu_playground_scan_step_vanilla` | `default` | `cpu` | `playground_scan_step_vanilla` | `PASS` | `0` | 47.23 | 1:PASS, 2:PASS, 10:PASS |
| `default_cpu_playground_scan_step_sanitized` | `default` | `cpu` | `playground_scan_step_sanitized` | `PASS` | `0` | 49.05 | 1:PASS, 2:PASS, 10:PASS |
| `default_cpu_playground_multi_step_bridge` | `default` | `cpu` | `playground_multi_step_bridge` | `PASS` | `0` | 62.79 | 1:HOLD_MODEL_DOES_NOT_REPRODUCE, 2:HOLD_MODEL_DOES_NOT_REPRODUCE, 10:HOLD_MODEL_DOES_NOT_REPRODUCE |
| `default_cpu_closed_loop_policy_eval_cpu` | `default` | `cpu` | `closed_loop_policy_eval_cpu` | `PASS` | `0` | 62.40 | 1:PASS_CLOSED_LOOP_REPRODUCTION, 2:PASS_CLOSED_LOOP_REPRODUCTION, 10:PASS_CLOSED_LOOP_REPRODUCTION |

## Failing Output Excerpts

### default_gpu_playground_direct_mjx_step

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_post_bios/default_gpu_playground_direct_mjx_step.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_post_bios/default_gpu_playground_direct_mjx_step.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

### default_gpu_playground_direct_mjx_step_jit

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_post_bios/default_gpu_playground_direct_mjx_step_jit.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_post_bios/default_gpu_playground_direct_mjx_step_jit.stderr.txt`

```text
    @     0x782282d56173  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x782282d560d0  xla::LRUCache<>::Clear()
    @     0x782282d5a532  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x782282d56385  std::default_delete<>::operator()()
    @     0x782282d5aa70  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x78227f58845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @          0x1aac007  PyObject_ClearWeakRefs.warm
    @          0x1a89a88  func_dealloc.warm
    @     0x782288f48fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x782288f45f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x782288f45fd5  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x782288f45cbb  xla::LRUCache<>::Clear()
    @     0x782288f45a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x782288f48008  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x78227f58845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @           0x45b024  handle_callback.llvm.6155425969336250027
    @          0x1b22206  subtype_dealloc.cold
    @          0x180137f  tupledealloc
    @     0x782288f48fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x782288f45f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x782288f46047  absl::lts_20250814::functional_internal::InvokeObject<>()
    @     0x782282ca04bf  absl::lts_20250814::container_internal::IterateOverFullSlots()
    @     0x782288f45ff3  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x782288f45cbb  xla::LRUCache<>::Clear()
    @     0x782288f45a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x782288f492a8  std::pair<>::~pair()
    @     0x782288f44fe8  jax::WeakrefLRUCache::Clear()
    @     0x782288f47146  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x78227f58845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1816073  _PyEval_EvalFrameDefault
    @          0x1ad68ff  atexit_callfuncs.llvm.9450642270383810775.warm
    @          0x190e896  Py_FinalizeEx
    @          0x198c54c  Py_RunMain
    @          0x198c198  pymain_main.llvm.11489439184168853189
    @          0x198bfac  main
    @     0x78228b22a601  (unknown)
```

### default_gpu_playground_one_step_vanilla

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_post_bios/default_gpu_playground_one_step_vanilla.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_post_bios/default_gpu_playground_one_step_vanilla.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

### default_gpu_playground_one_step_jit

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_post_bios/default_gpu_playground_one_step_jit.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_post_bios/default_gpu_playground_one_step_jit.stderr.txt`

```text
t<>::destructor_impl()
    @     0x7d938f5560d0  xla::LRUCache<>::Clear()
    @     0x7d938f55a532  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7d938f556385  std::default_delete<>::operator()()
    @     0x7d938f55aa70  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x7d938bd8845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @          0x1aac007  PyObject_ClearWeakRefs.warm
    @          0x1a89a88  func_dealloc.warm
    @     0x7d9395748fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7d9395745f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x7d9395745fd5  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x7d9395745cbb  xla::LRUCache<>::Clear()
    @     0x7d9395745a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7d9395748008  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x7d938bd8845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @           0x45b024  handle_callback.llvm.6155425969336250027
    @          0x1b22206  subtype_dealloc.cold
    @          0x180137f  tupledealloc
    @     0x7d9395748fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7d9395745f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x7d9395746047  absl::lts_20250814::functional_internal::InvokeObject<>()
    @     0x7d938f4a04bf  absl::lts_20250814::container_internal::IterateOverFullSlots()
    @     0x7d9395745ff3  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x7d9395745cbb  xla::LRUCache<>::Clear()
    @     0x7d9395745a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7d93957492a8  std::pair<>::~pair()
    @     0x7d9395744fe8  jax::WeakrefLRUCache::Clear()
    @     0x7d9395747146  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x7d938bd8845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1816073  _PyEval_EvalFrameDefault
    @          0x1ad68ff  atexit_callfuncs.llvm.9450642270383810775.warm
    @          0x190e896  Py_FinalizeEx
    @          0x198c54c  Py_RunMain
    @          0x198c198  pymain_main.llvm.11489439184168853189
    @          0x198bfac  main
    @     0x7d9397a2a601  (unknown)
    @     0x7d9397a2a718  __libc_start_main
    @          0x19a9269  _start
```

### default_gpu_playground_multi_step_vanilla

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_post_bios/default_gpu_playground_multi_step_vanilla.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_post_bios/default_gpu_playground_multi_step_vanilla.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

### default_gpu_playground_scan_step_vanilla

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_post_bios/default_gpu_playground_scan_step_vanilla.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_post_bios/default_gpu_playground_scan_step_vanilla.stderr.txt`

```text
    @     0x721fa9956173  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x721fa99560d0  xla::LRUCache<>::Clear()
    @     0x721fa995a532  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x721fa9956385  std::default_delete<>::operator()()
    @     0x721fa995aa70  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x721fa618845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @          0x1aac007  PyObject_ClearWeakRefs.warm
    @          0x1a89a88  func_dealloc.warm
    @     0x721fafb48fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x721fafb45f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x721fafb45fd5  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x721fafb45cbb  xla::LRUCache<>::Clear()
    @     0x721fafb45a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x721fafb48008  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x721fa618845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @           0x45b024  handle_callback.llvm.6155425969336250027
    @          0x1b22206  subtype_dealloc.cold
    @          0x180137f  tupledealloc
    @     0x721fafb48fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x721fafb45f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x721fafb46047  absl::lts_20250814::functional_internal::InvokeObject<>()
    @     0x721fa98a04bf  absl::lts_20250814::container_internal::IterateOverFullSlots()
    @     0x721fafb45ff3  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x721fafb45cbb  xla::LRUCache<>::Clear()
    @     0x721fafb45a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x721fafb492a8  std::pair<>::~pair()
    @     0x721fafb44fe8  jax::WeakrefLRUCache::Clear()
    @     0x721fafb47146  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x721fa618845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1816073  _PyEval_EvalFrameDefault
    @          0x1ad68ff  atexit_callfuncs.llvm.9450642270383810775.warm
    @          0x190e896  Py_FinalizeEx
    @          0x198c54c  Py_RunMain
    @          0x198c198  pymain_main.llvm.11489439184168853189
    @          0x198bfac  main
    @     0x721fb202a601  (unknown)
```

### default_gpu_playground_scan_step_sanitized

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_post_bios/default_gpu_playground_scan_step_sanitized.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_post_bios/default_gpu_playground_scan_step_sanitized.stderr.txt`

```text
t<>::destructor_impl()
    @     0x70e3915560d0  xla::LRUCache<>::Clear()
    @     0x70e39155a532  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x70e391556385  std::default_delete<>::operator()()
    @     0x70e39155aa70  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x70e38dd8845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @          0x1aac007  PyObject_ClearWeakRefs.warm
    @          0x1a89a88  func_dealloc.warm
    @     0x70e397748fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x70e397745f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x70e397745fd5  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x70e397745cbb  xla::LRUCache<>::Clear()
    @     0x70e397745a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x70e397748008  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x70e38dd8845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @           0x45b024  handle_callback.llvm.6155425969336250027
    @          0x1b22206  subtype_dealloc.cold
    @          0x180137f  tupledealloc
    @     0x70e397748fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x70e397745f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x70e397746047  absl::lts_20250814::functional_internal::InvokeObject<>()
    @     0x70e3914a04bf  absl::lts_20250814::container_internal::IterateOverFullSlots()
    @     0x70e397745ff3  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x70e397745cbb  xla::LRUCache<>::Clear()
    @     0x70e397745a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x70e3977492a8  std::pair<>::~pair()
    @     0x70e397744fe8  jax::WeakrefLRUCache::Clear()
    @     0x70e397747146  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x70e38dd8845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1816073  _PyEval_EvalFrameDefault
    @          0x1ad68ff  atexit_callfuncs.llvm.9450642270383810775.warm
    @          0x190e896  Py_FinalizeEx
    @          0x198c54c  Py_RunMain
    @          0x198c198  pymain_main.llvm.11489439184168853189
    @          0x198bfac  main
    @     0x70e399a2a601  (unknown)
    @     0x70e399a2a718  __libc_start_main
    @          0x19a9269  _start
```

### default_gpu_playground_multi_step_bridge

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_post_bios/default_gpu_playground_multi_step_bridge.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_post_bios/default_gpu_playground_multi_step_bridge.stderr.txt`

```text
    @     0x772393d56173  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x772393d560d0  xla::LRUCache<>::Clear()
    @     0x772393d5a532  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x772393d56385  std::default_delete<>::operator()()
    @     0x772393d5aa70  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x77239058845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @          0x1aac007  PyObject_ClearWeakRefs.warm
    @          0x1a89a88  func_dealloc.warm
    @     0x772399f48fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x772399f45f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x772399f45fd5  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x772399f45cbb  xla::LRUCache<>::Clear()
    @     0x772399f45a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x772399f48008  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x77239058845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @           0x45b024  handle_callback.llvm.6155425969336250027
    @          0x1b22206  subtype_dealloc.cold
    @          0x180137f  tupledealloc
    @     0x772399f48fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x772399f45f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x772399f46047  absl::lts_20250814::functional_internal::InvokeObject<>()
    @     0x772393ca04bf  absl::lts_20250814::container_internal::IterateOverFullSlots()
    @     0x772399f45ff3  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x772399f45cbb  xla::LRUCache<>::Clear()
    @     0x772399f45a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x772399f492a8  std::pair<>::~pair()
    @     0x772399f44fe8  jax::WeakrefLRUCache::Clear()
    @     0x772399f47146  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x77239058845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1816073  _PyEval_EvalFrameDefault
    @          0x1ad68ff  atexit_callfuncs.llvm.9450642270383810775.warm
    @          0x190e896  Py_FinalizeEx
    @          0x198c54c  Py_RunMain
    @          0x198c198  pymain_main.llvm.11489439184168853189
    @          0x198bfac  main
    @     0x77239c22a601  (unknown)
```

### default_gpu_closed_loop_policy_eval_gpu

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_post_bios/default_gpu_closed_loop_policy_eval_gpu.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_post_bios/default_gpu_closed_loop_policy_eval_gpu.stderr.txt`

```text
t<>::destructor_impl()
    @     0x7eb5183560d0  xla::LRUCache<>::Clear()
    @     0x7eb51835a532  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7eb518356385  std::default_delete<>::operator()()
    @     0x7eb51835aa70  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x7eb514b8845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @          0x1aac007  PyObject_ClearWeakRefs.warm
    @          0x1a89a88  func_dealloc.warm
    @     0x7eb51e548fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7eb51e545f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x7eb51e545fd5  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x7eb51e545cbb  xla::LRUCache<>::Clear()
    @     0x7eb51e545a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7eb51e548008  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x7eb514b8845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @           0x45b024  handle_callback.llvm.6155425969336250027
    @          0x1b22206  subtype_dealloc.cold
    @          0x180137f  tupledealloc
    @     0x7eb51e548fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7eb51e545f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x7eb51e546047  absl::lts_20250814::functional_internal::InvokeObject<>()
    @     0x7eb5182a04bf  absl::lts_20250814::container_internal::IterateOverFullSlots()
    @     0x7eb51e545ff3  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x7eb51e545cbb  xla::LRUCache<>::Clear()
    @     0x7eb51e545a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x7eb51e5492a8  std::pair<>::~pair()
    @     0x7eb51e544fe8  jax::WeakrefLRUCache::Clear()
    @     0x7eb51e547146  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x7eb514b8845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1816073  _PyEval_EvalFrameDefault
    @          0x1ad68ff  atexit_callfuncs.llvm.9450642270383810775.warm
    @          0x190e896  Py_FinalizeEx
    @          0x198c54c  Py_RunMain
    @          0x198c198  pymain_main.llvm.11489439184168853189
    @          0x198bfac  main
    @     0x7eb520a2a601  (unknown)
    @     0x7eb520a2a718  __libc_start_main
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
