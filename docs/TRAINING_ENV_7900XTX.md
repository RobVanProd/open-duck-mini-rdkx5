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
3. Run closed-loop actuator bridge eval and confirm current policy degrades in
   lagged sim like the real suspended `x=0.08` replay.
4. Only then implement or run a short ROCm smoke training job.

No policy should be exported for robot testing until suspended validation gates
are defined and passed.
