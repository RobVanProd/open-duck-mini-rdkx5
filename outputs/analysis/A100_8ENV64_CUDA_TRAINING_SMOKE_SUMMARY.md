# A100 8-Env / 64-Step CUDA Training Smoke Summary

Date: 2026-06-24

status: `PASS_A100_8ENV64_CUDA_TRAINING_SMOKE`

## Command Shape

The Colab A100 session ran the same scale that held on L4:

```text
platform: gpu
JAX_PLATFORM_NAME: gpu
JAX_PLATFORMS: cuda
num_timesteps: 64
ppo_num_envs: 8
ppo_batch_size: 8
actuator bridge: enabled
```

## Result

```text
00_python_jax_device: PASS
01_import_training_stack: PASS
02_smoke_dry_run: PASS
03_smoke_run: PASS
workflow exit sentinel: 0
artifact bundle: downloaded
```

Final smoke manifest:

```text
status: PASS_SMOKE_RUN
returncode: 0
elapsed_s: 362.05
STEP: 80 reward: 11.273723602294922 reward_std: 4.483529567718506
checkpoint: saved at step 80
```

GPU evidence from stderr:

```text
device: NVIDIA A100-SXM4-40GB
visible memory in TensorFlow export subprocess: 8075 MB
compute capability: 8.0
```

## Interpretation

The 8-env / 64-step CUDA smoke is viable on A100. The L4 hold at the same scale
is likely a Colab L4 runtime/session capacity issue rather than a generic
JAX/Brax/Open Duck training failure.

Use A100 for the next substantial candidate training run when available.

Robot status: parked. No robot SSH, deployment, runtime behavior change, or
hardware test was performed.
