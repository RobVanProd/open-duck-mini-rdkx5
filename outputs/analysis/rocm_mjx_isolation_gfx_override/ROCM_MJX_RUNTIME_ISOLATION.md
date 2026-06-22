# ROCm / MJX Runtime Isolation

gate_result: `HOLD_BASIC_JAX_GPU`
smallest_failing_subtest: `gfx1100_override_gpu_basic_jax`

## Executive Summary

- Basic JAX GPU: `FAIL`
- JAX jit/scan GPU: `NOT_RUN`
- Minimal MJX GPU: `NOT_RUN`
- Playground reset GPU: `NOT_RUN`
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
| `tensor_parallel_one_gpu_basic_jax` | `tensor_parallel_one` | `gpu` | `basic_jax` | `PASS` | `0` | 1.11 | NA |
| `gfx1100_override_gpu_basic_jax` | `gfx1100_override` | `gpu` | `basic_jax` | `FAIL` | `-6` | 4.42 | NA |
| `gfx1100_mem_safe_gpu_basic_jax` | `gfx1100_mem_safe` | `gpu` | `basic_jax` | `FAIL` | `-6` | 4.45 | NA |

## Failing Output Excerpts

### gfx1100_override_gpu_basic_jax

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_gfx_override/gfx1100_override_gpu_basic_jax.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_gfx_override/gfx1100_override_gpu_basic_jax.stderr.txt`

```text
F0622 00:01:53.645482   21769 rocm_context.cc:137] Check failed: ToStatus(wrap::hipCtxSetCurrent(context_), "Failed setting context") is OK (INTERNAL: Failed setting context: ROCM_ERROR_ILLEGAL_ADDRESS)
[symbolize_elf.inc : 379] RAW: Unable to get high fd: rc=0, limit=1024
*** Check failure stack trace: ***
    @     0x76ba081357a4  absl::lts_20250814::log_internal::LogMessage::SendToLog()
    @     0x76ba08135726  absl::lts_20250814::log_internal::LogMessage::Flush()
    @     0x76ba066baa49  stream_executor::gpu::RocmContext::SetActive()
    @     0x76ba066c6e56  stream_executor::gpu::ScopedActivateContext::ScopedActivateContext()
    @     0x76ba0632f99c  stream_executor::gpu::RocmExecutor::Activate()
    @     0x76ba066befff  stream_executor::gpu::RocmStream::BlockHostUntilDone()
    @     0x76b9fb35c830  xla::LocalDeviceState::SynchronizeAllActivity()
    @     0x76b9fb35c388  xla::LocalDeviceState::~LocalDeviceState()
    @     0x76b9fb35cb7e  xla::LocalDeviceState::~LocalDeviceState()
    @     0x76b9fb2ec79f  std::_Rb_tree<>::_M_erase()
    @     0x76b9fb2e2d1d  std::map<>::~map()
    @     0x76b9fb2e2bb4  xla::GetStreamExecutorGpuClient()
    @     0x76b9fb2d4c24  xla::GetXlaPjrtGpuClient()
    @     0x76b9fb267b0c  pjrt::gpu_plugin::PJRT_Client_Create()
    @     0x76bb6a9d74a4  xla::WrapClientAroundCApi()
    @     0x76bb6a9d717d  xla::GetCApiClient()
    @     0x76bb6a8f1788  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x76bb67188131  nanobind::detail::nb_func_vectorcall_complex()
    @          0x1816073  _PyEval_EvalFrameDefault
    @          0x18503f4  PyObject_Call
    @          0x1894fa4  partial_call
    @          0x185321c  _PyObject_MakeTpCall
    @          0x1816073  _PyEval_EvalFrameDefault
    @          0x1894b95  infinite_lru_cache_wrapper
    @          0x1815ee8  _PyEval_EvalFrameDefault
    @          0x1897ea0  PyEval_EvalCode
    @          0x18ac109  run_mod.llvm.15281556494959932569
    @          0x196bb20  PyRun_SimpleStringFlags
    @          0x1ae2d55  Py_RunMain.warm
    @          0x198c198  pymain_main.llvm.11489439184168853189
    @          0x198bfac  main
    @     0x76bb72e2a601  (unknown)
    @     0x76bb72e2a718  __libc_start_main
    @          0x19a9269  _start
