# A100 Training Smoke No-Sentinel Summary

status: `HOLD_A100_TRAINING_SMOKE_NO_SENTINEL`

## Context

After V15B and V15C both disappeared on A100, the Colab workflow was reduced to
a minimal `training-smoke` path. This path runs only the tiny PPO smoke and
skips the heavier contract audit, baseline eval, staged curriculum, candidate
gates, and step-0 ONNX export.

Command:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --session open-duck-a100-smoke \
  --workflow training-smoke \
  --run \
  --timeout-s 1800 \
  --smoke-num-timesteps 64 \
  --smoke-export-min-step 1
```

Robot touched: `false`.

## Result

The pinned CUDA/JAX stack initialized correctly:

```text
jax 0.7.2
jaxlib 0.7.2
brax 0.14.2
mujoco 3.9.0
mujoco-mjx 3.9.0
playground 0.0.5
backend gpu [CudaDevice(id=0)]
has_device_put_replicated True
```

The workflow launched:

```text
tools/run_actuator_bridge_training_smoke.py
  --platform gpu
  --num-timesteps 64
  --export-min-step 1
  --ppo-num-envs 8
  --ppo-batch-size 8
  --ppo-num-minibatches 1
  --ppo-num-updates-per-batch 1
```

The Colab session then reported idle while the workflow exit sentinel was
missing and no artifact bundle existed:

```text
status: HOLD_REMOTE_NO_SENTINEL
unchanged_log_polls: 1
idle_no_exit_polls: 2
```

No final manifest, ONNX, checkpoint, stdout/stderr artifact bundle, or remote
exit code was recovered.

## Interpretation

The A100 issue is now isolated below the recipe level:

- not V15-specific
- not caused solely by step-0 ONNX export
- not caused solely by the larger V15 PPO env/batch configuration
- not caused by contract audit or closed-loop baseline eval

The failure occurs in or immediately after the minimal GPU PPO training smoke.
Treat this as an A100/Colab/JAX/Brax training-runtime hold. Do not spend more
A100 time on curriculum recipes until a minimal training smoke can write a
normal final manifest and exit sentinel.

## Next Step

Use a different backend for recipe iteration or isolate the PPO smoke locally
with CPU/L4 before returning to A100. The robot remains parked.
