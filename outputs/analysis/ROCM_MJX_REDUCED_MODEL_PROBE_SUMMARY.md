# ROCm MJX Reduced Model Probe Summary

generated_at: `2026-06-22T11:55:00Z`

## Executive Summary

The reduced-model probe split the local 7900 XTX ROCm/MJX hold more precisely:

```text
single raw mjx.step on GPU: PASS
10-step lax.scan of mjx.step on CPU: PASS
10-step lax.scan of mjx.step on GPU: TIMEOUT / ROCM_ERROR_ILLEGAL_ADDRESS
```

This means the current local blocker is not simply:

```text
the Open Duck MJCF model cannot compile on ROCm
or
a single raw MJX step of the model cannot run on ROCm
or
mesh foot collision alone
```

The failure is now narrowed to ROCm execution of the scanned substep structure
used by `mujoco_playground._src.mjx_env.step(...)`.

## Probe Matrix

| probe | platform | n_substeps | baseline | no_contact | box_feet_no_visual |
|---|---|---:|---|---|---|
| raw single step | GPU | 1 | PASS | PASS | PASS |
| scanned substep loop | CPU | 10 | PASS | PASS | PASS |
| scanned substep loop | GPU | 10 | TIMEOUT | TIMEOUT | FAIL / `ROCM_ERROR_ILLEGAL_ADDRESS` |

## Commands Run

GPU one-step:

```bash
../envs/open-duck-playground/bin/python tools/probe_reduced_mjx_models.py \
  --source-xml-dir ../Open_Duck_Playground/playground/open_duck_mini_v2/xmls \
  --env-python ../envs/open-duck-playground/bin/python \
  --platforms gpu \
  --variants baseline,no_contact,box_feet_no_visual \
  --n-substeps 1 \
  --timeout-s 60 \
  --output-dir outputs/analysis/rocm_mjx_reduced_model_probe_gpu
```

CPU 10-substep comparison:

```bash
../envs/open-duck-playground/bin/python tools/probe_reduced_mjx_models.py \
  --source-xml-dir ../Open_Duck_Playground/playground/open_duck_mini_v2/xmls \
  --env-python ../envs/open-duck-playground/bin/python \
  --platforms cpu \
  --variants baseline,no_contact,box_feet_no_visual \
  --n-substeps 10 \
  --timeout-s 120 \
  --output-dir outputs/analysis/rocm_mjx_reduced_model_probe_cpu_substeps10
```

GPU 10-substep reproduction:

```bash
../envs/open-duck-playground/bin/python tools/probe_reduced_mjx_models.py \
  --source-xml-dir ../Open_Duck_Playground/playground/open_duck_mini_v2/xmls \
  --env-python ../envs/open-duck-playground/bin/python \
  --platforms gpu \
  --variants baseline,no_contact,box_feet_no_visual \
  --n-substeps 10 \
  --timeout-s 60 \
  --output-dir outputs/analysis/rocm_mjx_reduced_model_probe_gpu_substeps10
```

## Interpretation

Disabling contact did not clear the GPU 10-substep hold:

```text
baseline: TIMEOUT
no_contact: TIMEOUT
```

Replacing foot collision meshes with simple boxes and removing visual meshes did
not clear the issue either; it produced a hard ROCm failure:

```text
ROCM_ERROR_ILLEGAL_ADDRESS
```

The next local ROCm debug target is therefore the `jax.lax.scan` substep
execution path around `mjx.step`, not TPU foot mesh collision by itself.

CUDA remains the full closed-loop eval/training backend. CPU remains valid for
reduced correctness checks. No robot hardware, SSH, deployment, training, or
runtime behavior changes were involved.
