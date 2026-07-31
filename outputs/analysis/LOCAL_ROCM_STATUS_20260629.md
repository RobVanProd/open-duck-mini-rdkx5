# Local ROCm Status

status: `PASS_LOCAL_ROCM_READY`
timestamp: `20260629T074808Z`

This read-only check did not train, SSH, deploy, change runtime
behavior, or touch the robot.

## Summary

| check | result |
|---|---|
| rocminfo default | `PASS` |
| rocminfo /dev/kfd failure | `False` |
| JAX default GPU visible | `True` |
| JAX CPU fallback | `PASS` |

## rocminfo Variants

### default

returncode: `0`

```text
ROCk module is loaded
=====================
HSA System Attributes
=====================
Runtime Version:         1.21
Runtime Ext Version:     1.21
System Timestamp Freq.:  1000.000000MHz
Sig. Max Wait Duration:  18446744073709551615 (0xFFFFFFFFFFFFFFFF) (timestamp count)
Machine Model:           LARGE
System Endianness:       LITTLE
Mwaitx:                  ENABLED
XNACK enabled:           NO
DMAbuf Support:          YES
VMM Support:             YES

==========
HSA Agents
==========
*******
Agent 1
*******
  Name:                    AMD Ryzen 9 9950X 16-Core Processor
  Uuid:                    CPU-XX
  Marketing Name:          AMD Ryzen 9 9950X 16-Core Processor
  Vendor Name:             CPU
  Feature:                 None specified
  Profile:                 FULL_PROFILE
  Float Round Mode:        NEAR
  Max Queue Number:        0(0x0)
  Queue Min Size:          0(0x0)
  Queue Max Size:          0(0x0)
  Queue Type:              MULTI
  Node:                    0
  Device Type:             CPU
  Cache Info:
    L1:                      49152(0xc000) KB
  Chip ID:                 0(0x0)
  ASIC Revision:           0(0x0)
  Cacheline Size:          64(0x40)
  Max Clock Freq. (MHz):   5756
  BDFID:                   0
  Internal Node ID:        0
  Compute Unit:            32
  SIMDs per CU:            0
  Shader Engines:          0
  Shader Arrs. per Eng.:   0
  WatchPts on Addr. Ranges:1
  Memory Properties:
  Features:                None
  Pool Info:
    Pool 1
      Segment:                 GLOBAL; FLAGS: FINE GRAINED
      Size:                    127127216(0x793ceb0) KB
      Allocatable:             TRUE
      Alloc Granule:           4KB
      Alloc Recommended Granule:4KB
      Alloc Alignment:         4KB
      Accessible by all:       TRUE
    Pool 2
      Segment:                 GLOBAL; FLAGS: EXTENDED FINE GRAINED
      Size:                    127127216(0x793ceb0) KB
      Allocatable:             TRUE
      Alloc Granule:           4KB
      Alloc Recommended Granule:4KB
      Alloc Alignment:         4KB
      Accessible by all:       TRUE
    Pool 3
      Segment:                 GLOBAL; FLAGS: KERNARG, FINE GRAINED
      Size:                    127127216(0x793ceb0) KB
      Allocatable:             TRUE
      Alloc Granule:           4KB
      Alloc Recommended Granule:4KB
      Alloc Alignment:         4KB
      Accessible by all:       TRUE
    Pool 4
      Segment:                 GLOBAL; FLAGS: COARSE GRAINED
      Size:                    127127216(0x793ceb0) KB
      Allocatable:             TRUE
      Alloc Granule:           4KB
      Alloc Recommended Granule:4KB
... truncated 231 lines ...
```

### opt_rocm_path

returncode: `0`

