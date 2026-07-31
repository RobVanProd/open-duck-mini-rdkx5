# Local ROCm Status

status: `PASS_LOCAL_ROCM_READY`
timestamp: `20260628T073531Z`

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
python /home/lsd/robots/envs/open-duck-playground/bin/python
jax 0.8.2
backend gpu
devices [RocmDevice(id=0)]
mujoco 3.9.0
```

### opt_rocm_path

returncode: `0`

```text
python /home/lsd/robots/envs/open-duck-playground/bin/python
LD_LIBRARY_PATH /opt/rocm-7.2.1/lib
jax 0.8.2
backend gpu
devices [RocmDevice(id=0)]
mujoco 3.9.0
```

### hsa_override

returncode: `-6`

```text
F0628 03:35:38.378119   16583 rocm_context.cc:137] Check failed: ToStatus(wrap::hipCtxSetCurrent(context_), "Failed setting context") is OK (INTERNAL: Failed setting context: hipError_t(719))
[symbolize_elf.inc : 379] RAW: Unable to get high fd: rc=0, limit=1024
*** Check failure stack trace: ***
    @     0x7091713357a4  absl::lts_20250814::log_internal::LogMessage::SendToLog()
    @     0x709171335726  absl::lts_20250814::log_internal::LogMessage::Flush()
    @     0x70916f8baa49  stream_executor::gpu::RocmContext::SetActive()
    @     0x70916f8c6e56  stream_executor::gpu::ScopedActivateContext::ScopedActivateContext()
    @     0x70916f52f99c  stream_executor::gpu::RocmExecutor::Activate()
    @     0x70916f8befff  stream_executor::gpu::RocmStream::BlockHostUntilDone()
    @     0x70916455c830  xla::LocalDeviceState::SynchronizeAllActivity()
    @     0x70916455c388  xla::LocalDeviceState::~LocalDeviceState()
    @     0x70916455cb7e  xla::LocalDeviceState::~LocalDeviceState()
    @     0x7091644ec79f  std::_Rb_tree<>::_M_erase()
    @     0x7091644e2d1d  std::map<>::~map()
    @     0x7091644e2bb4  xla::GetStreamExecutorGpuClient()
    @     0x7091644d4c24  xla::GetXlaPjrtGpuClient()
    @     0x709164467b0c  pjrt::gpu_plugin::PJRT_Client_Create()
    @     0x709381bd74a4  xla::WrapClientAroundCApi()
    @     0x709381bd717d  xla::GetCApiClient()
    @     0x709381af1788  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x70937e388131  nanobind::detail::nb_func_vectorcall_complex()
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
    @     0x70938a02a601  (unknown)
    @     0x70938a02a718  __libc_start_main
    @          0x19a9269  _start
