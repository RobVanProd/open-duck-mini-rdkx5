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

CUDA remains the full closed-loop eval/training backend. CPU remains useful for
small correctness checks.
