# Soft-Prior CPU Smoke

status: `PASS_SOFT_PRIOR_CPU_SMOKE`

## Purpose

Verify that the patched Playground runner can execute an offline training smoke
with the default-off soft-prior hook explicitly enabled.

This was not a candidate policy run.

## Command Shape

```text
python3 tools/run_actuator_bridge_training_smoke.py
  --run
  --platform cpu
  --jax-platforms cpu
  --disable-actuator-bridge
  --enable-soft-prior
  --soft-prior-config-json outputs/analysis/soft_prior_fragment_config.json
  --num-timesteps 16
  --export-min-step 1
  --ppo-num-envs 4
  --ppo-num-evals 1
  --ppo-episode-length 20
  --ppo-unroll-length 5
  --ppo-batch-size 4
  --ppo-num-minibatches 1
  --ppo-num-updates-per-batch 1
```

## Result

```text
status: PASS_SMOKE_RUN
returncode: 0
elapsed_s: 51.95
platform: cpu
soft_prior_enabled: true
soft_prior_scale: -0.05
soft_prior_phase_source: imitation_i
actuator_bridge_enabled: false
robot_touched: false
deploy_performed: false
```

Smoke output summary:

```text
STEP: 20 reward: 5.1626739501953125 reward_std: 0.876919150352478
checkpoint: /tmp/open_duck_soft_prior_cpu_smoke/smoke_20260625T082634Z_cpu/2026_06_25_042710_20
```

The wrapper resolved the soft-prior config to:

```text
/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/soft_prior_fragment_config.json
```

## Notes

The CPU smoke printed expected nonfatal local-environment warnings:

```text
CUDA not available for the CPU-forced run
warp / mujoco_warp not installed
XLA CPU AOT feature warning
```

The run still completed and wrote `PASS_SMOKE_RUN`.

No raw `/tmp` training logs, checkpoint directories, or ONNX files were
committed.

## Safety

No robot tests, SSH, deployment, robot runtime behavior changes, policy file
changes, or deployable candidate generation were performed.
