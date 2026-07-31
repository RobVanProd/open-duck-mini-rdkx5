# 7900 XTX Training Environment

Last updated: 2026-06-30

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
  mujoco-mjx 3.9.0
  playground 0.0.3
  ONNX Runtime 1.26.0
  ml_collections 1.1.0
  NumPy 2.4.6
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

## Post-Reset ROCm Recheck

After a full device power/reset cycle, the local ROCm path was rechecked on
2026-06-22. The reset did not clear the Open Duck MJX stepping blocker.

Curated evidence:

```text
outputs/analysis/ROCM_AFTER_RESET_RECHECK_20260622.md
```

Default ROCm result:

```text
basic JAX arithmetic: PASS
JAX jit/scan: PASS
minimal MJX step: PASS
Open Duck contract-only: PASS
Open Duck XML/contact audit: PASS
Open Duck reset: PASS, about 42 s
Open Duck reset finite-state probe: PASS, about 42 s
Open Duck direct mjx_env.step: TIMEOUT at 120 s
Open Duck direct mjx_env.step JIT: ROCm abort, return code -6
Open Duck one-step vanilla: TIMEOUT at 120 s
gate: HOLD_PLAYGROUND_GPU_STEP
```

Bad override result:

```text
HSA_OVERRIDE_GFX_VERSION=11.0.0 -> harmful
basic JAX GPU -> ROCM_ERROR_ILLEGAL_ADDRESS
CPU-labelled isolation rows -> ROCM_ERROR_ILLEGAL_ADDRESS
```

Do not use `HSA_OVERRIDE_GFX_VERSION=11.0.0` in this environment. ROCm already
detects the RX `7900 XTX` as `gfx1100`.

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

## Post-BIOS ROCm Recheck

After the host BIOS/firmware update, the local stack was rechecked on
2026-06-30 with:

```text
../envs/open-duck-playground/bin/python tools/isolate_rocm_mjx_failure.py \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json \
  --output-dir outputs/analysis/rocm_mjx_isolation_post_bios \
  --command-x 0.08 \
  --steps 1,2,10 \
  --platforms gpu,cpu \
  --include-bridge \
  --timeout-s 120
```

Evidence:

```text
outputs/analysis/rocm_mjx_isolation_post_bios/ROCM_MJX_RUNTIME_ISOLATION.md
outputs/analysis/rocm_mjx_isolation_post_bios/rocm_mjx_runtime_isolation.json
```

Result:

```text
gate_result: HOLD_PLAYGROUND_GPU_STEP
smallest_failing_subtest: default_gpu_playground_direct_mjx_step
basic JAX GPU: PASS
JAX jit/scan GPU: PASS
minimal MJX GPU: PASS
Playground reset GPU: PASS
Playground step GPU: FAIL/TIMEOUT
closed-loop GPU: FAIL
closed-loop CPU: PASS
```

So the BIOS update did not clear the Open Duck Playground ROCm/MJX stepping
blocker. The local `7900 XTX` remains useful for basic ROCm/JAX smoke tests and
limited non-Playground experiments, but it is not cleared for Phase 2
JAX/MJX training. Use local CPU only for reduced-horizon correctness checks.
Use CUDA/Colab or another known-good accelerator backend for Phase 2 training.

## PufferLib ROCm Archive Lead

The local archive `/home/lsd/Downloads/PufferLib.rar` was inspected as a
possible `7900 XT/XTX` ROCm clue.

Review artifact:

```text
outputs/analysis/PUFFERLIB_ROCM_ARCHIVE_REVIEW.md
```

The archive contains a PufferLib ROCm port runbook for AMD Radeon RX `7900 XT`
/ RDNA3 / `gfx1100`, focused on native Windows ROCm, PyTorch HIP, HIP graph
capture, PufferLib Ocean environments, and WSL ROCm/RCCL. It is useful context
for `gfx1100` ROCm work, but it does not document JAX, XLA, MuJoCo MJX,
`mjx_env.step(...)`, or a fix for the local Open Duck Playground ROCm step
failure.

Do not treat the PufferLib archive as the missing Open Duck MJX fix. It may be
useful only if the project intentionally starts a separate PufferLib/PyTorch
training integration later.

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

The same memory-allocation and conservative compiler variants were then tested
on the narrower direct `mjx_env.step(...)` subtest:

```text
XLA_PYTHON_CLIENT_PREALLOCATE=false -> TIMEOUT
XLA_PYTHON_CLIENT_MEM_FRACTION=0.50 -> TIMEOUT
XLA_PYTHON_CLIENT_MEM_FRACTION=0.60 -> TIMEOUT
XLA_PYTHON_CLIENT_ALLOCATOR=platform -> TIMEOUT
ROCM_CHIP_COMPILER_FLAGS=-fno-fast-math -fhonor-infinities -fhonor-nans -> TIMEOUT
MIOpen/XLA conservative flags -> TIMEOUT
```

