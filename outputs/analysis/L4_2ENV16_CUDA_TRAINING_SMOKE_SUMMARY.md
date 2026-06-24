# L4 2-Env / 16-Step CUDA Training Smoke Summary

Date: 2026-06-24

status: `PASS_2ENV16_CUDA_TRAINING_SMOKE`

## Command Shape

The Colab L4 session ran the startup diagnostic at the next scale above the
passing 1-env / 16-step smoke:

```text
platform: gpu
JAX_PLATFORM_NAME: gpu
JAX_PLATFORMS: cuda
num_timesteps: 16
ppo_num_envs: 2
ppo_batch_size: 2
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
elapsed_s: 445.78
STEP: 20 reward: 8.948163986206055 reward_std: 3.5841026306152344
checkpoint: saved at step 20
```

## Interpretation

Colab L4 CUDA training smoke now passes at:

```text
2 env / 16 timesteps
```

The training stack is usable beyond the absolute-minimum smoke. The next scale
point is:

```text
4 env / 32 timesteps
```

Robot status: parked. No robot SSH, deployment, runtime behavior change, or
hardware test was performed.
