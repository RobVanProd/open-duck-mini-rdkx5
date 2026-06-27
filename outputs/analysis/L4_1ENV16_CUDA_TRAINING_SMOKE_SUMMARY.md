# L4 1-Env / 16-Step CUDA Training Smoke Summary

Date: 2026-06-24

status: `PASS_1ENV16_CUDA_TRAINING_SMOKE`

## Command Shape

The Colab L4 session ran the startup diagnostic at the next scale above the
first known passing smoke:

```text
platform: gpu
JAX_PLATFORM_NAME: gpu
JAX_PLATFORMS: cuda
num_timesteps: 16
ppo_num_envs: 1
ppo_batch_size: 1
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
elapsed_s: 423.93
STEP: 20 reward: 7.24683952331543 reward_std: 2.536440372467041
checkpoint: saved at step 20
```

## Interpretation

The earlier `1` env / `16` timestep hold was a poller false positive: the
remote run was still in a long quiet JAX/Brax compile/training window. After the
Colab helper stopped treating unchanged logs alone as a lost-sentinel condition,
the same scale completed and produced a final manifest, ONNX export, checkpoint,
workflow exit sentinel, and artifact bundle.

The known passing Colab L4 CUDA training-smoke scale is now at least:

```text
1 env / 16 timesteps
```

Next scale point:

```text
2 env / 16 timesteps
```

Robot status: parked. No robot SSH, deployment, runtime behavior change, or
hardware test was performed.
