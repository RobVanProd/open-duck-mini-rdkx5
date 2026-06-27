# L4 CUDA Training Smoke No-Sentinel Summary

status: `HOLD_L4_CUDA_TRAINING_SMOKE_NO_SENTINEL`

## Context

After fixing platform selection, the foreground L4 `training-smoke` was rerun
with:

```text
JAX_PLATFORM_NAME=gpu
JAX_PLATFORMS=cuda
```

The remote artifact bundler was also fixed to recreate its output directory
after repo extraction.

## Command

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --session open-duck-l4-smoke-cuda-platform \
  --workflow training-smoke \
  --run \
  --foreground-remote \
  --foreground-remote-timeout-s 1800 \
  --timeout-s 1800 \
  --smoke-num-timesteps 64 \
  --smoke-export-min-step 1
```

Robot touched: `false`.

## Result

The pinned stack initialized and the command reached the tiny PPO smoke:

```text
jax 0.7.2
jaxlib 0.7.2
brax 0.14.2
mujoco 3.9.0
mujoco-mjx 3.9.0
playground 0.0.5
backend gpu [CudaDevice(id=0)]
has_device_put_replicated True

tools/run_actuator_bridge_training_smoke.py
  --platform gpu
  --jax-platforms cuda
  --num-timesteps 64
  --export-min-step 1
  --ppo-num-envs 8
  --ppo-batch-size 8
```

The Colab session then reported idle without a workflow exit sentinel, artifact
bundle, smoke stdout/stderr, start manifest, final manifest, ONNX, or checkpoint.
Direct download of the expected smoke output paths failed because the smoke
output directory was never created.

```text
status: HOLD_REMOTE_NO_SENTINEL
unchanged_log_polls: 0
idle_no_exit_polls: 2
```

## Interpretation

The minimal PPO runner is valid locally on CPU, but Colab GPU dies during or
immediately before the tiny PPO smoke, even with explicit `JAX_PLATFORMS=cuda`.
This is now a cloud GPU training-runtime hold, not a recipe result.

The next useful path is to continue recipe/debug iteration on a stable backend
such as local CPU, while treating Colab GPU training as a separate runtime issue.

Robot validation remains blocked.
