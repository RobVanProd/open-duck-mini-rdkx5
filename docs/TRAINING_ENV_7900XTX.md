# 7900 XTX Training Environment

Last updated: 2026-06-21

## Purpose

Document the local AMD `7900 XTX` / ROCm setup for future Open Duck Playground
sim eval and training.

This is a gate, not permission to train. Do not start training until the
closed-loop sim actuator bridge eval passes review.

## Local Environments

| environment | path | current role |
|---|---|---|
| Open Duck Playground env | `../envs/open-duck-playground` | recommended sim eval / future training env |
| ROCm baseline env | `../envs/rocm-baseline` | useful GPU smoke baseline, missing some Playground deps |
| MuJoCo render smoke script | `../verify_scratch/render_mujoco_egl.py` | local AMD/MuJoCo render check |

Current observed state:

```text
../envs/open-duck-playground/bin/python
  Python 3.12.13
  JAX 0.8.2
  MuJoCo 3.9.0
  ONNX Runtime 1.26.0
  ml_collections 1.1.0
  mujoco_playground importable
  JAX backend: gpu
  JAX device: RocmDevice(id=0)

../envs/rocm-baseline/bin/python
  JAX backend: gpu
  JAX device: RocmDevice(id=0)
  missing ml_collections / mujoco_playground / onnxruntime
```

So future Open Duck sim eval/training should use:

```bash
../envs/open-duck-playground/bin/python
```

not system Python.

## Current ROCm / MJX Hold

The basic environment check sees the `7900 XTX`:

```text
JAX backend: gpu
JAX device: rocm:0
```

However, the closed-loop actuator bridge eval currently fails inside the
JAX/MJX GPU step:

```text
HOLD_SIM_RUNTIME_ERROR
ROCM_ERROR_ILLEGAL_ADDRESS
```

This means the environment is import-ready, but not yet cleared for closed-loop
MJX eval or training. Treat `tools/check_training_env.py` as a necessary
preflight, not as sufficient proof that long JAX/MJX jobs are safe.

ROCm/MJX isolation narrowed the failure:

```text
basic JAX GPU: PASS
JAX jit/scan GPU: PASS
minimal MJX GPU: PASS
Open Duck Playground reset GPU: PASS
Open Duck Playground one-step GPU: TIMEOUT
closed-loop GPU: ROCM_ERROR_ILLEGAL_ADDRESS
closed-loop CPU short matrix: PASS
```

So the next GPU debug target is the Open Duck Playground MJX step, not basic
ROCm visibility and not the fitted actuator bridge.

Focused memory-allocation variants were tested on the smallest failing GPU
subtest (`playground_one_step_vanilla`):

```text
XLA_PYTHON_CLIENT_MEM_FRACTION=0.50 -> TIMEOUT
XLA_PYTHON_CLIENT_MEM_FRACTION=0.60 -> TIMEOUT
XLA_PYTHON_CLIENT_ALLOCATOR=platform -> TIMEOUT
```

This does not rule out a hipSolver/XLA memory interaction for later crashes,
but it shows that JAX preallocation changes alone do not currently clear the
first Open Duck Playground GPU step. The current `amdgpu` module parameter is:

```text
cwsr_enable = 1
```

Do not change kernel/module settings such as CWSR from project scripts.

## Readiness Check

Run:

```bash
../envs/open-duck-playground/bin/python tools/check_training_env.py
```

Expected shape:

```text
JAX imports
JAX backend is gpu
JAX devices include rocm:0
MuJoCo imports
minimal MuJoCo model loads and steps
Open Duck Playground modules import
```

Optional render/context check:

```bash
../envs/open-duck-playground/bin/python tools/check_training_env.py --render-check
```

If render/context fails, inspect:

```text
MUJOCO_GL
ROCm driver/runtime install
../verify_scratch/render_mujoco_egl.py
```

## System Python Is Not The Training Env

System Python currently reports:

```text
HOLD_ENV_NOT_READY
missing jax
missing mujoco
missing ml_collections
missing mujoco_playground
```

That is useful as a guardrail: do not start training from system Python.

## Training Gate

Before any training job:

1. Run `tools/check_training_env.py` from `../envs/open-duck-playground/bin/python`.
2. Run policy/sim contract audit and confirm `PASS_POLICY_SIM_CONTRACT`.
3. Run closed-loop actuator bridge eval and confirm it no longer reports
   `HOLD_SIM_RUNTIME_ERROR`.
4. Confirm current policy degrades in lagged sim like the real suspended
   `x=0.08` replay.
5. Only then implement or run a short ROCm smoke training job.

No policy should be exported for robot testing until suspended validation gates
are defined and passed.
