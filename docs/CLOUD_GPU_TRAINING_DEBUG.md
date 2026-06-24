# Cloud GPU Training Debug

This project currently treats cloud GPU training as an infrastructure thread,
separate from robot validation.

Robot status: parked. Do not run robot tests from this workflow.

## Current Status

Known-good:

- local CPU `training-smoke`: `PASS`
- local CPU candidate gates: `PASS_PLUMBING`
- Colab CUDA JAX device detection: `PASS` in prior manual notebook checks
- Colab L4 minimal CUDA PPO smoke: `PASS`
  - `num_envs=1`
  - `num_timesteps=8`
  - actuator bridge enabled
  - final manifest written
  - checkpoint saved at step 10

Current hold:

```text
Colab A100 training-smoke: HOLD_REMOTE_NO_SENTINEL
Colab L4 training-smoke: HOLD_REMOTE_NO_SENTINEL
Colab L4 8-env training-smoke diagnostic: HOLD_REMOTE_NO_SENTINEL
```

The minimal L4 run proves CUDA/JAX/Brax/Playground are usable at very small
scale. The remaining problem is scale-sensitive or long-compile/runtime related:
the 8-env / 64-timestep diagnostic disappeared without a final sentinel, while
the 1-env / 8-timestep diagnostic completed.

## Required Next Command

Use the staged startup diagnostic before launching another recipe:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --session open-duck-l4 \
  --workflow training-smoke-diagnostic \
  --run \
  --foreground-remote \
  --foreground-remote-timeout-s 1800 \
  --idle-no-sentinel-polls 5 \
  --timeout-s 1800 \
  --smoke-num-timesteps 8 \
  --smoke-ppo-num-envs 1 \
  --smoke-ppo-batch-size 1 \
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
`HOLD_REMOTE_TIMEOUT`. Because `google-colab-cli` cannot download directories
directly, the helper now falls back to tarring the remote output directory and
downloading that archive.

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
- compare against the passing 1-env / 8-timestep smoke before changing recipe
  code.
- keep recipe search on a stable backend or a known-good cloud scale until the
  cloud runtime is fixed.

If the run disappears without a sentinel:

- do not promote any partial checkpoint.
- inspect `remote_live.log`, `REMOTE_NO_SENTINEL.md`, and
  `partial_remote_output` if present.

## Current Scale Question

The passing L4 smoke used `num_envs=1` and `num_timesteps=8`.

The next point, `num_envs=1` and `num_timesteps=16`, reached runner setup but
disappeared before a `STEP:` line or final manifest.

The failing diagnostic used `num_envs=8` and `num_timesteps=64`.

The next cloud isolation step should sweep upward conservatively, for example:

```text
1 env / 8 timesteps   known PASS
1 env / 16 timesteps  known HOLD so far
2 env / 16 timesteps
4 env / 32 timesteps
8 env / 64 timesteps  known HOLD so far
```

Stop at the first scale that disappears or times out and preserve the partial
output bundle.

## Non-Goals

- Do not run robot validation from cloud GPU diagnostics.
- Do not change robot runtime behavior.
- Do not treat a partial cloud checkpoint as a candidate unless it later passes
  local closed-loop gates.
