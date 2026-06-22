# ROCm / MJX Runtime Isolation

gate_result: `HOLD_PLAYGROUND_GPU_STEP`
smallest_failing_subtest: `default_gpu_playground_one_step_vanilla`

## Executive Summary

- Basic JAX GPU: `PASS`
- JAX jit/scan GPU: `PASS`
- Minimal MJX GPU: `PASS`
- Playground reset GPU: `PASS`
- Playground one-step GPU: `FAIL`
- Playground bridge GPU: `FAIL`
- Closed-loop GPU: `FAIL`
- Closed-loop CPU: `PASS`

This is an offline runtime/backend isolation report. No robot commands, SSH,
deployment, or training are involved.

## Matrix

| id | variant | platform | subtest | status | returncode | elapsed_s | progress |
|---|---|---|---|---|---:|---:|---|
| `default_gpu_basic_jax` | `default` | `gpu` | `basic_jax` | `PASS` | `0` | 1.61 | NA |
| `default_gpu_jax_jit_scan` | `default` | `gpu` | `jax_jit_scan` | `PASS` | `0` | 1.70 | 1:PASS, 2:PASS, 10:PASS, 100:PASS |
| `default_gpu_minimal_mjx_step` | `default` | `gpu` | `minimal_mjx_step` | `PASS` | `0` | 16.91 | 1:PASS, 2:PASS, 10:PASS, 100:PASS |
| `default_gpu_playground_contract_only` | `default` | `gpu` | `playground_contract_only` | `PASS` | `0` | 5.45 | NA |
| `default_gpu_playground_reset` | `default` | `gpu` | `playground_reset` | `PASS` | `0` | 74.36 | NA |
| `default_gpu_playground_one_step_vanilla` | `default` | `gpu` | `playground_one_step_vanilla` | `TIMEOUT` | `None` | 120.35 | NA |
| `default_gpu_playground_multi_step_vanilla` | `default` | `gpu` | `playground_multi_step_vanilla` | `TIMEOUT` | `None` | 120.29 | NA |
| `default_gpu_playground_multi_step_bridge` | `default` | `gpu` | `playground_multi_step_bridge` | `TIMEOUT` | `None` | 120.40 | NA |
| `default_gpu_closed_loop_policy_eval_gpu` | `default` | `gpu` | `closed_loop_policy_eval_gpu` | `FAIL` | `-6` | 112.09 | NA |
| `default_cpu_basic_jax` | `default` | `cpu` | `basic_jax` | `PASS` | `0` | 1.70 | NA |
| `default_cpu_jax_jit_scan` | `default` | `cpu` | `jax_jit_scan` | `PASS` | `0` | 1.75 | 1:PASS, 2:PASS, 10:PASS, 100:PASS |
| `default_cpu_minimal_mjx_step` | `default` | `cpu` | `minimal_mjx_step` | `PASS` | `0` | 13.96 | 1:PASS, 2:PASS, 10:PASS, 100:PASS |
| `default_cpu_playground_contract_only` | `default` | `cpu` | `playground_contract_only` | `PASS` | `0` | 3.60 | NA |
| `default_cpu_playground_reset` | `default` | `cpu` | `playground_reset` | `PASS` | `0` | 70.65 | NA |
| `default_cpu_playground_one_step_vanilla` | `default` | `cpu` | `playground_one_step_vanilla` | `PASS` | `0` | 65.45 | NA |
| `default_cpu_playground_multi_step_vanilla` | `default` | `cpu` | `playground_multi_step_vanilla` | `TIMEOUT` | `None` | 120.33 | 1:PASS, 2:PASS, 10:PASS |
| `default_cpu_playground_multi_step_bridge` | `default` | `cpu` | `playground_multi_step_bridge` | `TIMEOUT` | `None` | 120.27 | 1:HOLD_MODEL_DOES_NOT_REPRODUCE, 2:HOLD_MODEL_DOES_NOT_REPRODUCE, 10:HOLD_MODEL_DOES_NOT_REPRODUCE |
| `default_cpu_closed_loop_policy_eval_cpu` | `default` | `cpu` | `closed_loop_policy_eval_cpu` | `PASS` | `0` | 116.17 | 1:PASS_CLOSED_LOOP_REPRODUCTION, 2:PASS_CLOSED_LOOP_REPRODUCTION, 10:PASS_CLOSED_LOOP_REPRODUCTION, 100:PASS_CLOSED_LOOP_REPRODUCTION |

