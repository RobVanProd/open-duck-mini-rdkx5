# ROCm / MJX Debugging

Last updated: 2026-06-22

## Current Failure

Closed-loop actuator bridge eval reaches the correct Open Duck Playground
contract but fails on the local `7900 XTX` ROCm/MJX path:

```text
HOLD_SIM_RUNTIME_ERROR
ROCM_ERROR_ILLEGAL_ADDRESS
```

This is a backend/runtime failure. It is not a robot hardware result, not a
policy contract mismatch, and not evidence that the actuator model is wrong.

Tracking issue:

```text
https://github.com/RobVanProd/open-duck-mini-rdkx5/issues/19
```

## Isolation Result

Run:

```bash
../envs/open-duck-playground/bin/python tools/isolate_rocm_mjx_failure.py \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --output-dir outputs/analysis/rocm_mjx_isolation \
  --command-x 0.08 \
  --steps 1,2,10,100 \
  --platforms gpu,cpu \
  --include-bridge \
  --timeout-s 120
```

Result:

```text
gate_result: HOLD_PLAYGROUND_GPU_STEP
smallest_failing_subtest: default_gpu_playground_one_step_vanilla
```

Capability summary:

| test | result |
|---|---|
| basic JAX GPU arithmetic | `PASS` |
| JAX GPU jit/scan | `PASS` |
| minimal MJX GPU step/scan | `PASS` |
| Open Duck Playground contract construction on GPU | `PASS` |
| Open Duck Playground reset on GPU | `PASS` |
| Open Duck Playground one-step vanilla on GPU | `TIMEOUT` |
| Open Duck closed-loop GPU eval | `FAIL`, `ROCM_ERROR_ILLEGAL_ADDRESS` |
| CPU basic/JAX/MJX/contract/reset/one-step | `PASS` |
| CPU bridge short-horizon progress | passed through reduced steps before timeout |
| CPU closed-loop vanilla short matrix | `PASS` |

Interpretation:

```text
basic ROCm JAX works
minimal MJX works
Open Duck MJX model construction/reset works
Open Duck Playground GPU stepping is the smallest failing operation
the fitted bridge is not the smallest failure
```

## Post-Reset Recheck

After the workstation/GPU was fully power-cycled, the reduced one-step matrix
was rerun:

```bash
../envs/open-duck-playground/bin/python tools/isolate_rocm_mjx_failure.py \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --output-dir outputs/analysis/rocm_mjx_recheck_after_reset \
  --command-x 0.08 \
  --steps 1 \
  --platforms gpu,cpu \
  --include-bridge \
  --timeout-s 120
```

Result:

```text
gate_result: HOLD_PLAYGROUND_GPU_STEP
smallest_failing_subtest: default_gpu_playground_one_step_vanilla
```

Updated split:

| test | post-reset result |
|---|---|
| basic JAX GPU arithmetic | `PASS` |
| JAX GPU jit/scan | `PASS` |
| minimal MJX GPU step | `PASS` |
| Playground contract/reset/finite-state checks on GPU | `PASS` |
| Playground one-step vanilla on GPU | `TIMEOUT` |
| Playground one-step JIT on GPU | `FAIL`, returncode `-6` |
| Playground scan-step on GPU | `FAIL`, returncode `-6` |
| Playground bridge path on GPU | `TIMEOUT` |
| closed-loop GPU policy eval | `FAIL`, returncode `-6` |
| CPU one-step / JIT / scan / bridge / closed-loop | `PASS` |

The reset changed some GPU failures from hard aborts into timeouts, but it did
not clear the local ROCm/MJX blocker. CPU remains valid for reduced-horizon
correctness checks; CUDA remains the confirmed full closed-loop backend.

## Current Reduced Recheck

After the browser/Colab automated login path was blocked, the same reduced
one-step isolation was rerun locally:

```bash
../envs/open-duck-playground/bin/python tools/isolate_rocm_mjx_failure.py \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --output-dir outputs/analysis/rocm_mjx_recheck_current \
  --command-x 0.08 \
  --steps 1 \
  --platforms gpu,cpu \
  --include-bridge \
  --timeout-s 120
```

The result is unchanged:

```text
gate_result: HOLD_PLAYGROUND_GPU_STEP
smallest_failing_subtest: default_gpu_playground_one_step_vanilla
```

Current split:

