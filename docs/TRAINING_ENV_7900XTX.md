# 7900 XTX Training Environment

Last updated: 2026-06-22

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
Open Duck direct mjx_env.step GPU: TIMEOUT
Open Duck direct mjx_env.step CPU: PASS
Open Duck Playground one-step GPU: TIMEOUT
closed-loop GPU: ROCM_ERROR_ILLEGAL_ADDRESS
closed-loop CPU short matrix: PASS
```

So the next GPU debug target is the raw Open Duck MJX physics step on ROCm,
not basic ROCm visibility, policy inference, reward code, rollout-loop shape,
or the fitted actuator bridge.

Independent CUDA check:

```text
Google Colab NVIDIA L4
JAX backend: gpu / cuda:0
closed-loop actuator bridge eval: PASS_CLOSED_LOOP_REPRODUCTION
```

This confirms the policy/sim/eval path is viable on a CUDA backend. The local
`7900 XTX` issue is specific to the ROCm/MJX Playground step path.

Device-node visibility has been checked locally:

```text
/dev/kfd and /dev/dri/renderD* are present
the device nodes are owned by root:render
user lsd is in the render group
plain JAX device discovery reports RocmDevice(id=0)
```

That means the current issue is not basic `/dev/kfd` access.

The RX `7900 XTX` architecture override suggestion was also tested. In this
environment, `TENSOR_PARALLEL_SIZE=1` is harmless for a basic JAX smoke test,
but `HSA_OVERRIDE_GFX_VERSION=11.0.0` is harmful:

```text
baseline basic JAX arithmetic -> PASS
TENSOR_PARALLEL_SIZE=1 -> PASS
HSA_OVERRIDE_GFX_VERSION=11.0.0 -> ROCM_ERROR_ILLEGAL_ADDRESS
HSA_OVERRIDE_GFX_VERSION=11.0.0 plus memory-safe flags -> ROCM_ERROR_ILLEGAL_ADDRESS
```

Do not put this in the training shell profile:

```bash
export HSA_OVERRIDE_GFX_VERSION=11.0.0
```

The card is already detected through normal ROCm/JAX device discovery. Forcing
the override breaks basic JAX before MuJoCo or MJX enter the picture.

Focused memory-allocation variants were tested on the smallest failing GPU
subtest (`playground_one_step_vanilla`):

```text
XLA_PYTHON_CLIENT_PREALLOCATE=false -> TIMEOUT
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

Follow-up execution-mode checks show this is not fixed by changing the rollout
wrapper alone:

```text
playground_direct_mjx_step -> TIMEOUT
playground_direct_mjx_step_jit -> TIMEOUT
playground_one_step_jit -> ROCM_ERROR_ILLEGAL_ADDRESS
playground_scan_step_vanilla -> ROCM_ERROR_ILLEGAL_ADDRESS
```

The direct-step probe shows the same Open Duck model and direct `mjx_env.step`
call pass on CPU, so the MJCF/model is valid enough for CPU and CUDA-backed
correctness work. The local hold is specific to the ROCm execution of the full
Open Duck MJX physics step.

Compiler/debug toggles were also tested on the scan subtest:

```text
JAX_DEBUG_NANS=true,JAX_DEBUG_INFS=true -> FloatingPointError in MJX convex collision
MIOPEN_DEBUG_FUSION_ENGINE_DISABLE=1 -> ROCM_ERROR_ILLEGAL_ADDRESS
MIOPEN_DEBUG_FUSION_ENGINE_DISABLE=1 plus conservative XLA flags -> TIMEOUT
```

The debug-nan/inf result is not GPU-specific: CPU reset fails under the same
debug flags because MJX convex collision uses a `-inf` sentinel internally.
That makes it a locator for the collision code path, not proof of corrupted
robot state.

Additional Triton/strict-IEEE variants were tested:

```text
--xla_gpu_enable_triton_softmax=false -> unknown XLA flag
ROCM_CHIP_COMPILER_FLAGS=-fno-fast-math -fhonor-infinities -fhonor-nans -> ROCM_ERROR_ILLEGAL_ADDRESS
--xla_gpu_target_cuda_data_dir=/opt/rocm/lib -> unknown XLA flag
```

Finite reset-state probes found no raw NaN/Inf in the checked MJX reset state
fields:

```text
qpos, qvel, qacc, ctrl, qfrc_constraint: finite
nan_count / posinf_count / neginf_count: 0
```

Post-reset sanitation of `qpos`, `qvel`, `qacc`, `ctrl`, and `act` does not
fix the GPU scan-step failure. The CPU sanitized scan passes; the GPU sanitized
scan still hits `ROCM_ERROR_ILLEGAL_ADDRESS`.

The active Open Duck Mini v2 XMLs rely on MuJoCo defaults for several
contact-relevant floor/foot `solref` and `solimp` values. That is now a
reasonable offline simulator-model probe, but do not change MJCF contact
parameters inside the training environment setup doc.

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
3. Run closed-loop actuator bridge eval. If local ROCm still reports
   `HOLD_SIM_RUNTIME_ERROR`, use the CUDA L4 `PASS_CLOSED_LOOP_REPRODUCTION`
   result as the current correctness reference.
4. Confirm current policy degrades in lagged sim like the real suspended
   `x=0.08` replay.
5. Only then implement or run a short ROCm smoke training job.

No policy should be exported for robot testing until suspended validation gates
are defined and passed.
