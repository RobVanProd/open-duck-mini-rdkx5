# L4 Platform-Fix Training Smoke Summary

status: `HOLD_L4_TRAINING_SMOKE_BAD_JAX_PLATFORMS`

## Context

After local CPU passed with `JAX_PLATFORMS=cpu`, the foreground L4 smoke was
rerun with the patched launcher. That patch incorrectly mapped logical
`--platform gpu` to:

```text
JAX_PLATFORM_NAME=gpu
JAX_PLATFORMS=gpu
```

## Result

The run produced a real remote exit code and recovered stdout/stderr, which is
an observability improvement over the earlier no-sentinel failures. The smoke
itself failed with:

```text
RuntimeError: Backend 'rocm' is not in the list of known backends: ['cpu', 'tpu', 'cuda'].
...
RuntimeError: Unable to initialize backend 'rocm': Backend 'rocm' is not in the list of known backends: ['cpu', 'tpu', 'cuda'].
(set JAX_PLATFORMS='' to automatically choose an available backend)
```

## Interpretation

`JAX_PLATFORMS=gpu` is not a valid CUDA JAX backend selector. For Colab/NVIDIA
GPU, the value must be `cuda`. For CPU, `cpu` is correct. For ROCm, use `rocm`
explicitly when the ROCm stack is ready.

Follow-up fix:

- `tools/run_actuator_bridge_training_smoke.py` now accepts `--jax-platforms`.
- CPU smoke defaults to `JAX_PLATFORMS=cpu`.
- GPU smoke leaves `JAX_PLATFORMS` unset unless explicitly provided.
- Colab CUDA workflows pass `--jax-platforms cuda`.
- Staged curriculum passes the same override through each training phase.
- The remote artifact bundler now recreates `OUT` after repo extraction so
  failure logs can be packaged.

Next check: rerun foreground L4 `training-smoke` with `JAX_PLATFORMS=cuda`.

Robot validation remains blocked.