| test | result |
|---|---|
| basic JAX GPU arithmetic | `PASS` |
| JAX GPU jit/scan | `PASS` |
| minimal MJX GPU step | `PASS` |
| Playground contract/reset/finite-state checks on GPU | `PASS` |
| Playground one-step vanilla/JIT/scan on GPU | `TIMEOUT` |
| Playground sanitized scan-step on GPU | `FAIL`, returncode `-6` |
| Playground bridge path on GPU | `TIMEOUT` |
| closed-loop GPU policy eval | `TIMEOUT` |
| CPU one-step / JIT / scan / bridge / closed-loop | `PASS` |

This confirms the local blocker is still the Open Duck Playground
`mjx_env.step(...)` path on ROCm, not the actuator bridge. CPU is usable for
reduced correctness checks. CUDA remains the backend that completed the full
closed-loop reproduction.

## Direct MJX Step Probe

The isolation tool now includes direct Open Duck `mjx_env.step(...)` probes so
the failing layer can be separated from the higher-level `Joystick.step()`
wrapper, reward code, policy inference, and actuator bridge.

Command:

```bash
../envs/open-duck-playground/bin/python tools/isolate_rocm_mjx_failure.py \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --output-dir outputs/analysis/rocm_mjx_direct_step_probe \
  --command-x 0.08 \
  --steps 1 \
  --platforms gpu,cpu \
  --subtests playground_reset,playground_direct_mjx_step,playground_direct_mjx_step_jit,playground_one_step_vanilla \
  --timeout-s 180
```

Result:

```text
gate_result: HOLD_PLAYGROUND_GPU_STEP
smallest_failing_subtest: default_gpu_playground_direct_mjx_step
```

Current direct-step split:

| test | GPU | CPU |
|---|---|---|
| Playground reset | `PASS` | `PASS` |
| direct `mjx_env.step(...)` | `TIMEOUT` | `PASS` |
| direct jitted `mjx_env.step(...)` | `TIMEOUT` | `PASS` |
| `Joystick.step(...)` one-step | `TIMEOUT` | `PASS` |

This narrows the local 7900 XTX issue further than the original closed-loop
failure. The full Open Duck MJX model can be instantiated and reset on ROCm,
but a single physics step of that model does not complete. The same model and
same step path pass on CPU. Therefore the smallest local blocker is the Open
Duck MJX physics step on ROCm, before policy inference, reward logic, actuator
bridge insertion, or rollout-loop structure matter.

## Direct Step Variant Probe

The smallest failing direct-step subtest was rerun with the main per-process
ROCm/JAX workaround variants:

```bash
../envs/open-duck-playground/bin/python tools/isolate_rocm_mjx_failure.py \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --output-dir outputs/analysis/rocm_mjx_direct_step_variants \
  --command-x 0.08 \
  --steps 1 \
  --platforms gpu \
  --subtests playground_direct_mjx_step \
  --variants preallocate_false,mem_fraction_050,mem_fraction_060,allocator_platform,rocm_strict_ieee,xla_compiler_conservative \
  --timeout-s 120
```

Result:

| variant | direct Open Duck `mjx_env.step(...)` result |
|---|---|
| `XLA_PYTHON_CLIENT_PREALLOCATE=false` | `TIMEOUT` |
| `XLA_PYTHON_CLIENT_MEM_FRACTION=0.50` | `TIMEOUT` |
| `XLA_PYTHON_CLIENT_MEM_FRACTION=0.60` | `TIMEOUT` |
| `XLA_PYTHON_CLIENT_ALLOCATOR=platform` | `TIMEOUT` |
| `ROCM_CHIP_COMPILER_FLAGS=-fno-fast-math -fhonor-infinities -fhonor-nans` | `TIMEOUT` |
| conservative MIOpen/XLA flags | `TIMEOUT` |

This does not prove the ROCm failure is impossible to fix, but it rules out the
simple per-process memory allocation and strict-math toggles as sufficient fixes
for the smallest failing Open Duck physics step in the current environment.

## Repeatable Version Matrix

Use this runner for future disposable package-version probes:

```bash
python3 tools/run_rocm_version_matrix.py
```

Default mode is dry-run only. It prints the commands for the known matrix cases
without creating envs or running probes. To create and run the current matrix:

```bash
python3 tools/run_rocm_version_matrix.py --apply
```

The runner uses disposable envs under:

```text
../envs/open-duck-playground-rocm-*
```

and leaves the known local env untouched:

```text
../envs/open-duck-playground
```

If you intentionally want to replace existing disposable matrix envs, add
`--force-recreate`.