```

### opt_rocm_path_hsa_override

returncode: `-6`

```text
F0628 03:35:42.854338   16721 rocm_context.cc:137] Check failed: ToStatus(wrap::hipCtxSetCurrent(context_), "Failed setting context") is OK (INTERNAL: Failed setting context: ROCM_ERROR_ILLEGAL_ADDRESS)
[symbolize_elf.inc : 379] RAW: Unable to get high fd: rc=0, limit=1024
*** Check failure stack trace: ***
    @     0x77ce711357a4  absl::lts_20250814::log_internal::LogMessage::SendToLog()
    @     0x77ce71135726  absl::lts_20250814::log_internal::LogMessage::Flush()
    @     0x77ce6f6baa49  stream_executor::gpu::RocmContext::SetActive()
    @     0x77ce6f6c6e56  stream_executor::gpu::ScopedActivateContext::ScopedActivateContext()
    @     0x77ce6f32f99c  stream_executor::gpu::RocmExecutor::Activate()
    @     0x77ce6f6befff  stream_executor::gpu::RocmStream::BlockHostUntilDone()
    @     0x77ce6435c830  xla::LocalDeviceState::SynchronizeAllActivity()
    @     0x77ce6435c388  xla::LocalDeviceState::~LocalDeviceState()
    @     0x77ce6435cb7e  xla::LocalDeviceState::~LocalDeviceState()
    @     0x77ce642ec79f  std::_Rb_tree<>::_M_erase()
    @     0x77ce642e2d1d  std::map<>::~map()
    @     0x77ce642e2bb4  xla::GetStreamExecutorGpuClient()
    @     0x77ce642d4c24  xla::GetXlaPjrtGpuClient()
    @     0x77ce64267b0c  pjrt::gpu_plugin::PJRT_Client_Create()
    @     0x77d0819d74a4  xla::WrapClientAroundCApi()
    @     0x77d0819d717d  xla::GetCApiClient()
    @     0x77d0818f1788  nanobind::detail::func_create<>()::{lambda()#1}::__invoke()
    @     0x77d07e188131  nanobind::detail::nb_func_vectorcall_complex()
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
    @     0x77d089e2a601  (unknown)
    @     0x77d089e2a718  __libc_start_main
    @          0x19a9269  _start
```

### cpu

returncode: `0`

```text
python /home/lsd/robots/envs/open-duck-playground/bin/python
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
crw-rw----+   1 root render 226, 128 Jun 28 03:29 /dev/dri/renderD128
crw-rw----+   1 root render 226, 129 Jun 28 03:29 /dev/dri/renderD129
crw-rw----+   1 root render 511,   0 Jun 28 03:29 /dev/kfd
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
Jun 28 03:29:08 LSD kernel: uvcvideo 1-1.3.3.3:1.0: Found UVC 1.00 device icspring camera (32e6:9005)
Jun 28 03:29:08 LSD kernel: amdgpu: vga_switcheroo: detected switching method \_SB_.PCI0.GP17.VGA_.ATPX handle
Jun 28 03:29:08 LSD kernel: amdgpu: ATPX version 1, functions 0x00000000
Jun 28 03:29:08 LSD kernel: amdgpu: Virtual CRAT table created for CPU
Jun 28 03:29:08 LSD kernel: amdgpu: Topology: Add CPU node
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: enabling device (0006 -> 0007)
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: initializing kernel modesetting (IP DISCOVERY 0x1002:0x744C 0x1EAE:0x7901 0xC8).
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: register mmio base: 0xDE400000
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: register mmio size: 1048576
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: detected ip block number 0 <common_v1_0_0> (soc21_common)
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: detected ip block number 1 <gmc_v11_0_0> (gmc_v11_0)
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: detected ip block number 2 <ih_v6_0_0> (ih_v6_0)
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: detected ip block number 3 <psp_v13_0_0> (psp)
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: detected ip block number 4 <smu_v13_0_0> (smu)
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: detected ip block number 5 <dce_v1_0_0> (dm)
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: detected ip block number 6 <gfx_v11_0_0> (gfx_v11_0)
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: detected ip block number 7 <sdma_v6_0_0> (sdma_v6_0)
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: detected ip block number 8 <vcn_v4_0_0> (vcn_v4_0)
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: detected ip block number 9 <jpeg_v4_0_0> (jpeg_v4_0)
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: detected ip block number 10 <mes_v11_0_0> (mes_v11_0)
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: Fetched VBIOS from VFCT
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: [drm] ATOM BIOS: 113-31XFSHBS1-L03
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: CP RS64 enable
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: Trusted Memory Zone (TMZ) feature not supported
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: MEM ECC is not presented.
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: SRAM ECC is not presented.
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: vm size is 262144 GB, 4 levels, block size is 9-bit, fragment size is 9-bit
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: VRAM: 24560M 0x0000008000000000 - 0x00000085FEFFFFFF (24560M used)
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: GART: 512M 0x00007FFF00000000 - 0x00007FFF1FFFFFFF
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: [drm] Detected VRAM RAM=24560M, BAR=32768M
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: [drm] RAM width 384bits GDDR6
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0:  24560M of VRAM memory ready
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0:  62073M of GTT memory ready.
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: [drm] GART: num cpu pages 131072, num gpu pages 131072
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: [drm] PCIE GART of 512M enabled (table at 0x00000085FEB00000).
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: [drm] Loading DMUB firmware via PSP: version=0x07002F00
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: [VCN instance 0] Found VCN firmware Version ENC: 1.24 DEC: 9 VEP: 0 Revision: 27
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: [VCN instance 1] Found VCN firmware Version ENC: 1.24 DEC: 9 VEP: 0 Revision: 27
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: MES: vmid_mask_mmhub 0x0000ff00, vmid_mask_gfxhub 0x0000ff00
Jun 28 03:29:08 LSD kernel: amdgpu 0000:04:00.0: MES: gfx_hqd_mask 0x00000002, compute_hqd_mask 0x0000000c, sdma_hqd_mask 0x000000fc
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: reserve 0x1300000 from 0x85fc000000 for PSP TMR
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: RAP: optional rap ta ucode is not available
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: SECUREDISPLAY: optional securedisplay ta ucode is not available
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: smu driver if version = 0x0000003d, smu fw if version = 0x00000040, smu fw program = 0, smu fw version = 0x004e8300 (78.131.0)
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: SMU driver if version not matched
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: SMU is initialized successfully!
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: [drm] Display Core v3.2.369 initialized on DCN 3.2
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: [drm] DP-HDMI FRL PCON supported
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: [drm] DMUB hardware initialized: version=0x07002F00
Jun 28 03:29:09 LSD kernel: snd_hda_intel 0000:04:00.1: bound 0000:04:00.0 (ops amdgpu_dm_audio_component_bind_ops [amdgpu])
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: [drm] DP-1: PSR support 0, DC PSR ver -1, sink PSR ver 0 DPCD caps 0x0 su_y_granularity 0
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: [drm] DP-2: PSR support 0, DC PSR ver -1, sink PSR ver 0 DPCD caps 0x0 su_y_granularity 0
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: [drm] DP-3: PSR support 0, DC PSR ver -1, sink PSR ver 0 DPCD caps 0x0 su_y_granularity 0
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: [drm] HDMI-A-1: PSR support 0, DC PSR ver -1, sink PSR ver 0 DPCD caps 0x0 su_y_granularity 0
Jun 28 03:29:09 LSD kernel: kfd kfd: Allocated 3969056 bytes on gart
Jun 28 03:29:09 LSD kernel: kfd kfd: Total number of KFD nodes to be created: 1
Jun 28 03:29:09 LSD kernel: amdgpu: Virtual CRAT table created for GPU
Jun 28 03:29:09 LSD kernel: amdgpu: Topology: Add GPU node [0x1002:0x744c]
Jun 28 03:29:09 LSD kernel: kfd kfd: added device 1002:744c
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: SE 6, SH per SE 2, CU per SH 8, active_cu_number 96
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: ring gfx_0.0.0 uses VM inv eng 0 on hub 0
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.0.0 uses VM inv eng 1 on hub 0
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.1.0 uses VM inv eng 4 on hub 0
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.2.0 uses VM inv eng 6 on hub 0
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.3.0 uses VM inv eng 7 on hub 0
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.0.1 uses VM inv eng 8 on hub 0
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.1.1 uses VM inv eng 9 on hub 0
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.2.1 uses VM inv eng 10 on hub 0
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: ring comp_1.3.1 uses VM inv eng 11 on hub 0
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: ring sdma0 uses VM inv eng 12 on hub 0
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: ring sdma1 uses VM inv eng 13 on hub 0
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: ring vcn_unified_0 uses VM inv eng 0 on hub 8
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: ring vcn_unified_1 uses VM inv eng 1 on hub 8
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: ring jpeg_dec uses VM inv eng 4 on hub 8
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: ring mes_kiq_3.1.0 uses VM inv eng 14 on hub 0
Jun 28 03:29:09 LSD kernel: amdgpu: HMM registered 24560MB device memory
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: Using BACO for runtime pm
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: [drm] Registered 4 planes with drm panic
Jun 28 03:29:09 LSD kernel: [drm] Initialized amdgpu 3.64.0 for 0000:04:00.0 on minor 1
Jun 28 03:29:09 LSD kernel: amdgpu 0000:04:00.0: [drm] Cannot find any crtc or sizes
Jun 28 03:29:09 LSD kernel: [drm] pre_validate_dsc:1667 MST_DSC dsc precompute is not needed
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: enabling device (0006 -> 0007)
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: initializing kernel modesetting (IP DISCOVERY 0x1002:0x13C0 0x1043:0x8877 0xC1).
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: register mmio base: 0xDE300000
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: register mmio size: 524288
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: detected ip block number 0 <common_v1_0_0> (nv_common)
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: detected ip block number 1 <gmc_v10_0_0> (gmc_v10_0)
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: detected ip block number 2 <ih_v5_0_0> (navi10_ih)
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: detected ip block number 3 <psp_v13_0_0> (psp)
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: detected ip block number 4 <smu_v13_0_0> (smu)
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: detected ip block number 5 <dce_v1_0_0> (dm)
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: detected ip block number 6 <gfx_v10_0_0> (gfx_v10_0)
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: detected ip block number 7 <sdma_v5_2_0> (sdma_v5_2)
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: detected ip block number 8 <vcn_v3_0_0> (vcn_v3_0)
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: detected ip block number 9 <jpeg_v3_0_0> (jpeg_v3_0)
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: Fetched VBIOS from VFCT
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: [drm] ATOM BIOS: 102-RAPHAEL-008
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: vgaarb: deactivate vga console
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: Trusted Memory Zone (TMZ) feature disabled as experimental (default)
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: vm size is 262144 GB, 4 levels, block size is 9-bit, fragment size is 9-bit
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: VRAM: 2048M 0x000000F400000000 - 0x000000F47FFFFFFF (2048M used)
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: GART: 1024M 0x0000000000000000 - 0x000000003FFFFFFF
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: [drm] Detected VRAM RAM=2048M, BAR=2048M
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: [drm] RAM width 64bits DDR5
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0:  2048M of VRAM memory ready
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0:  62073M of GTT memory ready.
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: [drm] GART: num cpu pages 262144, num gpu pages 262144
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: [drm] PCIE GART of 1024M enabled (table at 0x000000F47FC00000).
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: [drm] Loading DMUB firmware via PSP: version=0x05002D00
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: [drm] use_doorbell being set to: [true]
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: [VCN instance 0] Found VCN firmware Version ENC: 1.33 DEC: 4 VEP: 0 Revision: 14
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: reserve 0xa00000 from 0xf47e000000 for PSP TMR
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: RAS: optional ras ta ucode is not available
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: RAP: optional rap ta ucode is not available
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: SECUREDISPLAY: optional securedisplay ta ucode is not available
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: SMU is initialized successfully!
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: [drm] Display Core v3.2.369 initialized on DCN 3.1.5
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: [drm] DP-HDMI FRL PCON supported
Jun 28 03:29:09 LSD kernel: amdgpu 0000:7c:00.0: [drm] DMUB hardware initialized: version=0x05002D00
Jun 28 03:29:09 LSD kernel: snd_hda_intel 0000:7c:00.1: bound 0000:7c:00.0 (ops amdgpu_dm_audio_component_bind_ops [amdgpu])
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