```text
ROCk module is loaded
=====================
HSA System Attributes
=====================
Runtime Version:         1.21
Runtime Ext Version:     1.21
System Timestamp Freq.:  1000.000000MHz
Sig. Max Wait Duration:  18446744073709551615 (0xFFFFFFFFFFFFFFFF) (timestamp count)
Machine Model:           LARGE
System Endianness:       LITTLE
Mwaitx:                  ENABLED
XNACK enabled:           NO
DMAbuf Support:          YES
VMM Support:             YES

==========
HSA Agents
==========
*******
Agent 1
*******
  Name:                    AMD Ryzen 9 9950X 16-Core Processor
  Uuid:                    CPU-XX
  Marketing Name:          AMD Ryzen 9 9950X 16-Core Processor
  Vendor Name:             CPU
  Feature:                 None specified
  Profile:                 FULL_PROFILE
  Float Round Mode:        NEAR
  Max Queue Number:        0(0x0)
  Queue Min Size:          0(0x0)
  Queue Max Size:          0(0x0)
  Queue Type:              MULTI
  Node:                    0
  Device Type:             CPU
  Cache Info:
    L1:                      49152(0xc000) KB
  Chip ID:                 0(0x0)
  ASIC Revision:           0(0x0)
  Cacheline Size:          64(0x40)
  Max Clock Freq. (MHz):   5756
  BDFID:                   0
  Internal Node ID:        0
  Compute Unit:            32
  SIMDs per CU:            0
  Shader Engines:          0
  Shader Arrs. per Eng.:   0
  WatchPts on Addr. Ranges:1
  Memory Properties:
  Features:                None
  Pool Info:
    Pool 1
      Segment:                 GLOBAL; FLAGS: FINE GRAINED
      Size:                    127127216(0x793ceb0) KB
      Allocatable:             TRUE
      Alloc Granule:           4KB
      Alloc Recommended Granule:4KB
      Alloc Alignment:         4KB
      Accessible by all:       TRUE
    Pool 2
      Segment:                 GLOBAL; FLAGS: EXTENDED FINE GRAINED
      Size:                    127127216(0x793ceb0) KB
      Allocatable:             TRUE
      Alloc Granule:           4KB
      Alloc Recommended Granule:4KB
      Alloc Alignment:         4KB
      Accessible by all:       TRUE
    Pool 3
      Segment:                 GLOBAL; FLAGS: KERNARG, FINE GRAINED
      Size:                    127127216(0x793ceb0) KB
      Allocatable:             TRUE
      Alloc Granule:           4KB
      Alloc Recommended Granule:4KB
      Alloc Alignment:         4KB
      Accessible by all:       TRUE
    Pool 4
      Segment:                 GLOBAL; FLAGS: COARSE GRAINED
      Size:                    127127216(0x793ceb0) KB
      Allocatable:             TRUE
      Alloc Granule:           4KB
      Alloc Recommended Granule:4KB
... truncated 231 lines ...
```

### hsa_override

returncode: `0`

```text
ROCk module is loaded
=====================
HSA System Attributes
=====================
Runtime Version:         1.21
Runtime Ext Version:     1.21
System Timestamp Freq.:  1000.000000MHz
Sig. Max Wait Duration:  18446744073709551615 (0xFFFFFFFFFFFFFFFF) (timestamp count)
Machine Model:           LARGE
System Endianness:       LITTLE
Mwaitx:                  ENABLED
XNACK enabled:           NO
DMAbuf Support:          YES
VMM Support:             YES

==========
HSA Agents
==========
*******
Agent 1
*******
  Name:                    AMD Ryzen 9 9950X 16-Core Processor
  Uuid:                    CPU-XX
  Marketing Name:          AMD Ryzen 9 9950X 16-Core Processor
  Vendor Name:             CPU
  Feature:                 None specified
  Profile:                 FULL_PROFILE
  Float Round Mode:        NEAR
  Max Queue Number:        0(0x0)
  Queue Min Size:          0(0x0)
  Queue Max Size:          0(0x0)
  Queue Type:              MULTI
  Node:                    0
  Device Type:             CPU
  Cache Info:
    L1:                      49152(0xc000) KB
  Chip ID:                 0(0x0)
  ASIC Revision:           0(0x0)
  Cacheline Size:          64(0x40)
  Max Clock Freq. (MHz):   5756
  BDFID:                   0
  Internal Node ID:        0
  Compute Unit:            32
  SIMDs per CU:            0
  Shader Engines:          0
  Shader Arrs. per Eng.:   0
  WatchPts on Addr. Ranges:1
  Memory Properties:
  Features:                None
  Pool Info:
    Pool 1
      Segment:                 GLOBAL; FLAGS: FINE GRAINED
      Size:                    127127216(0x793ceb0) KB
      Allocatable:             TRUE
      Alloc Granule:           4KB
      Alloc Recommended Granule:4KB
      Alloc Alignment:         4KB
      Accessible by all:       TRUE
    Pool 2
      Segment:                 GLOBAL; FLAGS: EXTENDED FINE GRAINED
      Size:                    127127216(0x793ceb0) KB
      Allocatable:             TRUE
      Alloc Granule:           4KB
      Alloc Recommended Granule:4KB
      Alloc Alignment:         4KB
      Accessible by all:       TRUE
    Pool 3
      Segment:                 GLOBAL; FLAGS: KERNARG, FINE GRAINED
      Size:                    127127216(0x793ceb0) KB
      Allocatable:             TRUE
      Alloc Granule:           4KB
      Alloc Recommended Granule:4KB
      Alloc Alignment:         4KB
      Accessible by all:       TRUE
    Pool 4
      Segment:                 GLOBAL; FLAGS: COARSE GRAINED
      Size:                    127127216(0x793ceb0) KB
      Allocatable:             TRUE
      Alloc Granule:           4KB
      Alloc Recommended Granule:4KB
... truncated 231 lines ...
```