## Failing Output Excerpts

### default_gpu_playground_one_step_vanilla

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation/default_gpu_playground_one_step_vanilla.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation/default_gpu_playground_one_step_vanilla.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

### default_gpu_playground_multi_step_vanilla

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation/default_gpu_playground_multi_step_vanilla.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation/default_gpu_playground_multi_step_vanilla.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

### default_gpu_playground_multi_step_bridge

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation/default_gpu_playground_multi_step_bridge.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation/default_gpu_playground_multi_step_bridge.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

### default_gpu_closed_loop_policy_eval_gpu

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation/default_gpu_closed_loop_policy_eval_gpu.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation/default_gpu_closed_loop_policy_eval_gpu.stderr.txt`

```text
    @     0x729366156173  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x7293661560d0  xla::LRUCache<>::Clear()
    @     0x72936615a532  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x729366156385  std::default_delete<>::operator()()
    @     0x72936615aa70  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x72936298845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @          0x1aac007  PyObject_ClearWeakRefs.warm
    @          0x1a89a88  func_dealloc.warm
    @     0x72936c348fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x72936c345f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x72936c345fd5  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x72936c345cbb  xla::LRUCache<>::Clear()
    @     0x72936c345a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x72936c348008  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x72936298845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1853754  PyObject_CallOneArg
    @           0x45b024  handle_callback.llvm.6155425969336250027
    @          0x1b22206  subtype_dealloc.cold
    @          0x180137f  tupledealloc
    @     0x72936c348fef  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x72936c345f32  absl::lts_20250814::inlined_vector_internal::Storage<>::DestroyContents()
    @     0x72936c346047  absl::lts_20250814::functional_internal::InvokeObject<>()
    @     0x7293660a04bf  absl::lts_20250814::container_internal::IterateOverFullSlots()
    @     0x72936c345ff3  absl::lts_20250814::container_internal::raw_hash_set<>::destructor_impl()
    @     0x72936c345cbb  xla::LRUCache<>::Clear()
    @     0x72936c345a72  std::_Sp_counted_ptr_inplace<>::_M_dispose()
    @     0x72936c3492a8  std::pair<>::~pair()
    @     0x72936c344fe8  jax::WeakrefLRUCache::Clear()
    @     0x72936c347146  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x72936298845d  nanobind::detail::nb_func_vectorcall_simple_1()
    @          0x1816073  _PyEval_EvalFrameDefault
    @          0x1ad68ff  atexit_callfuncs.llvm.9450642270383810775.warm
    @          0x190e896  Py_FinalizeEx
    @          0x198c54c  Py_RunMain
    @          0x198c198  pymain_main.llvm.11489439184168853189
    @          0x198bfac  main
    @     0x72936e62a601  (unknown)
```

### default_cpu_playground_multi_step_vanilla

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation/default_cpu_playground_multi_step_vanilla.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation/default_cpu_playground_multi_step_vanilla.stderr.txt`

```text
ed in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

### default_cpu_playground_multi_step_bridge

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation/default_cpu_playground_multi_step_bridge.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation/default_cpu_playground_multi_step_bridge.stderr.txt`

```text
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
/home/lsd/robots/envs/open-duck-playground/lib/python3.12/site-packages/jax/_src/abstract_arrays.py:135: RuntimeWarning: overflow encountered in cast
  return literals.TypedNdArray(np.asarray(x, dtype), weak_type=False)
```

## Environment Variants Run

`default`

Supported variants are `default`, `preallocate_false`,
`mem_fraction_050`, `disable_jit`, and `debug_nans_infs`.

## Recommendation

Minimal MJX works, but Playground stepping fails. Inspect Open Duck MJX model features on ROCm.