```

### gfx1100_mem_safe_gpu_basic_jax

- stdout: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_gfx_override/gfx1100_mem_safe_gpu_basic_jax.stdout.txt`
- stderr: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/rocm_mjx_isolation_gfx_override/gfx1100_mem_safe_gpu_basic_jax.stderr.txt`

```text
F0622 00:01:58.091830   21876 rocm_context.cc:137] Check failed: ToStatus(wrap::hipCtxSetCurrent(context_), "Failed setting context") is OK (INTERNAL: Failed setting context: ROCM_ERROR_ILLEGAL_ADDRESS)
[symbolize_elf.inc : 379] RAW: Unable to get high fd: rc=0, limit=1024
*** Check failure stack trace: ***
    @     0x794dc6b357a4  absl::lts_20250814::log_internal::LogMessage::SendToLog()
    @     0x794dc6b35726  absl::lts_20250814::log_internal::LogMessage::Flush()
    @     0x794dc50baa49  stream_executor::gpu::RocmContext::SetActive()
    @     0x794dc50c6e56  stream_executor::gpu::ScopedActivateContext::ScopedActivateContext()
    @     0x794dc4d2f99c  stream_executor::gpu::RocmExecutor::Activate()
    @     0x794dc50befff  stream_executor::gpu::RocmStream::BlockHostUntilDone()
    @     0x794db9d5c830  xla::LocalDeviceState::SynchronizeAllActivity()
    @     0x794db9d5c388  xla::LocalDeviceState::~LocalDeviceState()
    @     0x794db9d5cb7e  xla::LocalDeviceState::~LocalDeviceState()
    @     0x794db9cec79f  std::_Rb_tree<>::_M_erase()
    @     0x794db9ce2d1d  std::map<>::~map()
    @     0x794db9ce2bb4  xla::GetStreamExecutorGpuClient()
    @     0x794db9cd4c24  xla::GetXlaPjrtGpuClient()
    @     0x794db9c67b0c  pjrt::gpu_plugin::PJRT_Client_Create()
    @     0x794f291d74a4  xla::WrapClientAroundCApi()
    @     0x794f291d717d  xla::GetCApiClient()
    @     0x794f290f1788  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x794f25988131  nanobind::detail::nb_func_vectorcall_complex()
    @          0x1816073  _PyEval_EvalFrameDefault
    @          0x18503f4  PyObject_Call
    @          0x1894fa4  partial_call
    @          0x185321c  _PyObject_MakeTpCall
    @          0x1816073  _PyEval_EvalFrameDefault
    @          0x1894b95  infinite_lru_cache_wrapper
    @          0x1815ee8  _PyEval_EvalFrameDefault
    @          0x1897ea0  PyEval_EvalCode
    @          0x18ac109  run_mod.llvm.15281556494959932569
    @          0x196bb20  PyRun_SimpleStringFlags
    @          0x1ae2d55  Py_RunMain.warm
    @          0x198c198  pymain_main.llvm.11489439184168853189
    @          0x198bfac  main
    @     0x794f3182a601  (unknown)
    @     0x794f3182a718  __libc_start_main
    @          0x19a9269  _start
```

## Environment Variants Run

`tensor_parallel_one`, `gfx1100_override`, `gfx1100_mem_safe`

Supported variants are `default`, `preallocate_false`,
`mem_fraction_050`, `mem_fraction_060`, `allocator_platform`,
`disable_jit`, `debug_nans_infs`, `tensor_parallel_one`,
`gfx1100_override`, `gfx1100_mem_safe`, `miopen_fusion_disabled`,
`xla_disable_latency_scheduler`, `xla_disable_triton_gemm`,
`xla_disable_triton_gemm_softmax`, `xla_compiler_conservative`,
`rocm_strict_ieee`, `xla_rocm_data_dir`, and `xla_triton_strict_ieee`.

## Recommendation

Fix the local JAX/ROCm install before debugging MuJoCo or Playground.
