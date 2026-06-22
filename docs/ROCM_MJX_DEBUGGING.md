# ROCm / MJX Debugging

Last updated: 2026-06-21

## Current Failure

Closed-loop actuator bridge eval reaches the correct Open Duck Playground
contract but fails on the local `7900 XTX` ROCm/MJX path:

```text
HOLD_SIM_RUNTIME_ERROR
ROCM_ERROR_ILLEGAL_ADDRESS
```

This is a backend/runtime failure. It is not a robot hardware result, not a
policy contract mismatch, and not evidence that the actuator model is wrong.

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
```

Important failure logs:

```text
default_gpu_playground_one_step_vanilla
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
| ROCm/MJX closed-loop step | blocked |

Do not train until the backend/runtime failure is resolved or a reviewed CPU
correctness fallback produces enough evidence.

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

1. Run focused ROCm/MJX variants on `default_gpu_playground_one_step_vanilla`.
2. Inspect Open Duck Playground MJX model features that differ from the minimal
   MJX test.
3. Use CPU only for short correctness probes while resolving GPU stepping.
4. Investigate package/version compatibility for JAX 0.8.2, MuJoCo 3.9.0, and
   ROCm on the `7900 XTX`.

Do not run robot motion, grounded replay, deployment, or training as part of
this backend debug step.