### opt_rocm_path_hsa_override

returncode: `0`

```text
ROCk module is loaded
=====================
HSA System Attributes
=====================
Runtime Version:         1.21
Runtime Ext Version:     1.21
System Timestamp Freq.:  1000.000000MHz
Sig. Max Wait Duration:  18446744073709551615 (0xFFFFFFFFFFFFFFFF) (timestamp count)
Machine Model:           LARGE
System Endianness:       LITTLE
Mwaitx:                  ENABLED
XNACK enabled:           NO
DMAbuf Support:          YES
VMM Support:             YES

==========
HSA Agents
==========
*******
Agent 1
*******
  Name:                    AMD Ryzen 9 9950X 16-Core Processor
  Uuid:                    CPU-XX
  Marketing Name:          AMD Ryzen 9 9950X 16-Core Processor
  Vendor Name:             CPU
  Feature:                 None specified
  Profile:                 FULL_PROFILE
  Float Round Mode:        NEAR
  Max Queue Number:        0(0x0)
  Queue Min Size:          0(0x0)
  Queue Max Size:          0(0x0)
  Queue Type:              MULTI
  Node:                    0
  Device Type:             CPU
  Cache Info:
    L1:                      49152(0xc000) KB
  Chip ID:                 0(0x0)
  ASIC Revision:           0(0x0)
  Cacheline Size:          64(0x40)
  Max Clock Freq. (MHz):   5756
  BDFID:                   0
  Internal Node ID:        0
  Compute Unit:            32
  SIMDs per CU:            0
  Shader Engines:          0
  Shader Arrs. per Eng.:   0
  WatchPts on Addr. Ranges:1
  Memory Properties:
  Features:                None
  Pool Info:
    Pool 1
      Segment:                 GLOBAL; FLAGS: FINE GRAINED
      Size:                    127127216(0x793ceb0) KB
      Allocatable:             TRUE
      Alloc Granule:           4KB
      Alloc Recommended Granule:4KB
      Alloc Alignment:         4KB
      Accessible by all:       TRUE
    Pool 2
      Segment:                 GLOBAL; FLAGS: EXTENDED FINE GRAINED
      Size:                    127127216(0x793ceb0) KB
      Allocatable:             TRUE
      Alloc Granule:           4KB
      Alloc Recommended Granule:4KB
      Alloc Alignment:         4KB
      Accessible by all:       TRUE
    Pool 3
      Segment:                 GLOBAL; FLAGS: KERNARG, FINE GRAINED
      Size:                    127127216(0x793ceb0) KB
      Allocatable:             TRUE
      Alloc Granule:           4KB
      Alloc Recommended Granule:4KB
      Alloc Alignment:         4KB
      Accessible by all:       TRUE
    Pool 4
      Segment:                 GLOBAL; FLAGS: COARSE GRAINED
      Size:                    127127216(0x793ceb0) KB
      Allocatable:             TRUE
      Alloc Granule:           4KB
      Alloc Recommended Granule:4KB
... truncated 231 lines ...
```

## JAX Variants

### default

returncode: `0`

```text
python /home/lsd/robots/open-duck-mini-rdkx5/../envs/open-duck-playground/bin/python
jax 0.8.2
backend gpu
devices [RocmDevice(id=0)]
mujoco 3.9.0
```

### opt_rocm_path

returncode: `0`

```text
python /home/lsd/robots/open-duck-mini-rdkx5/../envs/open-duck-playground/bin/python
LD_LIBRARY_PATH /opt/rocm-7.2.1/lib
jax 0.8.2
backend gpu
devices [RocmDevice(id=0)]
mujoco 3.9.0
```

