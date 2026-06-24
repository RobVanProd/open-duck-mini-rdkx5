# L4 1-Env / 16-Step CUDA Training Smoke Hold

Date: 2026-06-24

status: `HOLD_1ENV16_CUDA_TRAINING_SMOKE`

## Command Shape

The Colab L4 session ran the startup diagnostic at the next scale above the
known passing smoke:

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
03_smoke_run: RUNNING marker only
final manifest: MISSING
workflow exit sentinel: MISSING
artifact bundle: MISSING
```

The smoke subprocess wrote:

```text
smoke_manifest.start.json
stdout.txt
stderr.txt
```

The stdout reached environment setup and PPO parameter printing:

```text
Observation size: 101
num_timesteps: 16
num_envs: 1
batch_size: 1
Skipping checkpoint/export at step 0; export_min_step=1
```

No `STEP:` line and no final manifest were produced.

## Interpretation

The previous `1` env / `8` timestep CUDA smoke passed, including a step line,
checkpoint, and final manifest. This `1` env / `16` timestep run reached the
same runner setup point but disappeared before the first reported step.

The Colab GPU training issue is therefore not a basic JAX/CUDA import or Open
Duck environment-instantiation issue. It appears during the actual Brax/PPO
training execution window, and may be sensitive to training horizon, compile
shape, Colab runtime lifetime, or the Colab CLI console/poller behavior.

Robot status: parked. No robot SSH, deployment, runtime behavior change, or
hardware test was performed.
