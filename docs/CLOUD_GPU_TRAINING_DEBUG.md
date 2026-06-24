# Cloud GPU Training Debug

This project currently treats cloud GPU training as an infrastructure thread,
separate from robot validation.

Robot status: parked. Do not run robot tests from this workflow.

## Current Status

Known-good:

- local CPU `training-smoke`: `PASS`
- local CPU candidate gates: `PASS_PLUMBING`
- Colab CUDA JAX device detection: `PASS` in prior manual notebook checks

Current hold:

```text
Colab A100 training-smoke: HOLD_REMOTE_NO_SENTINEL
Colab L4 training-smoke: HOLD_REMOTE_NO_SENTINEL
Colab L4 foreground + JAX_PLATFORMS=cuda: HOLD_REMOTE_NO_SENTINEL
```

The L4 foreground run reached the tiny PPO smoke command but produced no smoke
output directory, manifest, stdout/stderr, ONNX, checkpoint, artifact bundle, or
exit sentinel.

## Required Next Command

Use the staged startup diagnostic before launching another recipe:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --session open-duck-l4 \
  --workflow training-smoke-diagnostic \
  --run \
  --foreground-remote \
  --foreground-remote-timeout-s 1800 \
  --timeout-s 1800 \
  --smoke-num-timesteps 64 \
  --smoke-export-min-step 1
```

It records one stage at a time:

```text
00_python_jax_device
01_import_training_stack
02_smoke_dry_run
03_smoke_run
```

The poller also attempts to recover the remote workflow output directory into
`partial_remote_output` before declaring `HOLD_REMOTE_NO_SENTINEL` or
`HOLD_REMOTE_TIMEOUT`.

If a notebook is connected in the browser but `google-colab-cli` reports no
active sessions, generate a diagnostic single-cell notebook instead:

```bash
python3 tools/print_cuda_colab_cell.py \
  --training-smoke-diagnostic \
  --rdk-branch codex/colab-cli-cuda-workflow \
  --playground-branch codex/forward-progress-reward \
  --handoff-dir /home/lsd/robots/cuda_colab_diagnostic_handoff
```

Then upload/open:

```text
/home/lsd/robots/cuda_colab_diagnostic_handoff/open_duck_cuda_smoke.ipynb
```

See `docs/CUDA_COLAB_SINGLE_CELL.md` for the manual notebook fallback.

## Backend Selection Rules

Use explicit JAX backend selection for every smoke/gate command.

Local CPU:

```text
JAX_PLATFORM_NAME=cpu
JAX_PLATFORMS=cpu
```

Colab/NVIDIA CUDA:

```text
JAX_PLATFORM_NAME=gpu
JAX_PLATFORMS=cuda
```

Do not use `JAX_PLATFORMS=gpu`; CUDA JAX expects the backend name `cuda`.

## Diagnostic Environment Toggles

Use these only for isolation runs, not as permanent training defaults.

GPU memory preallocation:

```bash
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_MEM_FRACTION=0.60
```

JAX documents that it preallocates GPU memory by default and exposes these
environment variables for memory-allocation debugging:
https://docs.jax.dev/en/latest/gpu_memory_allocation.html

NaN/Inf and JIT debugging:

```bash
export JAX_DEBUG_NANS=true
export JAX_DEBUG_INFS=true
export JAX_DISABLE_JIT=true
```

JAX debugging flags are documented here:
https://docs.jax.dev/en/latest/debugging/flags.html

JAX configuration options, including platform controls, are documented here:
https://docs.jax.dev/en/latest/config_options.html

## Interpretation Rules

If `00_python_jax_device` fails:

- debug JAX/CUDA installation before touching Open Duck code.

If `01_import_training_stack` fails:

- debug dependency pins or editable Playground install.

If `02_smoke_dry_run` fails:

- debug smoke runner arguments/path validation.

If `03_smoke_run` fails or disappears:

- the issue is inside the tiny PPO/Brax/MJX training path.
- keep recipe search on a stable backend until the cloud runtime is fixed.

If the run disappears without a sentinel:

- do not promote any partial checkpoint.
- inspect `remote_live.log`, `REMOTE_NO_SENTINEL.md`, and
  `partial_remote_output` if present.

## Non-Goals

- Do not run robot validation from cloud GPU diagnostics.
- Do not change robot runtime behavior.
- Do not treat a partial cloud checkpoint as a candidate unless it later passes
  local closed-loop gates.