### hsa_override

returncode: `-6`

```text
F0629 03:48:14.635880  678886 rocm_context.cc:137] Check failed: ToStatus(wrap::hipCtxSetCurrent(context_), "Failed setting context") is OK (INTERNAL: Failed setting context: ROCM_ERROR_ILLEGAL_ADDRESS)
[symbolize_elf.inc : 379] RAW: Unable to get high fd: rc=0, limit=1024
*** Check failure stack trace: ***
    @     0x7465095357a4  absl::lts_20250814::log_internal::LogMessage::SendToLog()
    @     0x746509535726  absl::lts_20250814::log_internal::LogMessage::Flush()
    @     0x746507abaa49  stream_executor::gpu::RocmContext::SetActive()
    @     0x746507ac6e56  stream_executor::gpu::ScopedActivateContext::ScopedActivateContext()
    @     0x74650772f99c  stream_executor::gpu::RocmExecutor::Activate()
    @     0x746507abefff  stream_executor::gpu::RocmStream::BlockHostUntilDone()
    @     0x7464fc75c830  xla::LocalDeviceState::SynchronizeAllActivity()
    @     0x7464fc75c388  xla::LocalDeviceState::~LocalDeviceState()
    @     0x7464fc75cb7e  xla::LocalDeviceState::~LocalDeviceState()
    @     0x7464fc6ec79f  std::_Rb_tree<>::_M_erase()
    @     0x7464fc6e2d1d  std::map<>::~map()
    @     0x7464fc6e2bb4  xla::GetStreamExecutorGpuClient()
    @     0x7464fc6d4c24  xla::GetXlaPjrtGpuClient()
    @     0x7464fc667b0c  pjrt::gpu_plugin::PJRT_Client_Create()
    @     0x746719dd74a4  xla::WrapClientAroundCApi()
    @     0x746719dd717d  xla::GetCApiClient()
    @     0x746719cf1788  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x746716588131  nanobind::detail::nb_func_vectorcall_complex()
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
    @     0x74672222a601  (unknown)
    @     0x74672222a718  __libc_start_main
    @          0x19a9269  _start
```

### opt_rocm_path_hsa_override

returncode: `-6`

```text
F0629 03:48:19.112580  679025 rocm_context.cc:137] Check failed: ToStatus(wrap::hipCtxSetCurrent(context_), "Failed setting context") is OK (INTERNAL: Failed setting context: ROCM_ERROR_ILLEGAL_ADDRESS)
[symbolize_elf.inc : 379] RAW: Unable to get high fd: rc=0, limit=1024
*** Check failure stack trace: ***
    @     0x7f722ab357a4  absl::lts_20250814::log_internal::LogMessage::SendToLog()
    @     0x7f722ab35726  absl::lts_20250814::log_internal::LogMessage::Flush()
    @     0x7f72290baa49  stream_executor::gpu::RocmContext::SetActive()
    @     0x7f72290c6e56  stream_executor::gpu::ScopedActivateContext::ScopedActivateContext()
    @     0x7f7228d2f99c  stream_executor::gpu::RocmExecutor::Activate()
    @     0x7f72290befff  stream_executor::gpu::RocmStream::BlockHostUntilDone()
    @     0x7f721dd5c830  xla::LocalDeviceState::SynchronizeAllActivity()
    @     0x7f721dd5c388  xla::LocalDeviceState::~LocalDeviceState()
    @     0x7f721dd5cb7e  xla::LocalDeviceState::~LocalDeviceState()
    @     0x7f721dcec79f  std::_Rb_tree<>::_M_erase()
    @     0x7f721dce2d1d  std::map<>::~map()
    @     0x7f721dce2bb4  xla::GetStreamExecutorGpuClient()
    @     0x7f721dcd4c24  xla::GetXlaPjrtGpuClient()
    @     0x7f721dc67b0c  pjrt::gpu_plugin::PJRT_Client_Create()
    @     0x7f743b3d74a4  xla::WrapClientAroundCApi()
    @     0x7f743b3d717d  xla::GetCApiClient()
    @     0x7f743b2f1788  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x7f7437b88131  nanobind::detail::nb_func_vectorcall_complex()
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
    @     0x7f744382a601  (unknown)
    @     0x7f744382a718  __libc_start_main
    @          0x19a9269  _start
```

