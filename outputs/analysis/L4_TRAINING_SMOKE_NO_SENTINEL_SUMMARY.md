# L4 Training Smoke No-Sentinel Summary

status: `HOLD_L4_TRAINING_SMOKE_NO_SENTINEL`

## Context

The same minimal `training-smoke` used for the A100 infrastructure check was
run on a fresh L4 Colab session to separate A100-specific failure from a broader
Colab/JAX/Brax runner issue.

Command:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --session open-duck-l4-smoke \
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

The tiny PPO smoke launched, then the remote Colab session reported idle while
the workflow exit sentinel was missing and no artifact bundle existed:

```text
status: HOLD_REMOTE_NO_SENTINEL
unchanged_log_polls: 0
idle_no_exit_polls: 2
```

No final manifest, ONNX, checkpoint, stdout/stderr artifact bundle, or remote
exit code was recovered.

## Interpretation

The minimal training-smoke failure is not A100-specific. It reproduces on L4
with the same pinned JAX/Brax/MuJoCo stack. The next debugging target is the
Colab remote execution/capture path or a generic GPU PPO smoke failure, not a
specific staged curriculum recipe.

The next infrastructure step should run the remote driver in a foreground
Colab-console mode for tiny smokes so the console captures the exit status
directly instead of relying on a detached background job and later sentinel
polling.

Robot validation remains blocked.