Known case outcomes:

| case | outcome |
|---|---|
| `playground005` | `HOLD_PLAYGROUND_GPU_STEP` |
| `mujoco337` | `HOLD_PLAYGROUND_GPU_STEP` |
| `mujoco327` | `HOLD_ENV_API_INCOMPATIBLE` |

The `mujoco327` case fails on both CPU and GPU with:

```text
AttributeError: 'Data' object has no attribute '_impl'
```

That is a package/API mismatch, not a ROCm-only Open Duck physics-step hold.

## PufferLib / Torch ROCm Note

The workstation also has a local PufferLib HIP/ROCm tree:

```text
/home/lsd/Downloads/PufferLib.rar
/home/lsd/external/PufferLib-hip-4
```

That tree is useful evidence that this machine can run some ROCm RL workloads:
older six-pendulum reports under `/home/lsd/robotics-six-pendulums/reports/`
show stable PufferLib ROCm smoke/training runs. However, PufferLib is a
separate Torch-based RL stack with its own vectorized environment path. It does
not directly fix this issue, because the current blocker is inside the Open
Duck Playground JAX/MJX `mjx_env.step(...)` path.

Treat PufferLib as a future backend lead only if the project intentionally
ports or wraps the Open Duck environment outside MJX/JAX. For the current
actuator-bridge work, keep using CPU for reduced local correctness checks and
CUDA for full closed-loop eval/training.

## Evidence Files

Primary summaries:

```text
outputs/analysis/ROCM_MJX_RUNTIME_ISOLATION.md
outputs/analysis/rocm_mjx_runtime_isolation.json
```

Per-subtest logs:

```text
outputs/analysis/rocm_mjx_isolation/*.stdout.txt
outputs/analysis/rocm_mjx_isolation/*.stderr.txt
outputs/analysis/rocm_mjx_direct_step_probe/*.stdout.txt
outputs/analysis/rocm_mjx_direct_step_probe/*.stderr.txt
outputs/analysis/rocm_mjx_direct_step_variants/*.stdout.txt
outputs/analysis/rocm_mjx_direct_step_variants/*.stderr.txt
```

Important failure logs:

```text
default_gpu_playground_one_step_vanilla
default_gpu_playground_direct_mjx_step
default_gpu_playground_direct_mjx_step_jit
default_gpu_playground_multi_step_vanilla
default_gpu_playground_multi_step_bridge
default_gpu_closed_loop_policy_eval_gpu
```

## Backend vs Contract vs Actuator Model

The current stack is split cleanly:

| layer | status |
|---|---|
| real robot evidence | dynamic actuator lag at suspended `x=0.08` |
| actuator response fit | explains most target/actual lag |
| policy/sim contract | `PASS_POLICY_SIM_CONTRACT` |
| closed-loop bridge insertion point | implemented at target stage |
| CUDA closed-loop bridge eval | `PASS_CLOSED_LOOP_REPRODUCTION` |
| ROCm/MJX closed-loop step | blocked |

The local ROCm/MJX failure is no longer a blocker for correctness: the same
closed-loop bridge eval passed on Google Colab with an NVIDIA L4 / CUDA backend.
Do not train on the robot-facing path until the training-time actuator wrapper
is implemented and reviewed, but treat local ROCm debugging as a backend
workstream rather than a policy/sim-contract blocker.

## CPU Fallback

CPU can be used for small correctness probes because it passes:

```text
basic JAX
minimal MJX
Open Duck contract
Open Duck reset
Open Duck one-step
closed-loop vanilla short matrix
```

CPU is too slow under the current timeout for the full requested multi-step
bridge matrix. Treat CPU as a reduced-horizon correctness tool, not as a final
training path.

## Environment Toggles

The isolation tool supports these variants:

