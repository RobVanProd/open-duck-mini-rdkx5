# Phase 2 Local ROCm Post-B0G Backend Hold

status: `HOLD_LOCAL_ROCM_POST_B0G_NODEVICE`

## Scope

This is a local offline backend diagnostic after the B0G smoke. No robot tests,
SSH, deploy, grounded replay, runtime behavior changes, or policy overwrite
were performed.

## What Passed First

The RX 7900 XTX did complete the bounded B0G smoke:

```text
run_dir:
  outputs/phase2_domain_randomization/stage_b0g_push_recovery_local_rocm_smoke/smoke_20260629T130541Z_gpu

status: PASS_SMOKE_RUN
returncode: 0
step: 20480
onnx_sha256: 70fde5e93cfe7252ef14d8c953e9015051cde1747806f24adf2274f022491473
```

So the push-recovery hook is not blocked at import/compile time, and local
ROCm can run a small 32-env B0G-shaped workload when the device is healthy.

## Failure Afterward

Immediately after the B0G smoke and CPU gate, the same local env could no
longer initialize the ROCm JAX backend:

```text
JAX_PLATFORMS=cpu:
  cpu_jax 0.8.2 cpu [CpuDevice(id=0)]

JAX_PLATFORMS=rocm:
  failed call to hipInit: HIP_ERROR_NoDevice
  RuntimeError: Unable to initialize backend 'rocm': FAILED_PRECONDITION: No visible GPU devices.
```

Device nodes and group membership still looked correct:

```text
/dev/dri/renderD128: root:render
/dev/dri/renderD129: root:render
/dev/kfd: root:render
user groups include: render
```

`rocm-smi --showproductname --showuse --showmeminfo vram --json` then hung
after printing:

```text
_amdgpu_device_initialize: amdgpu_query_gpu_info_init failed
```

The stuck diagnostic process was killed. No training/eval process was left
running.

## Decision

Do not launch additional local ROCm policy-producing jobs in this wedged
state. Treat the local 7900 XTX path as useful for bounded smoke only after a
fresh backend reset and a passing JAX/ROCm device check.

The next policy-producing B0G attempt should use the pinned A100/Colab path
when a visible session is available:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow phase2-b0g \
  --session <visible-a100-session> \
  --candidate-checkpoint-sweep \
  --candidate-checkpoint-sweep-commands 0.0,0.08 \
  --candidate-checkpoint-sweep-duration 1.0 \
  --candidate-checkpoint-sweep-jax-platform cpu \
  --run
```

Until then, CPU remains acceptable for correctness gates and trace analysis,
but not for broad policy-producing Phase 2 training.
