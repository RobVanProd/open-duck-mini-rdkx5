# ROCm Version Matrix Summary

generated_at: `2026-06-22T11:35:00Z`

## Executive Summary

The simple local ROCm package-version matrix did not clear the 7900 XTX Open
Duck MJX step blocker.

The local GPU can run:

- basic JAX GPU arithmetic
- simple JAX jit/scan tests
- minimal MJX model stepping
- Open Duck env construction
- Open Duck env reset for compatible MuJoCo/MJX versions

The remaining local backend blocker is still the full Open Duck MJX physics
step on ROCm:

```text
playground_direct_mjx_step on gpu
```

The practical project path remains:

```text
CUDA/L4/A100 for full candidate training and closed-loop eval
CPU for reduced local correctness checks
7900 XTX ROCm as a separate backend-debug workstream
```

## Matrix

| env | JAX / ROCm | MuJoCo / MJX | playground | GPU reset | GPU direct step | CPU direct step | decision |
|---|---|---|---|---|---|---|---|
| `../envs/open-duck-playground` | `0.8.2 / rocm7.2.1` | `3.9.0` | `0.0.3` | PASS | TIMEOUT / illegal address in broader runs | PASS | `HOLD_PLAYGROUND_GPU_STEP` |
| `../envs/open-duck-playground-rocm-playground005` | `0.8.2 / rocm7.2.1` | `3.9.0` | `0.0.5` | PASS | TIMEOUT | PASS | `HOLD_PLAYGROUND_GPU_STEP` |
| `../envs/open-duck-playground-rocm-mujoco337` | `0.8.2 / rocm7.2.1` | `3.3.7` | `0.0.5` | PASS | TIMEOUT | PASS | `HOLD_PLAYGROUND_GPU_STEP` |
| `../envs/open-duck-playground-rocm-mujoco327` | `0.8.2 / rocm7.2.1` | `3.2.7` | `0.0.5` | FAIL | FAIL | FAIL | incompatible API |

## Evidence

```text
outputs/analysis/rocm_mjx_direct_step_probe/ROCM_MJX_RUNTIME_ISOLATION.md
outputs/analysis/rocm_mjx_direct_step_variants/ROCM_MJX_RUNTIME_ISOLATION.md
outputs/analysis/rocm_mjx_version_matrix_playground005/ROCM_MJX_RUNTIME_ISOLATION.md
outputs/analysis/rocm_mjx_version_matrix_mujoco337/ROCM_MJX_RUNTIME_ISOLATION.md
outputs/analysis/rocm_mjx_version_matrix_mujoco327/ROCM_MJX_RUNTIME_ISOLATION.md
```

## Interpretation

`playground==0.0.5` matches the CUDA-passing Colab dependency, but it does not
fix local ROCm when MuJoCo/MJX remains at `3.9.0`.

MuJoCo/MJX `3.3.7` is compatible enough to construct/reset the Open Duck env
and step on CPU, but the direct Open Duck MJX step still times out on ROCm.

MuJoCo/MJX `3.2.7` is not compatible with the current `playground==0.0.5`
collision helper path:

```text
AttributeError: 'Data' object has no attribute '_impl'
```

So the quick version-matrix hypothesis is exhausted. Future local ROCm work
should focus on the Open Duck model features inside `mjx_env.step(...)`, ROCm
compiler/runtime behavior for that model, or an alternate backend architecture.

## Safety

These were offline runtime/backend checks only.

No robot tests, SSH, deployment, training, policy overwrite, gain changes,
offset changes, IMU remaps, action-scale changes, or phase changes were
performed.