So the simple per-process memory and strict-math workarounds also do not clear
the raw Open Duck MJX physics step.

## Version-Matrix Lead

The current local ROCm env differs from the passing CUDA/Colab path:

Current consolidated matrix summary:

```text
outputs/analysis/ROCM_VERSION_MATRIX_SUMMARY.md
```

```text
local 7900 XTX:
  jax/jaxlib 0.8.2
  mujoco/mujoco-mjx 3.9.0
  playground 0.0.3

passing CUDA/L4 cell:
  jax[cuda12] from the active pip index
  mujoco/mujoco-mjx constrained to >=3.2.7,<3.10
  playground==0.0.5
```

This is a useful ROCm follow-up lead, but do not mutate
`../envs/open-duck-playground` in place. Any package-version experiment should
use a disposable env and rerun the smallest direct-step gate first:

```text
playground_direct_mjx_step on gpu
```

Repeatable dry-run-first helper:

```bash
python3 tools/run_rocm_version_matrix.py
```

To create and run the disposable matrix:

```bash
python3 tools/run_rocm_version_matrix.py --apply
```

The helper uses `../envs/open-duck-playground-rocm-*` and does not mutate the
known `../envs/open-duck-playground` env. Add `--force-recreate` only when you
intentionally want to replace existing disposable matrix envs.

Suggested first disposable matrix:

```text
playground==0.0.5 with current mujoco/mujoco-mjx
mujoco/mujoco-mjx==3.3.7 with matching playground dependency
mujoco/mujoco-mjx==3.2.7 with matching playground dependency
```

Only promote a version set if `playground_direct_mjx_step` passes on ROCm and
the CPU/CUDA contract remains `obs=101`, `actions=14`.

First disposable matrix result:

```text
env: ../envs/open-duck-playground-rocm-playground005
jax/jaxlib: 0.8.2
jax-rocm7-pjrt/plugin: 0.8.2+rocm7.2.1
mujoco/mujoco-mjx: 3.9.0
playground: 0.0.5
evidence: outputs/analysis/rocm_mjx_version_matrix_playground005/
gate_result: HOLD_PLAYGROUND_GPU_STEP
smallest_failing_subtest: default_gpu_playground_direct_mjx_step
```

Result split:

```text
GPU basic JAX: PASS
GPU minimal MJX: PASS
GPU Open Duck contract: PASS
GPU Open Duck reset: PASS
GPU direct mjx_env.step: TIMEOUT after 120s
CPU direct mjx_env.step: PASS
```

Conclusion: aligning the external `mujoco_playground` package to the
CUDA-passing `playground==0.0.5` does not clear the local 7900 XTX direct Open
Duck MJX step hang when MuJoCo/MJX remains at `3.9.0`.

Second disposable matrix result:

```text
env: ../envs/open-duck-playground-rocm-mujoco337
jax/jaxlib: 0.8.2
jax-rocm7-pjrt/plugin: 0.8.2+rocm7.2.1
mujoco/mujoco-mjx: 3.3.7
playground: 0.0.5
evidence: outputs/analysis/rocm_mjx_version_matrix_mujoco337/
gate_result: HOLD_PLAYGROUND_GPU_STEP
smallest_failing_subtest: default_gpu_playground_direct_mjx_step
```

Result split:

```text
GPU basic JAX: PASS
GPU minimal MJX: PASS
GPU Open Duck contract: PASS
GPU Open Duck reset: PASS
GPU direct mjx_env.step: TIMEOUT after 120s
CPU direct mjx_env.step: PASS
```

Conclusion: downgrading MuJoCo/MJX to `3.3.7` with `playground==0.0.5` also
does not clear the local 7900 XTX direct Open Duck MJX step hang.

Third disposable matrix result:

```text
env: ../envs/open-duck-playground-rocm-mujoco327
jax/jaxlib: 0.8.2
jax-rocm7-pjrt/plugin: 0.8.2+rocm7.2.1
mujoco/mujoco-mjx: 3.2.7
playground: 0.0.5
evidence: outputs/analysis/rocm_mjx_version_matrix_mujoco327/
```

Result split:

```text
GPU basic JAX: PASS
GPU minimal MJX: PASS
GPU Open Duck contract: PASS
GPU Open Duck reset: FAIL
GPU direct mjx_env.step: FAIL
CPU Open Duck reset: FAIL
CPU direct mjx_env.step: FAIL
```

Failure:

```text
AttributeError: 'Data' object has no attribute '_impl'
```

Updated classification: `HOLD_ENV_API_INCOMPATIBLE`.

Conclusion: MuJoCo/MJX `3.2.7` is incompatible with the current
`playground==0.0.5` collision helper / Open Duck env path, so it is not a
candidate local ROCm fix.

The current `amdgpu` module parameter is:

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