### cpu

returncode: `0`

```text
python /home/lsd/robots/open-duck-mini-rdkx5/../envs/open-duck-playground/bin/python
JAX_PLATFORMS cpu
JAX_PLATFORM_NAME cpu
jax 0.8.2
backend cpu
devices [CpuDevice(id=0)]
mujoco 3.9.0
```

## System Evidence

### Device Nodes

```text
crw-rw----+   1 root render 226, 128 Jun 28 06:22 /dev/dri/renderD128
crw-rw----+   1 root render 226, 129 Jun 28 06:22 /dev/dri/renderD129
crw-rw----+   1 root render 511,   0 Jun 28 06:22 /dev/kfd
```

### ROCm Packages

```text
amdgpu-core 1:7.2.70201-2303469.24.04
amdgpu-dkms 1:6.16.13.30300100-2303411.24.04
amdgpu-dkms-firmware 30.30.1.0.30300100-2303411.24.04
amdgpu-install 30.30.1.0.30300100-2303411.24.04
amdgpu-lib 1:7.2.70201-2303469.24.04
amdgpu-lib32 1:7.2.70201-2303469.24.04
amdgpu-multimedia 1:7.2.70201-2303469.24.04
libamdhip64-5
libamdhip64-7 7.1.0-0ubuntu2
libhsa-runtime64-1 7.1.0+dfsg-0ubuntu9
libhsakmt1 7.1.0+dfsg-0ubuntu9
rocm-opencl-icd
```

### ROCm Library Paths

```text
libhsakmt.so.1 (libc6,x86-64) => /usr/lib/x86_64-linux-gnu/libhsakmt.so.1
	libhsa-runtime64.so.1 (libc6,x86-64) => /usr/lib/x86_64-linux-gnu/libhsa-runtime64.so.1
	libamdhip64.so.7 (libc6,x86-64) => /usr/lib/x86_64-linux-gnu/libamdhip64.so.7
```

### Recent Kernel GPU Lines