```text
default
preallocate_false              XLA_PYTHON_CLIENT_PREALLOCATE=false
mem_fraction_050               XLA_PYTHON_CLIENT_MEM_FRACTION=0.50
mem_fraction_060               XLA_PYTHON_CLIENT_MEM_FRACTION=0.60
allocator_platform             XLA_PYTHON_CLIENT_ALLOCATOR=platform
disable_jit                    JAX_DISABLE_JIT=true
debug_nans_infs                JAX_DEBUG_NANS=true, JAX_DEBUG_INFS=true
miopen_fusion_disabled         MIOPEN_DEBUG_FUSION_ENGINE_DISABLE=1
xla_disable_latency_scheduler  XLA_FLAGS=--xla_gpu_enable_latency_hiding_scheduler=false
xla_disable_triton_gemm        XLA_FLAGS=--xla_gpu_enable_triton_gemm=false
xla_disable_triton_gemm_softmax XLA_FLAGS=--xla_gpu_enable_triton_gemm=false plus --xla_gpu_enable_triton_softmax=false
xla_compiler_conservative      MIOPEN_DEBUG_FUSION_ENGINE_DISABLE=1 plus both XLA flags
rocm_strict_ieee               ROCM_CHIP_COMPILER_FLAGS=-fno-fast-math -fhonor-infinities -fhonor-nans
xla_rocm_data_dir              XLA_FLAGS=--xla_gpu_target_cuda_data_dir=/opt/rocm/lib
xla_triton_strict_ieee         strict IEEE flags plus Triton/data-dir XLA flags
```

JAX's GPU memory allocation docs describe preallocation behavior and these
memory allocator controls:

```text
https://docs.jax.dev/en/latest/gpu_memory_allocation.html
```

The committed main isolation run used `default`. A focused memory-variant run
was also performed against the smallest failing GPU subtest:

```text
subtest: playground_one_step_vanilla
variants:
  XLA_PYTHON_CLIENT_PREALLOCATE=false
  XLA_PYTHON_CLIENT_MEM_FRACTION=0.50
  XLA_PYTHON_CLIENT_MEM_FRACTION=0.60
  XLA_PYTHON_CLIENT_ALLOCATOR=platform
result: all timed out
```

So the simple JAX preallocation fix did not clear the Open Duck Playground
one-step GPU hang in this environment. It may still be relevant to the later
illegal-address abort, but it is not sufficient by itself for the smallest
failing operation.

Focused variant command:

```bash
../envs/open-duck-playground/bin/python tools/isolate_rocm_mjx_failure.py \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --output-dir outputs/analysis/rocm_mjx_isolation_memory_variants \
  --command-x 0.08 \
  --steps 1 \
  --platforms gpu \
  --subtests playground_one_step_vanilla \
  --variants preallocate_false,mem_fraction_050,mem_fraction_060,allocator_platform \
  --timeout-s 180
```

The host currently reports:

```text
/sys/module/amdgpu/parameters/cwsr_enable = 1
```

Changing CWSR is a system/kernel-module setting, not a normal per-process
Python environment switch. Do not change it from project tooling; it needs
explicit system-level approval and a rollback plan.

## 7900 XTX `gfx1100` Override Follow-Up

The host can see the RX `7900 XTX` device through the normal ROCm path without
forcing an architecture override:

```text
JAX backend: gpu
JAX devices: [RocmDevice(id=0)]
```

The local device nodes are present and readable through the `render` group:

```text
/dev/kfd
/dev/dri/renderD128
/dev/dri/renderD129
```

User `lsd` is already in the `render` group. This weakens the hypothesis that
the current MJX failure is caused by basic GPU visibility or device-node
permissions.

The suggested `TENSOR_PARALLEL_SIZE=1` and `HSA_OVERRIDE_GFX_VERSION=11.0.0`
settings were tested as isolated basic-JAX variants:

```bash
../envs/open-duck-playground/bin/python tools/isolate_rocm_mjx_failure.py \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --output-dir outputs/analysis/rocm_mjx_isolation_gfx_override \
  --command-x 0.08 \
  --steps 1 \
  --platforms gpu \
  --variants tensor_parallel_one,gfx1100_override,gfx1100_mem_safe \
  --subtests basic_jax \
  --timeout-s 60
```

Result:

| variant | result |
|---|---|
| `tensor_parallel_one` | `PASS` |
| `gfx1100_override` | `FAIL`, `ROCM_ERROR_ILLEGAL_ADDRESS` |
| `gfx1100_mem_safe` | `FAIL`, `ROCM_ERROR_ILLEGAL_ADDRESS` |

The combined memory-safe override variant used:

```text
HSA_OVERRIDE_GFX_VERSION=11.0.0
TENSOR_PARALLEL_SIZE=1
XLA_PYTHON_CLIENT_PREALLOCATE=false
XLA_PYTHON_CLIENT_MEM_FRACTION=0.60
```

It still failed during basic JAX GPU startup. In this local JAX `0.8.2` /
ROCm setup, do not export `HSA_OVERRIDE_GFX_VERSION=11.0.0`. The card is
already detected as a ROCm device without it, and the override makes the
smallest possible GPU smoke test fail.

