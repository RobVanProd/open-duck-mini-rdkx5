# Local CPU Training Smoke Summary

status: `PASS_LOCAL_CPU_TRAINING_SMOKE`

## Context

After Colab A100/L4 `training-smoke` runs disappeared without sentinels, the
same tiny smoke was run locally on CPU. The first local attempt failed because
JAX still tried to initialize the installed ROCm backend even with
`JAX_PLATFORM_NAME=cpu`.

The smoke launcher was fixed to set both:

```text
JAX_PLATFORM_NAME=cpu
JAX_PLATFORMS=cpu
```

## Command

```bash
python3 tools/run_actuator_bridge_training_smoke.py \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --platform cpu \
  --run \
  --output-root outputs/analysis/local_training_smoke_cpu \
  --num-timesteps 64 \
  --export-min-step 1 \
  --ppo-num-envs 8 \
  --ppo-num-evals 1 \
  --ppo-episode-length 50 \
  --ppo-unroll-length 5 \
  --ppo-batch-size 8 \
  --ppo-num-minibatches 1 \
  --ppo-num-updates-per-batch 1 \
  --target-rate-scale -0.01 \
  --actuator-tracking-scale 0.0 \
  --timeout-s 1200
```

Robot touched: `false`.

## Result

The rerun passed:

```text
status: PASS_SMOKE_RUN
returncode: 0
elapsed_s: 54.36
STEP: 80 reward: 11.251152038574219 reward_std: 4.502880573272705
Skipping checkpoint/export at step 0; export_min_step=1
Saving checkpoint (step: 80): .../smoke_20260624T074158Z_cpu/2026_06_24_034235_80
```

The final manifest was written at:

```text
outputs/analysis/local_training_smoke_cpu/smoke_20260624T074158Z_cpu/smoke_manifest.final.json
```

## Interpretation

The Open Duck PPO smoke runner is valid outside Colab. The previous local CPU
failure was a platform-selection issue caused by the installed ROCm backend, and
setting `JAX_PLATFORMS` fixes it.

The next cloud check should rerun the minimal GPU smoke with the patched launcher
so the remote environment sets both `JAX_PLATFORM_NAME=gpu` and
`JAX_PLATFORMS=gpu`.

Robot validation remains blocked.
