# L4 8-Env / 64-Step CUDA Training Smoke Hold

Date: 2026-06-24

status: `HOLD_8ENV64_REMOTE_NO_SENTINEL`

## Command Shape

The Colab L4 session reran the original failing scale after the quiet-compile
poller fix:

```text
platform: gpu
JAX_PLATFORM_NAME: gpu
JAX_PLATFORMS: cuda
num_timesteps: 64
ppo_num_envs: 8
ppo_batch_size: 8
actuator bridge: enabled
idle_no_sentinel_polls: 18
```

## Result

The remote log reached the actual startup diagnostic smoke command:

```text
jax 0.7.2
jaxlib 0.7.2
brax 0.14.2
mujoco 3.9.0
mujoco-mjx 3.9.0
playground 0.0.5
backend gpu [CudaDevice(id=0)]
has_device_put_replicated True
diagnose_training_smoke_startup.py ... --smoke-num-timesteps 64 --ppo-num-envs 8 --ppo-batch-size 8 --run-smoke
```

The workflow then ended with:

```text
status: HOLD_REMOTE_NO_SENTINEL
idle_no_exit_polls: 18
idle_no_sentinel_polls_limit: 18
unchanged_log_polls: 3
local_partial_output_dir: None
workflow exit sentinel: MISSING
artifact bundle: MISSING
```

Read-only side inspection found the expected remote diagnostic/output paths were
missing after the run:

```text
/content/open-duck-mini-rdkx5/outputs/analysis/open_duck_colab_cli_training-smoke-diagnostic_20260624T091541Z/training_smoke_startup_diagnostic: MISSING
/content/open_duck_colab_cli_training-smoke-diagnostic_20260624T091541Z.exit: MISSING
/content/open_duck_colab_cli_training-smoke-diagnostic_20260624T091541Z_artifacts.tar.gz: MISSING
```

## Interpretation

The Colab L4 CUDA path is verified through:

```text
4 env / 32 timesteps
```

The original 8-env / 64-step scale still holds even after fixing the aggressive
poller. This looks like Colab runtime/session loss or a hard failure before the
diagnostic could persist stage artifacts, not a policy or robot issue.

Next cloud options:

```text
1. continue recipe work at a verified smaller smoke/training scale,
2. try an A100 session for the 8-env / 64-step smoke,
3. test intermediate scale 4 env / 64 timesteps or 8 env / 32 timesteps.
```

Robot status: parked. No robot SSH, deployment, runtime behavior change, or
hardware test was performed.
