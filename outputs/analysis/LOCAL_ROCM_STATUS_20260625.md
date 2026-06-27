# Local ROCm Status

status: `HOLD_LOCAL_ROCM_KFD`
timestamp: `20260625T084902Z`

This read-only check did not train, SSH, deploy, change runtime
behavior, or touch the robot.

## Summary

| check | result |
|---|---|
| rocminfo default | `HOLD` |
| rocminfo /dev/kfd failure | `True` |
| JAX default GPU visible | `False` |
| JAX CPU fallback | `PASS` |

## rocminfo Variants

### default

returncode: `1`

```text
ROCk module is loaded
Unable to open /dev/kfd read-write: Invalid argument
lsd is member of render group
```

### opt_rocm_path

returncode: `1`

```text
ROCk module is loaded
Unable to open /dev/kfd read-write: Invalid argument
lsd is member of render group
```

### hsa_override

returncode: `1`

```text
ROCk module is loaded
Unable to open /dev/kfd read-write: Invalid argument
lsd is member of render group
```

### opt_rocm_path_hsa_override

returncode: `1`

```text
ROCk module is loaded
Unable to open /dev/kfd read-write: Invalid argument
lsd is member of render group
```

## JAX Variants

### default

returncode: `0`

```text
python /home/lsd/robots/envs/open-duck-playground/bin/python
jax 0.8.2
jax_error RuntimeError Unable to initialize backend 'rocm': FAILED_PRECONDITION: No visible GPU devices. (you may need to uninstall the failing plugin package, or set JAX_PLATFORMS=cpu to skip this backend.)
mujoco 3.9.0
E0625 04:49:02.672996  246831 rocm_platform.cc:50] failed call to hipInit: HIP_ERROR_NoDevice
```

### opt_rocm_path

returncode: `0`

```text
python /home/lsd/robots/envs/open-duck-playground/bin/python
LD_LIBRARY_PATH /opt/rocm-7.2.1/lib
jax 0.8.2
jax_error RuntimeError Unable to initialize backend 'rocm': FAILED_PRECONDITION: No visible GPU devices. (you may need to uninstall the failing plugin package, or set JAX_PLATFORMS=cpu to skip this backend.)
mujoco 3.9.0
E0625 04:49:03.017712  246929 rocm_platform.cc:50] failed call to hipInit: HIP_ERROR_NoDevice
```

### hsa_override

returncode: `0`

```text
python /home/lsd/robots/envs/open-duck-playground/bin/python
HSA_OVERRIDE_GFX_VERSION 11.0.0
jax 0.8.2
jax_error RuntimeError Unable to initialize backend 'rocm': FAILED_PRECONDITION: No visible GPU devices. (you may need to uninstall the failing plugin package, or set JAX_PLATFORMS=cpu to skip this backend.)
mujoco 3.9.0
E0625 04:49:03.391909  247027 rocm_platform.cc:50] failed call to hipInit: HIP_ERROR_NoDevice
```

### opt_rocm_path_hsa_override

returncode: `0`

