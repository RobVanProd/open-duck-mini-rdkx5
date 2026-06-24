# Local ROCm After BIOS Summary

Date: 2026-06-23

Purpose: record the local 7900 XTX status after the BIOS/firmware update and
decide whether to use the local ROCm path for Open Duck closed-loop eval or
training.

## Executive Summary

The BIOS update did not make the local 7900 XTX path reliable for Open Duck
Playground closed-loop MJX stepping.

What works locally:

- ROCm sees the RX 7900 XTX as `gfx1100`.
- With `ROCR_VISIBLE_DEVICES=0`, JAX sees only `RocmDevice(id=0)`.
- Basic JAX GPU arithmetic passes.
- JAX `jit` / `lax.scan` smoke tests pass.
- A minimal MJX model step passes on GPU.
- Open Duck Playground reset and finite-state checks pass on GPU.
- The same Open Duck Playground step tests pass on CPU.

What still fails locally:

- Open Duck Playground direct MJX step on GPU does not return a pass payload.
- Open Duck Playground `env.step` variants on GPU do not complete inside the
  isolation timeout.
- Jitted Open Duck Playground direct MJX step produced
  `ROCM_ERROR_ILLEGAL_ADDRESS`.
- Closed-loop policy eval on GPU produced
  `ROCM_ERROR_ILLEGAL_ADDRESS`.

Current practical decision:

Use Colab/A100 for closed-loop candidate gates and training. Keep local CPU as a
correctness fallback. Do not spend more candidate-search time on the local ROCm
path until the ROCm/JAX/MuJoCo stack is updated or isolated in a container.

## Local Stack Observed

- GPU: Radeon RX 7900 XTX
- ROCm device: `gfx1100`
- Integrated GPU also present: `gfx1036`
- ROCm driver reported by `rocm-smi`: `7.0.0-22-generic`
- Python env: `/home/lsd/robots/envs/open-duck-playground/bin/python`
- JAX: `0.8.2`
- jaxlib: `0.8.2`
- MuJoCo: `3.9.0`
- JAX backend under GPU mask: `gpu`
- JAX device under GPU mask: `rocm:0`

The XTX-only mask used for tests was:

```bash
ROCR_VISIBLE_DEVICES=0
HSA_OVERRIDE_GFX_VERSION=11.0.0
XLA_PYTHON_CLIENT_PREALLOCATE=false
```

## Evidence Path

Isolation output directory:

```text
outputs/analysis/rocm_mjx_isolation_after_bios/
```

Key completed rows:

| Subtest | GPU result | CPU result | Interpretation |
|---|---|---|---|
| basic JAX | PASS | PASS | JAX itself is not the blocker |
| JAX jit/scan | PASS | PASS | simple compiled loops are not the blocker |
| minimal MJX step | PASS | PASS | MJX package can run a tiny model |
| Open Duck contract | PASS | PASS | 101/14 env contract is visible |
| Open Duck reset | PASS | PASS | env creation/reset is not the blocker |
| Open Duck finite-state check | PASS | PASS | reset state is finite |
| Open Duck direct MJX step | no pass payload / timeout | PASS | GPU-specific Open Duck MJX step failure |
| Open Duck direct MJX step, jitted | `ROCM_ERROR_ILLEGAL_ADDRESS` | PASS | GPU-specific compiled step failure |
| Open Duck one-step / scan variants | timeout/no pass payload | PASS for completed CPU rows | local GPU path unreliable |
| closed-loop policy eval | `ROCM_ERROR_ILLEGAL_ADDRESS` | not needed for decision yet | local GPU closed-loop blocked |

## Online Research Notes

AMD's ROCm blog has a March 2026 MuJoCo/JAX tutorial that says their 7900 XTX
setup was verified with ROCm 7.2 and used these environment variables:

```bash
export LLVM_PATH=/opt/rocm/llvm
export HIP_DEVICE_LIB_PATH=/opt/rocm-7.2.0/lib/llvm/lib/clang/22/lib/amdgcn/bitcode
export MUJOCO_GL=osmesa
export XLA_FLAGS="--xla_gpu_enable_command_buffer="
```

Source:
https://rocm.blogs.amd.com/artificial-intelligence/rocm-jax-mujoco/README.html

AMD's JAX-on-ROCm installation docs list a validated ROCm 7.2.4 image with
JAX 0.8.2 / Python 3.12, matching our JAX version but newer than the local ROCm
driver:

```text
rocm/jax:rocm7.2.4-jax0.8.2-py3.12
```

Source:
https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/3rd-party/jax-install.html

MuJoCo's MJX docs say MJX-JAX supports AMD GPUs, but they also point out that
MJX-Warp resolves important contact/constraint bottlenecks for NVIDIA. For this
project, that supports the current split: use A100/CUDA for candidate gates and
training while local ROCm remains a backend issue.

Source:
https://mujoco.readthedocs.io/en/stable/mjx.html

## Recommendation

Do not use the local 7900 XTX path for Open Duck closed-loop eval or training
right now.

Use this priority order:

1. Colab/A100 for training and closed-loop candidate gates.
2. Local CPU for small correctness checks when A100 is unavailable.
3. Local ROCm only for smoke tests until upgraded to a ROCm 7.2+ container or
   bare-metal stack matching AMD's MuJoCo/JAX guidance.

If we revisit local ROCm, test in this order:

1. ROCm 7.2.4 JAX container or equivalent.
2. Set `LLVM_PATH`, `HIP_DEVICE_LIB_PATH`, `MUJOCO_GL=osmesa`, and
   `XLA_FLAGS="--xla_gpu_enable_command_buffer="`.
3. Keep `ROCR_VISIBLE_DEVICES=0` to exclude the integrated GPU.
4. Re-run `tools/isolate_rocm_mjx_failure.py`.
5. Only if Open Duck Playground one-step and scan-step pass, retry closed-loop
   candidate eval locally.

## Project Impact

This does not change the robot diagnosis or candidate status:

- V7 proved in-envelope forward motion but fell from a forward lunge.
- V8 and V9 removed the lunge but collapsed to standstill.
- The next policy work is checkpoint selection and teacher/trust-region
  continuity, not more local ROCm debugging.

Robot remains parked. No SSH, deployment, robot tests, or runtime behavior
changes were performed.
