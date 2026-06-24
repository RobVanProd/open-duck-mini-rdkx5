# L4 Minimal CUDA Training Smoke Summary

Date: 2026-06-24

status: `PASS_MINIMAL_CUDA_TRAINING_SMOKE`

## Command

The Colab L4 session ran the startup diagnostic with the smallest real PPO
training smoke:

```bash
python3 tools/diagnose_training_smoke_startup.py \
  --playground-path /content/Open_Duck_Playground \
  --env-python /usr/bin/python3 \
  --platform gpu \
  --jax-platforms cuda \
  --output-dir outputs/analysis/manual_l4_minimal_smoke_diagnostic \
  --timeout-s 300 \
  --smoke-timeout-s 600 \
  --smoke-num-timesteps 8 \
  --export-min-step 1 \
  --ppo-num-envs 1 \
  --ppo-batch-size 1 \
  --run-smoke
```

## Result

```text
00_python_jax_device: PASS
01_import_training_stack: PASS
02_smoke_dry_run: PASS
03_smoke_run: PASS
```

The smoke run used:

```text
JAX_PLATFORM_NAME=gpu
JAX_PLATFORMS=cuda
jax backend: gpu
device: CudaDevice(id=0)
num_timesteps: 8
ppo_num_envs: 1
ppo_batch_size: 1
actuator bridge: enabled
```

Final smoke manifest:

```text
status: PASS_SMOKE_RUN
returncode: 0
elapsed_s: 361.21
STEP: 10 reward: 7.2996506690979 reward_std: 2.555509090423584
checkpoint: saved at step 10
```

## Interpretation

Colab L4 CUDA is not globally broken. The pinned JAX/Brax/MuJoCo/Playground
stack can initialize the 101-observation / 14-action Open Duck environment and
complete a tiny GPU PPO update with the actuator bridge enabled.

The remaining Colab hold is scale-sensitive or long-compile/runtime related:
the earlier `8` env / `64` timestep smoke disappeared without a final manifest,
while this `1` env / `8` timestep smoke completed.

Robot status: parked. No robot SSH, deployment, runtime behavior change, or
hardware test was performed.