Evidence:

```text
outputs/analysis/rocm_mjx_isolation_gfx_override/ROCM_MJX_RUNTIME_ISOLATION.md
outputs/analysis/rocm_mjx_isolation_gfx_override/rocm_mjx_runtime_isolation.json
```

## Scan / Compiler Follow-Up

The consultant hypothesis that a sequential `jax.lax.scan` rollout might avoid
the illegal address was tested directly.

Step-mode command:

```bash
../envs/open-duck-playground/bin/python tools/isolate_rocm_mjx_failure.py \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --output-dir outputs/analysis/rocm_mjx_isolation_step_modes_default \
  --command-x 0.08 \
  --steps 1 \
  --platforms gpu \
  --variants default \
  --subtests playground_one_step_jit,playground_scan_step_vanilla \
  --timeout-s 180
```

Result:

| subtest | result |
|---|---|
| `playground_one_step_jit` | `FAIL`, returncode `-6`, `ROCM_ERROR_ILLEGAL_ADDRESS` |
| `playground_scan_step_vanilla` | `FAIL`, returncode `-6`, `ROCM_ERROR_ILLEGAL_ADDRESS` |

So changing the rollout from direct step to JIT step or `lax.scan` does not fix
the Open Duck Playground GPU failure in this environment.

Compiler/debug variant command:

```bash
../envs/open-duck-playground/bin/python tools/isolate_rocm_mjx_failure.py \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --output-dir outputs/analysis/rocm_mjx_isolation_scan_variants \
  --command-x 0.08 \
  --steps 1 \
  --platforms gpu \
  --variants debug_nans_infs,miopen_fusion_disabled,xla_compiler_conservative \
  --subtests playground_scan_step_vanilla \
  --timeout-s 120
```

Result:

| variant | result |
|---|---|
| `debug_nans_infs` | `FAIL`, returncode `1`, `FloatingPointError` in MJX convex collision |
| `miopen_fusion_disabled` | `FAIL`, returncode `-6`, `ROCM_ERROR_ILLEGAL_ADDRESS` |
| `xla_compiler_conservative` | `TIMEOUT` |

`debug_nans_infs` is not a clean root-cause proof here. The same debug flags
also fail on CPU during Playground reset:

```text
FloatingPointError: invalid value (inf) encountered in broadcast_in_dim
mujoco/mjx/_src/collision_convex.py:_sat_gaussmap
edge_dist = jp.where(is_minkowski_face, edge_dist, -jp.inf)
```

That means the debug flags are catching an MJX convex-collision `-inf` sentinel
path that exists on CPU too. Treat this as a useful locator for the collision
code path, not as evidence that robot model state is numerically corrupt.

Local JAX `0.8.2` does not expose a `jax_three_fry_gpu_global_pool` config key;
it was not added as a supported variant.

## Triton / Strict Math Follow-Up

The suggested Triton and strict-IEEE compiler flags were tested on the
`playground_scan_step_vanilla` subtest:

```bash
../envs/open-duck-playground/bin/python tools/isolate_rocm_mjx_failure.py \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --output-dir outputs/analysis/rocm_mjx_isolation_triton_strict_variants \
  --command-x 0.08 \
  --steps 1 \
  --platforms gpu \
  --variants xla_disable_triton_gemm_softmax,rocm_strict_ieee,xla_rocm_data_dir,xla_triton_strict_ieee \
  --subtests playground_scan_step_vanilla \
  --timeout-s 90
```

Result:

| variant | result |
|---|---|
| `xla_disable_triton_gemm_softmax` | `FAIL`, unknown XLA flag `--xla_gpu_enable_triton_softmax=false` |
| `rocm_strict_ieee` | `FAIL`, `ROCM_ERROR_ILLEGAL_ADDRESS` |
| `xla_rocm_data_dir` | `FAIL`, unknown XLA flag `--xla_gpu_target_cuda_data_dir=/opt/rocm/lib` |
| `xla_triton_strict_ieee` | `FAIL`, unknown XLA flags for Triton softmax and data-dir |

So strict IEEE compiler flags alone do not clear the GPU fault, and the two
additional XLA flags suggested by the consultant are not accepted by this local
JAX/XLA build.

## Reset Finite-State / MJCF Contact Audit

The suggested reset-state sanitation was tested without changing simulator
source files:

