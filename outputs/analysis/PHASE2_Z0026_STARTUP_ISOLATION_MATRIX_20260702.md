# Phase 2 z=0.0026 Startup Isolation Matrix

status: `HOLD_GPU_STARTUP_PATH`
date: `2026-07-02`
scope: offline sim/training diagnostics only

## Executive Summary

The phase-2 z=0.0026 training startup issue now isolates to the GPU/Colab path, not the recipe wiring itself.

Four local CPU smoke runs completed and exported ONNX:

- baseline PPO path
- restore checkpoint + restore-policy KL path
- behavior-prior path
- restore checkpoint + restore-policy KL + behavior-prior path

The direct A100/Colab run reached the same restore-policy/behavior-prior startup region, then disappeared during the PPO/JAX compile/update window with no final manifest, traceback, checkpoint, or ONNX. That makes the next blocker a GPU runtime/process-survival issue, not a candidate-quality result.

No robot test, SSH, deploy, grounded replay, or runtime behavior change was performed.

## Matrix

| test | platform | restore | restore KL | behavior prior | bridge | terrain | status | return code | output |
|---|---|---:|---:|---:|---:|---|---|---:|---|
| CPU baseline | cpu | no | no | no | disabled | rough z=0.0026 | `PASS_SMOKE_RUN` | 0 | checkpoint + ONNX |
| CPU restore/KL | cpu | yes | yes | no | disabled | rough z=0.0026 | `PASS_SMOKE_RUN` | 0 | checkpoint + ONNX |
| CPU behavior prior | cpu | no | no | yes | disabled | rough z=0.0026 | `PASS_SMOKE_RUN` | 0 | checkpoint + ONNX |
| CPU restore/KL + behavior prior | cpu | yes | yes | yes | disabled | rough z=0.0026 | `PASS_SMOKE_RUN` | 0 | checkpoint + ONNX |
| Direct A100 restored phase-2 smoke | gpu/cuda | yes | yes | yes | configured in smoke path | rough z=0.0026 | `HOLD_PROCESS_DISAPPEARED` | unknown | no final manifest, no checkpoint, no ONNX |

## Local CPU Evidence

All CPU runs used:

- `/home/lsd/robots/envs/open-duck-playground/bin/python`
- `JAX_PLATFORM_NAME=cpu`
- `JAX_PLATFORMS=cpu`
- `ppo_num_envs=1`
- `ppo_episode_length=64`
- `ppo_unroll_length=8`
- `ppo_batch_size=8`
- `ppo_num_timesteps=64`
- `export_min_step=1`
- `rough_terrain_backlash` with `terrain_hfield_z_scale=0.0026`

Summary:

| run | final manifest | elapsed | reward line |
|---|---|---:|---|
| baseline | `/tmp/open_duck_phase2_startup_cpu_baseline/smoke_20260702T022034Z_cpu/smoke_manifest.final.json` | 180.01s | `STEP: 64 reward: 6.317789077758789 reward_std: 2.8741326332092285` |
| restore/KL | `/tmp/open_duck_phase2_startup_cpu_restore_kl/smoke_20260702T022349Z_cpu/smoke_manifest.final.json` | 120.03s | `STEP: 64 reward: 22.94146728515625 reward_std: 6.999323844909668` |
| behavior prior | `/tmp/open_duck_phase2_startup_cpu_behavior_prior/smoke_20260702T022604Z_cpu/smoke_manifest.final.json` | 150.05s | `STEP: 64 reward: 6.308642387390137 reward_std: 2.8714842796325684` |
| restore/KL + behavior prior | `/tmp/open_duck_phase2_startup_cpu_restore_behavior_combined/smoke_20260702T023213Z_cpu/smoke_manifest.final.json` | 120.04s | `STEP: 64 reward: 22.978134155273438 reward_std: 7.006093502044678` |

Each CPU run wrote a checkpoint and ONNX at step 64.

## A100/Colab Evidence

The direct Colab probe was collected under:

`outputs/analysis/colab_cli/direct_probe2_20260702T0211Z/extracted/open_duck_direct_phase2_training2/smoke_20260702T021124Z_gpu/`

Observed facts:

- `smoke_manifest.start.json` exists.
- `smoke_manifest.live.json` exists.
- stdout/stderr exist.
- The run reached Playground contract/setup and restore-policy KL setup.
- The process then disappeared during the first PPO/JAX compile/update window.
- There is no `smoke_manifest.final.json`.
- There is no checkpoint.
- There is no ONNX export.
- There is no Python traceback in the captured logs.

The high-level Colab workflow showed the same broad symptom earlier: it printed `RUN_PLANNED`, then no sentinel/artifact appeared.

## Interpretation

The CPU matrix removes these as primary startup blockers:

- z=0.0026 terrain XML override
- restore checkpoint loading
- restore-policy KL wiring
- behavior-prior MLP wiring
- restore-policy KL combined with behavior prior
- tiny PPO/export path in the local Playground runner

The remaining startup blocker is the GPU/A100 path or the Colab process-survival path. The next GPU probe should be a detached direct run with artifact polling, starting from the smallest GPU baseline and adding features one at a time:

1. GPU baseline, no restore, no behavior prior, bridge disabled.
2. GPU restore/KL only.
3. GPU behavior prior only.
4. GPU restore/KL + behavior prior.
5. Only then re-enable bridge and larger phase-2 shape.

Do not treat the A100 disappearance as a policy-quality failure.

## Safe Point

At the time this report was written:

- no Colab sessions were active;
- no phase-2 smoke or Playground runner process was active locally;
- the unrelated `so101_dreamer_ue` training process was still present and was not touched.

## Gate

`HOLD_GPU_STARTUP_PATH`

Phase 2 remains active. The current result is an infrastructure isolation result, not a deployable candidate.