```text
python /home/lsd/robots/envs/open-duck-playground/bin/python
HSA_OVERRIDE_GFX_VERSION 11.0.0
LD_LIBRARY_PATH /opt/rocm-7.2.1/lib
jax 0.8.2
jax_error RuntimeError Unable to initialize backend 'rocm': FAILED_PRECONDITION: No visible GPU devices. (you may need to uninstall the failing plugin package, or set JAX_PLATFORMS=cpu to skip this backend.)
mujoco 3.9.0
E0625 04:49:03.744737  247125 rocm_platform.cc:50] failed call to hipInit: HIP_ERROR_NoDevice
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
crw-rw----+   1 root render 226, 128 Jun 24 21:25 /dev/dri/renderD128
crw-rw----+   1 root render 226, 129 Jun 24 21:25 /dev/dri/renderD129
crw-rw----+   1 root render 511,   0 Jun 24 21:25 /dev/kfd
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
hip-base
hip-dev 7.2.53211.70201-81~24.04
hip-doc 7.2.53211.70201-81~24.04
hip-rocclr
hip-runtime-amd 7.2.53211.70201-81~24.04
hip-samples 7.2.53211.70201-81~24.04
hip-thrust
hipblas 3.2.0.70201-81~24.04
hipblas-common
hipblas-common-dev 1.4.0.70201-81~24.04
hipblas-dev 3.2.0.70201-81~24.04
hipblaslt 1.2.2.70201-81~24.04
hipblaslt-dev 1.2.2.70201-81~24.04
hipcc 1.1.1.70201-81~24.04
hipcub
hipcub-dev 4.2.0.70201-81~24.04
hipfft 1.0.22.70201-81~24.04
hipfft-dev 1.0.22.70201-81~24.04
hipfort
hipfort-dev 0.7.1.70201-81~24.04
hipify-clang 22.0.0.70201-81~24.04
hiprand 3.1.0.70201-81~24.04
hiprand-dev 3.1.0.70201-81~24.04
hipsolver 3.2.0.70201-81~24.04
hipsolver-dev 3.2.0.70201-81~24.04
hipsparse 4.2.0.70201-81~24.04
hipsparse-dev 4.2.0.70201-81~24.04
hipsparselt 0.2.6.70201-81~24.04
hipsparselt-dev 0.2.6.70201-81~24.04
hipstdpar
hiptensor 2.2.0.70201-81~24.04
hiptensor-dev 2.2.0.70201-81~24.04
hsa-amd-aqlprofile 1.0.0.70201-81~24.04
hsa-ext-rocr-dev
hsa-rocr 1.18.0.70201-81~24.04
hsa-rocr-dev 1.18.0.70201-81~24.04
hsakmt-roct
hsakmt-roct-dev
libamdhip64-5
libamdhip64-7 7.1.0-0ubuntu2
libhsa-runtime64-1 7.1.0+dfsg-0ubuntu9
libhsakmt1 7.1.0+dfsg-0ubuntu9
rocm 7.2.1.70201-81~24.04
rocm-cmake 0.14.0.70201-81~24.04
rocm-core 7.2.1.70201-81~24.04
rocm-dbgapi 0.77.4.70201-81~24.04
rocm-debug-agent 2.1.0.70201-81~24.04
rocm-developer-tools 7.2.1.70201-81~24.04
rocm-device-libs 1.0.0.70201-81~24.04
rocm-gdb 16.3.70201-81~24.04
rocm-hip 7.2.1.70201-81~24.04
rocm-llvm 22.0.0.26084.70201-81~24.04
rocm-opencl 2.0.0.70201-81~24.04
rocm-opencl-dev 2.0.0.70201-81~24.04
rocm-opencl-icd
rocm-opencl-icd-loader
rocm-opencl-sdk 7.2.1.70201-81~24.04
rocm-openmp 7.2.1.70201-81~24.04
rocm-smi-lib 7.8.0.70201-81~24.04
rocminfo 1.0.0.70201-81~24.04
```

### ROCm Library Paths

```text
libhsakmt.so.1 (libc6,x86-64) => /usr/lib/x86_64-linux-gnu/libhsakmt.so.1
	libhsa-runtime64.so.1 (libc6,x86-64) => /opt/rocm-7.2.1/lib/libhsa-runtime64.so.1
	libhsa-runtime64.so.1 (libc6,x86-64) => /usr/lib/x86_64-linux-gnu/libhsa-runtime64.so.1
	libhsa-runtime64.so (libc6,x86-64) => /opt/rocm-7.2.1/lib/libhsa-runtime64.so
	libhsa-amd-aqlprofile64.so.1 (libc6,x86-64) => /opt/rocm-7.2.1/lib/libhsa-amd-aqlprofile64.so.1
	libhsa-amd-aqlprofile64.so (libc6,x86-64) => /opt/rocm-7.2.1/lib/libhsa-amd-aqlprofile64.so
	libhiprtc.so.7 (libc6,x86-64) => /opt/rocm-7.2.1/lib/libhiprtc.so.7
	libhiprtc.so (libc6,x86-64) => /opt/rocm-7.2.1/lib/libhiprtc.so
	libhiprtc-builtins.so.7 (libc6,x86-64) => /opt/rocm-7.2.1/lib/libhiprtc-builtins.so.7
	libhiprtc-builtins.so (libc6,x86-64) => /opt/rocm-7.2.1/lib/libhiprtc-builtins.so
	libamdhip64.so.7 (libc6,x86-64) => /opt/rocm-7.2.1/lib/libamdhip64.so.7
	libamdhip64.so.7 (libc6,x86-64) => /usr/lib/x86_64-linux-gnu/libamdhip64.so.7
	libamdhip64.so (libc6,x86-64) => /opt/rocm-7.2.1/lib/libamdhip64.so
```

### Recent Kernel GPU Lines