```bash
../envs/open-duck-playground/bin/python tools/isolate_rocm_mjx_failure.py \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --output-dir outputs/analysis/rocm_mjx_isolation_sanitized_state \
  --command-x 0.08 \
  --steps 1 \
  --platforms gpu,cpu \
  --variants default \
  --subtests playground_xml_contact_audit,playground_reset_state_finite,playground_scan_step_sanitized \
  --timeout-s 120
```

Result:

| subtest | GPU | CPU |
|---|---|---|
| `playground_xml_contact_audit` | `PASS` | `PASS` |
| `playground_reset_state_finite` | `PASS` | `PASS` |
| `playground_scan_step_sanitized` | `FAIL`, `ROCM_ERROR_ILLEGAL_ADDRESS` | `PASS` |

Reset state fields checked by `playground_reset_state_finite` are finite on
both GPU and CPU:

```text
qpos, qvel, qacc, ctrl, qfrc_constraint: finite
nan_count / posinf_count / neginf_count: 0
```

Post-reset sanitation of `qpos`, `qvel`, `qacc`, `ctrl`, and `act` therefore
does not fix the GPU step fault. This weakens the idea that raw infinities in
reset state are the immediate trigger.

The XML contact audit found seven contact-relevant floor/foot entries without
explicit `solref` or `solimp`:

```text
scene_flat_terrain.xml floor
scene_flat_terrain_backlash.xml floor
scene_rough_terrain_backlash.xml floor
open_duck_mini_v2.xml left_foot_bottom_tpu
open_duck_mini_v2.xml right_foot_bottom_tpu
open_duck_mini_v2_backlash.xml left_foot_bottom_tpu
open_duck_mini_v2_backlash.xml right_foot_bottom_tpu
```

Do not patch these values blindly. They are now a plausible next offline
simulator-model probe because the GPU failure is localized to Open Duck
Playground stepping/collision, but changing them would alter the sim contract
and needs a separate reviewed PR.

## Power-Cycle Retest

The `7900 XTX` was fully unplugged for about 30 seconds after another ROCm
training job had previously died with a Torch/HIP launch failure. After
replugging, the smallest Open Duck Playground GPU probes were rerun:

```bash
../envs/open-duck-playground/bin/python tools/isolate_rocm_mjx_failure.py \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --output-dir outputs/analysis/rocm_mjx_isolation_after_power_reset \
  --command-x 0.08 \
  --steps 1 \
  --platforms gpu \
  --variants default \
  --subtests playground_reset,playground_one_step_vanilla,playground_one_step_jit,playground_scan_step_vanilla \
  --timeout-s 180
```

Result:

| subtest | result |
|---|---|
| `playground_reset` | `PASS` |
| `playground_one_step_vanilla` | `TIMEOUT` |
| `playground_one_step_jit` | `FAIL`, returncode `-6` |
| `playground_scan_step_vanilla` | `TIMEOUT` |

The power-cycle retest therefore did not clear the Open Duck Playground MJX GPU
step failure. That weakens the stale-device-state hypothesis for this specific
MJX issue, while still leaving ROCm runtime stability as a separate concern for
long Torch/PufferLib training jobs.

## Local Alternate Leads

Local PufferLib files exist:

```text
/home/lsd/Downloads/PufferLib.rar
/home/lsd/external/PufferLib-hip-4
```

This may become useful for a PyTorch/PufferLib training path after the sim
contract and actuator bridge are settled. It does not directly fix JAX/MJX
Playground stepping.

The AMD Schola + UnrealRoboticsLab article describes a separate AMD-friendly
pipeline:

```text
MJCF -> URLab MuJoCo-in-Unreal -> Schola Gymnasium/gRPC -> Python RL loop
```

That is a possible future alternate simulator/training stack, not a drop-in fix
for the current JAX/MJX backend issue.

## Next Recommendation

Choose one of these before training:

1. Inspect Open Duck Playground MJX collision/model features that differ from
   the minimal MJX test, especially mesh/convex contacts and missing explicit
   `solref` / `solimp` on foot/floor contact geoms.
2. Use CPU only for short correctness probes while resolving GPU stepping.
3. Investigate package/version compatibility for JAX 0.8.2, MuJoCo 3.9.0, and
   ROCm on the `7900 XTX`.
4. If a system-level change such as CWSR is tested, do it outside project
   tooling with explicit approval and a rollback plan.

Do not run robot motion, grounded replay, deployment, or training as part of
this backend debug step.
