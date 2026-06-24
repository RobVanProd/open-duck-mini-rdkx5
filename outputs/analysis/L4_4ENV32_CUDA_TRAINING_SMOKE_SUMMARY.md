# L4 4-Env / 32-Step CUDA Training Smoke Summary

Date: 2026-06-24

status: `PASS_4ENV32_CUDA_TRAINING_SMOKE`

## Command Shape

The Colab L4 session ran the startup diagnostic at the next scale above the
passing 2-env / 16-step smoke:

```text
platform: gpu
JAX_PLATFORM_NAME: gpu
JAX_PLATFORMS: cuda
num_timesteps: 32
ppo_num_envs: 4
ppo_batch_size: 4
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
elapsed_s: 437.48
STEP: 40 reward: 11.187263488769531 reward_std: 4.4381818771362305
checkpoint: saved at step 40
```

## Interpretation

Colab L4 CUDA training smoke now passes at:

```text
4 env / 32 timesteps
```

The original 8-env / 64-step hold should be rerun with the corrected quiet
compile polling before treating it as a real scale limit.

Robot status: parked. No robot SSH, deployment, runtime behavior change, or
hardware test was performed.