```text
Jun 25 03:17:31 LSD kernel: amdgpu 0000:7c:00.0: Dumping IP State
Jun 25 03:17:36 LSD kernel: amdgpu 0000:7c:00.0: SMU: No response msg_reg: 17 resp_reg: 0
Jun 25 03:17:36 LSD kernel: amdgpu 0000:7c:00.0: Failed to disable gfxoff!
Jun 25 03:17:41 LSD kernel: amdgpu 0000:7c:00.0: SMU: No response msg_reg: 17 resp_reg: 0
Jun 25 03:17:41 LSD kernel: amdgpu 0000:7c:00.0: Failed to disable gfxoff!
Jun 25 03:17:46 LSD kernel: amdgpu 0000:7c:00.0: SMU: No response msg_reg: 17 resp_reg: 0
Jun 25 03:17:46 LSD kernel: amdgpu 0000:7c:00.0: Failed to disable gfxoff!
Jun 25 03:17:51 LSD kernel: amdgpu 0000:7c:00.0: SMU: No response msg_reg: 17 resp_reg: 0
Jun 25 03:17:51 LSD kernel: amdgpu 0000:7c:00.0: Failed to disable gfxoff!
Jun 25 03:17:51 LSD kernel: amdgpu 0000:7c:00.0: Dumping IP State Completed
Jun 25 03:17:51 LSD kernel: amdgpu 0000:7c:00.0: [drm] AMDGPU device coredump file has been created
Jun 25 03:17:51 LSD kernel: amdgpu 0000:7c:00.0: [drm] Check your /sys/class/drm/card2/device/devcoredump/data
Jun 25 03:17:51 LSD kernel: amdgpu 0000:7c:00.0: ring gfx_0.0.0 timeout, signaled seq=900246, emitted seq=900247
Jun 25 03:17:51 LSD kernel: amdgpu 0000:7c:00.0:  Process ptyxis pid 6099 thread ptyxis pid 6099
Jun 25 03:17:51 LSD kernel: amdgpu 0000:7c:00.0: Starting gfx_0.0.0 ring reset
Jun 25 03:17:52 LSD kernel: amdgpu 0000:7c:00.0: Ring gfx_0.0.0 reset failed
Jun 25 03:17:52 LSD kernel: amdgpu 0000:7c:00.0: GPU reset begin!. Source:  1
Jun 25 03:17:57 LSD kernel: amdgpu 0000:7c:00.0: SMU: No response msg_reg: 17 resp_reg: 0
Jun 25 03:17:57 LSD kernel: amdgpu 0000:7c:00.0: Failed to disable gfxoff!
Jun 25 03:18:02 LSD kernel: amdgpu 0000:7c:00.0: SMU: No response msg_reg: 17 resp_reg: 0
Jun 25 03:18:02 LSD kernel: amdgpu 0000:7c:00.0: Failed to disable smu features.
Jun 25 03:18:02 LSD kernel: amdgpu 0000:7c:00.0: MODE2 reset
Jun 25 03:18:07 LSD kernel: amdgpu 0000:7c:00.0: SMU: No response msg_reg: 17 resp_reg: 0
Jun 25 03:18:07 LSD kernel: amdgpu 0000:7c:00.0: Failed to mode reset!
Jun 25 03:18:07 LSD kernel: amdgpu 0000:7c:00.0: Mode2 reset failed!
Jun 25 03:18:07 LSD kernel: amdgpu 0000:7c:00.0: GPU mode2 reset failed
Jun 25 03:18:07 LSD kernel: amdgpu 0000:7c:00.0: ASIC reset failed with error, -62 for drm dev, 0000:7c:00.0
Jun 25 03:18:07 LSD kernel: amdgpu 0000:7c:00.0: GPU reset end with ret = -62
Jun 25 03:18:07 LSD kernel: amdgpu 0000:7c:00.0: GPU Recovery Failed: -62
Jun 25 03:18:09 LSD kernel: amdgpu 0000:7c:00.0: Dumping IP State
Jun 25 03:18:09 LSD kernel: amdgpu 0000:7c:00.0: Dumping IP State Completed
Jun 25 03:18:09 LSD kernel: amdgpu 0000:7c:00.0: [drm] AMDGPU device coredump file has been created
Jun 25 03:18:09 LSD kernel: amdgpu 0000:7c:00.0: [drm] Check your /sys/class/drm/card2/device/devcoredump/data
Jun 25 03:18:09 LSD kernel: amdgpu 0000:7c:00.0: ring gfx_0.0.0 timeout, signaled seq=900247, emitted seq=900247
Jun 25 03:18:09 LSD kernel: amdgpu 0000:7c:00.0:  Process ptyxis pid 6099 thread ptyxis pid 6099
Jun 25 03:18:09 LSD kernel: amdgpu 0000:7c:00.0: Starting gfx_0.0.0 ring reset
Jun 25 03:18:09 LSD kernel: amdgpu 0000:7c:00.0: Ring gfx_0.0.0 reset failed
Jun 25 03:18:09 LSD kernel: amdgpu 0000:7c:00.0: GPU reset begin!. Source:  1
Jun 25 03:21:49 LSD kernel:  dma_fence_default_wait+0x1a0/0x280
Jun 25 03:21:49 LSD kernel:  ? __pfx_dma_fence_default_wait_cb+0x10/0x10
Jun 25 03:21:49 LSD kernel:  amdgpu_vm_fini+0xed/0x600 [amdgpu]
Jun 25 03:21:49 LSD kernel:  ? amdgpu_vm_bo_del+0x2f8/0x390 [amdgpu]
Jun 25 03:21:49 LSD kernel:  amdgpu_driver_postclose_kms+0x1ab/0x290 [amdgpu]
Jun 25 03:21:49 LSD kernel:  drm_file_free+0x240/0x2d0
Jun 25 03:21:49 LSD kernel:  drm_release+0xcb/0x160
Jun 25 03:21:49 LSD kernel:  amdgpu_drm_release+0x5b/0xb0 [amdgpu]
Jun 25 03:21:49 LSD kernel:  dma_fence_default_wait+0x1a0/0x280
Jun 25 03:21:49 LSD kernel:  ? __pfx_dma_fence_default_wait_cb+0x10/0x10
Jun 25 03:21:49 LSD kernel:  dma_fence_default_wait+0x1a0/0x280
Jun 25 03:21:49 LSD kernel:  ? __pfx_dma_fence_default_wait_cb+0x10/0x10
Jun 25 03:21:49 LSD kernel: Workqueue: amdgpu-reset-dev drm_sched_job_timedout [gpu_sched]
Jun 25 03:21:49 LSD kernel:  dma_fence_default_wait+0x1a0/0x280
Jun 25 03:21:49 LSD kernel:  ? __pfx_dma_fence_default_wait_cb+0x10/0x10
Jun 25 03:21:49 LSD kernel:  drm_sched_stop+0x157/0x210 [gpu_sched]
Jun 25 03:21:49 LSD kernel:  amdgpu_device_halt_activities.isra.0+0x1f3/0x24b [amdgpu]
Jun 25 03:21:49 LSD kernel:  amdgpu_device_gpu_recover.cold+0x185/0x2ff [amdgpu]
Jun 25 03:21:49 LSD kernel:  amdgpu_job_timedout.cold+0x20f/0x24d [amdgpu]
Jun 25 03:21:49 LSD kernel:  drm_sched_job_timedout+0x8c/0x1a0 [gpu_sched]
Jun 25 03:21:49 LSD kernel:  dma_fence_default_wait+0x1a0/0x280
Jun 25 03:21:49 LSD kernel:  ? __pfx_dma_fence_default_wait_cb+0x10/0x10
Jun 25 03:21:49 LSD kernel:  dma_fence_default_wait+0x1a0/0x280
Jun 25 03:21:49 LSD kernel:  ? __pfx_dma_fence_default_wait_cb+0x10/0x10
Jun 25 03:21:49 LSD kernel:  dma_fence_default_wait+0x1a0/0x280
Jun 25 03:21:49 LSD kernel:  ? __pfx_dma_fence_default_wait_cb+0x10/0x10
Jun 25 03:21:49 LSD kernel:  dma_fence_default_wait+0x1a0/0x280
Jun 25 03:21:49 LSD kernel:  ? __pfx_dma_fence_default_wait_cb+0x10/0x10
Jun 25 03:21:49 LSD kernel:  dma_fence_default_wait+0x1a0/0x280
Jun 25 03:21:49 LSD kernel:  ? __pfx_dma_fence_default_wait_cb+0x10/0x10
Jun 25 03:21:49 LSD kernel:  dma_fence_default_wait+0x1a0/0x280
Jun 25 03:21:49 LSD kernel:  ? __pfx_dma_fence_default_wait_cb+0x10/0x10
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