```text
Jun 29 02:20:43 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.2.0 uses VM inv eng 6 on hub 0
Jun 29 02:20:43 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.3.0 uses VM inv eng 7 on hub 0
Jun 29 02:20:43 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.0.1 uses VM inv eng 8 on hub 0
Jun 29 02:20:43 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.1.1 uses VM inv eng 9 on hub 0
Jun 29 02:20:43 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.2.1 uses VM inv eng 10 on hub 0
Jun 29 02:20:43 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.3.1 uses VM inv eng 11 on hub 0
Jun 29 02:20:43 LSD kernel: amdgpu 0000:04:00.0: ring sdma0 uses VM inv eng 12 on hub 0
Jun 29 02:20:43 LSD kernel: amdgpu 0000:04:00.0: ring sdma1 uses VM inv eng 13 on hub 0
Jun 29 02:20:43 LSD kernel: amdgpu 0000:04:00.0: ring vcn_unified_0 uses VM inv eng 0 on hub 8
Jun 29 02:20:43 LSD kernel: amdgpu 0000:04:00.0: ring vcn_unified_1 uses VM inv eng 1 on hub 8
Jun 29 02:20:43 LSD kernel: amdgpu 0000:04:00.0: ring jpeg_dec uses VM inv eng 4 on hub 8
Jun 29 02:20:43 LSD kernel: amdgpu 0000:04:00.0: ring mes_kiq_3.1.0 uses VM inv eng 14 on hub 0
Jun 29 02:20:43 LSD kernel: amdgpu 0000:04:00.0: [drm] Cannot find any crtc or sizes
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: [drm] PCIE GART of 512M enabled (table at 0x00000085FEB00000).
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: PSP is resuming...
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: reserve 0x1300000 from 0x85fc000000 for PSP TMR
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: RAP: optional rap ta ucode is not available
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: SECUREDISPLAY: optional securedisplay ta ucode is not available
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: SMU is resuming...
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: smu driver if version = 0x0000003d, smu fw if version = 0x00000040, smu fw program = 0, smu fw version = 0x004e8300 (78.131.0)
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: SMU driver if version not matched
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: SMU is resumed successfully!
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: [drm] DMUB hardware initialized: version=0x07002F00
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: [drm] Cannot find any crtc or sizes
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: ring gfx_0.0.0 uses VM inv eng 0 on hub 0
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.0.0 uses VM inv eng 1 on hub 0
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.1.0 uses VM inv eng 4 on hub 0
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.2.0 uses VM inv eng 6 on hub 0
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.3.0 uses VM inv eng 7 on hub 0
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.0.1 uses VM inv eng 8 on hub 0
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.1.1 uses VM inv eng 9 on hub 0
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.2.1 uses VM inv eng 10 on hub 0
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.3.1 uses VM inv eng 11 on hub 0
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: ring sdma0 uses VM inv eng 12 on hub 0
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: ring sdma1 uses VM inv eng 13 on hub 0
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: ring vcn_unified_0 uses VM inv eng 0 on hub 8
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: ring vcn_unified_1 uses VM inv eng 1 on hub 8
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: ring jpeg_dec uses VM inv eng 4 on hub 8
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: ring mes_kiq_3.1.0 uses VM inv eng 14 on hub 0
Jun 29 03:32:45 LSD kernel: amdgpu 0000:04:00.0: [drm] Cannot find any crtc or sizes
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: [drm] PCIE GART of 512M enabled (table at 0x00000085FEB00000).
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: PSP is resuming...
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: reserve 0x1300000 from 0x85fc000000 for PSP TMR
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: RAP: optional rap ta ucode is not available
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: SECUREDISPLAY: optional securedisplay ta ucode is not available
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: SMU is resuming...
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: smu driver if version = 0x0000003d, smu fw if version = 0x00000040, smu fw program = 0, smu fw version = 0x004e8300 (78.131.0)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: SMU driver if version not matched
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: SMU is resumed successfully!
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: [drm] DMUB hardware initialized: version=0x07002F00
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: [drm] Cannot find any crtc or sizes
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: ring gfx_0.0.0 uses VM inv eng 0 on hub 0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.0.0 uses VM inv eng 1 on hub 0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.1.0 uses VM inv eng 4 on hub 0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.2.0 uses VM inv eng 6 on hub 0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.3.0 uses VM inv eng 7 on hub 0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.0.1 uses VM inv eng 8 on hub 0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.1.1 uses VM inv eng 9 on hub 0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.2.1 uses VM inv eng 10 on hub 0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.3.1 uses VM inv eng 11 on hub 0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: ring sdma0 uses VM inv eng 12 on hub 0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: ring sdma1 uses VM inv eng 13 on hub 0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: ring vcn_unified_0 uses VM inv eng 0 on hub 8
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: ring vcn_unified_1 uses VM inv eng 1 on hub 8
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: ring jpeg_dec uses VM inv eng 4 on hub 8
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: ring mes_kiq_3.1.0 uses VM inv eng 14 on hub 0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:04:00.0: [drm] Cannot find any crtc or sizes
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0: [gfxhub] page fault (src_id:0 ring:24 vmid:8 pasid:319)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:  Process python pid 668369 thread python pid 668369
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:   in page starting at address 0x00007fb625910000 from client 0x1b (UTCL2)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0: GCVM_L2_PROTECTION_FAULT_STATUS:0x00801431
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:          Faulty UTCL2 client ID: SQC (data) (0xa)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:          MORE_FAULTS: 0x1
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:          WALKER_ERROR: 0x0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:          PERMISSION_FAULTS: 0x3
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:          MAPPING_ERROR: 0x0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:          RW: 0x0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0: [gfxhub] page fault (src_id:0 ring:24 vmid:8 pasid:319)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:  Process python pid 668369 thread python pid 668369
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:   in page starting at address 0x00007fb61a2a8000 from client 0x1b (UTCL2)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0: GCVM_L2_PROTECTION_FAULT_STATUS:0x00801230
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:          Faulty UTCL2 client ID: SQC (inst) (0x9)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:          MORE_FAULTS: 0x0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:          WALKER_ERROR: 0x0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:          PERMISSION_FAULTS: 0x3
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:          MAPPING_ERROR: 0x0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:          RW: 0x0
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0: [gfxhub] page fault (src_id:0 ring:24 vmid:8 pasid:319)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:  Process python pid 668369 thread python pid 668369
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:   in page starting at address 0x00007fb6047f9000 from client 0x1b (UTCL2)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0: [gfxhub] page fault (src_id:0 ring:24 vmid:8 pasid:319)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:  Process python pid 668369 thread python pid 668369
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:   in page starting at address 0x00007fb608de5000 from client 0x1b (UTCL2)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0: [gfxhub] page fault (src_id:0 ring:24 vmid:8 pasid:319)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:  Process python pid 668369 thread python pid 668369
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:   in page starting at address 0x00007fb604fef000 from client 0x1b (UTCL2)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0: [gfxhub] page fault (src_id:0 ring:24 vmid:8 pasid:319)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:  Process python pid 668369 thread python pid 668369
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:   in page starting at address 0x00007fb64550e000 from client 0x1b (UTCL2)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0: [gfxhub] page fault (src_id:0 ring:24 vmid:8 pasid:319)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:  Process python pid 668369 thread python pid 668369
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:   in page starting at address 0x00007fb6b4b2f000 from client 0x1b (UTCL2)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0: [gfxhub] page fault (src_id:0 ring:24 vmid:8 pasid:319)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:  Process python pid 668369 thread python pid 668369
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:   in page starting at address 0x00007fb6873f7000 from client 0x1b (UTCL2)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0: [gfxhub] page fault (src_id:0 ring:24 vmid:8 pasid:319)
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:  Process python pid 668369 thread python pid 668369
Jun 29 03:34:02 LSD kernel: amdgpu 0000:7c:00.0:   in page starting at address 0x00007fb856e3e000 from client 0x1b (UTCL2)
Jun 29 03:34:06 LSD kernel: amdgpu 0000:7c:00.0: Queue preemption failed for queue with doorbell_id: 80004008
Jun 29 03:34:06 LSD kernel: amdgpu 0000:7c:00.0: sq_intr: error, se 0, data 0x100000, sa 0, priv 1, wave_id 0, simd_id 0, wgp_id 0, err_type 2
Jun 29 03:34:06 LSD kernel: amdgpu 0000:7c:00.0: GPU reset begin!. Source:  4
Jun 29 03:34:06 LSD kernel: amdgpu 0000:7c:00.0: sq_intr: error, se 0, data 0x100000, sa 0, priv 1, wave_id 0, simd_id 2, wgp_id 0, err_type 2
Jun 29 03:34:06 LSD kernel: amdgpu 0000:7c:00.0: sq_intr: error, se 0, data 0x100000, sa 0, priv 1, wave_id 0, simd_id 1, wgp_id 0, err_type 2
Jun 29 03:34:06 LSD kernel: amdgpu 0000:7c:00.0: sq_intr: error, se 0, data 0x100000, sa 0, priv 1, wave_id 0, simd_id 3, wgp_id 0, err_type 2
Jun 29 03:34:06 LSD kernel: amdgpu 0000:7c:00.0: sq_intr: error, se 0, data 0x100000, sa 0, priv 1, wave_id 1, simd_id 0, wgp_id 0, err_type 2
Jun 29 03:34:06 LSD kernel: amdgpu 0000:7c:00.0: sq_intr: error, se 0, data 0x100000, sa 0, priv 1, wave_id 1, simd_id 2, wgp_id 0, err_type 2
Jun 29 03:34:06 LSD kernel: amdgpu 0000:7c:00.0: sq_intr: error, se 0, data 0x100000, sa 0, priv 1, wave_id 1, simd_id 1, wgp_id 0, err_type 2
Jun 29 03:34:06 LSD kernel: amdgpu 0000:7c:00.0: sq_intr: error, se 0, data 0x100000, sa 0, priv 1, wave_id 1, simd_id 3, wgp_id 0, err_type 2
Jun 29 03:34:06 LSD kernel: amdgpu 0000:7c:00.0: Dumping IP State
Jun 29 03:34:06 LSD kernel: amdgpu 0000:7c:00.0: Dumping IP State Completed
... truncated 60 lines ...
```

## External Leads

- ROCm `/dev/kfd` `Invalid argument` issue:
  <https://github.com/ROCm/ROCm/issues/4043>
- Similar ROCm `/dev/kfd` issue:
  <https://github.com/ROCm/ROCm/issues/6166>
- AMD ROCm installation prerequisites:
  <https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/prerequisites.html>
- AMD ROCm quick start:
  <https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/quick-start.html>

## Next Gate

Do not use local ROCm for V21 training until both commands pass:

```bash
rocminfo
../envs/open-duck-playground/bin/python -c 'import jax; print(jax.devices())'
```

CUDA/Colab remains the preferred V21 path while this hold is active.
