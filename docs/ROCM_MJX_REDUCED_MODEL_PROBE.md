# ROCm MJX Reduced Model Probe

Last updated: 2026-06-22

## Purpose

This probe generates reduced Open Duck MJCF variants and runs raw MJX stepping
in subprocesses with explicit timeouts. It is for local `7900 XTX` ROCm backend
debugging only.

No robot hardware, SSH, deployment, policy overwrite, runtime behavior change,
or training is involved.

## Tool

```bash
../envs/open-duck-playground/bin/python tools/probe_reduced_mjx_models.py --help
```

The tool:

- copies the Open Duck XML files into an output directory
- symlinks assets only inside the transient working output
- generates reduced variants such as `no_contact` and `box_feet_no_visual`
- runs each probe in a subprocess
- sets `JAX_PLATFORM_NAME` per subprocess
- records stdout/stderr tails and pass/fail/timeout status

Do not commit transient generated variant directories with absolute asset
symlinks. Commit only curated summaries unless raw logs are explicitly needed.

## Current Result

Current summary:

```text
outputs/analysis/ROCM_MJX_REDUCED_MODEL_PROBE_SUMMARY.md
outputs/analysis/rocm_mjx_reduced_model_probe_summary.json
outputs/analysis/ROCM_MJX_LOOP_MODE_PROBE_SUMMARY.md
outputs/analysis/rocm_mjx_loop_mode_probe_summary.json
```

Result:

```text
single raw mjx.step on GPU: PASS
10-step lax.scan of mjx.step on CPU: PASS
10-step lax.scan of mjx.step on GPU: TIMEOUT / ROCM_ERROR_ILLEGAL_ADDRESS
```

## Interpretation

The local ROCm blocker is now narrower than “Open Duck MJX cannot run on
7900 XTX.”

What passes:

```text
model compile
model reset in compatible envs
single raw mjx.step on GPU
10-substep scan on CPU
```

What fails:

```text
10-substep lax.scan of mjx.step on GPU
```

Disabling contact did not clear the GPU 10-substep hold. Replacing foot
collision meshes with simple boxes and removing visual meshes did not clear it
either.

The next ROCm debug target is therefore the JAX/ROCm substep-scan execution
path around `mjx.step`, not foot contact alone.

## Loop-Mode Follow-Up

The loop-mode probe tested the baseline model with `n_substeps=10`:

| loop mode | GPU result |
|---|---|
| `scan` | `TIMEOUT` |
| `fori` | `TIMEOUT` |
| `python` | `PASS` |
| `python_block_each` | `PASS` |

Interpretation:

```text
10 sequential MJX steps can run on ROCm when driven from the host.
JAX control-flow lowering of the repeated MJX step is the local blocker.
```

This suggests a slow local ROCm correctness-eval workaround may be possible by
using a host Python substep loop. It is not a training-throughput solution.

CUDA remains the full closed-loop eval/training backend. CPU remains useful for
small correctness checks.

## Closed-Loop Host-Loop Smoke

The closed-loop actuator bridge evaluator now has an explicit eval-only
substep mode:

```bash
../envs/open-duck-playground/bin/python tools/eval_policy_with_actuator_bridge.py \
  --mode closed-loop-sim \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --command-x 0.08 \
  --duration 0.2 \
  --bridge-mode vanilla \
  --jax-platform gpu \
  --mjx-step-loop-mode python \
  --closed-loop-timeout-s 300 \
  --sim-preflight-timeout-s 300 \
  --output-dir outputs/analysis/rocm_host_loop_closed_loop_smoke_python
```

Result on the local `7900 XTX`:

| mode | result | samples | wall clock |
|---|---|---:|---:|
| `python` | `PASS_CLOSED_LOOP_REPRODUCTION` | 10 | 104.79s |
| `python_block_each` | `PASS_CLOSED_LOOP_REPRODUCTION` | 10 | 107.02s |

This confirms the host-loop workaround can carry the full closed-loop eval path
for tiny correctness probes on ROCm. It is far too slow for full 15-second evals
or training.
