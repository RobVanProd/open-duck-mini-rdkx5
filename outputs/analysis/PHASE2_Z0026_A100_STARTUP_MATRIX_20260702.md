# Phase 2 z=0.0026 A100 Startup Matrix

status: `PASS_A100_STARTUP_MATRIX`
date: `2026-07-02`
session: `open-duck-a100-startup`
hardware: `NVIDIA A100-SXM4-40GB`
scope: offline Colab/A100 startup diagnostics only

## Executive Summary

The A100 startup failure was not reproduced when using the `colab exec` transport, pinned JAX/JAXlib `0.7.2`, and the same tiny 64-step startup shape.

The following A100 paths completed with return code `0`, final manifests, checkpoints, and ONNX exports:

- baseline GPU startup diagnostic;
- restore checkpoint + restore-policy KL;
- behavior prior;
- restore checkpoint + restore-policy KL + behavior prior;
- restore checkpoint + restore-policy KL + behavior prior + smoke-runner actuator bridge.

This supersedes the earlier `HOLD_PROCESS_DISAPPEARED` as the current infrastructure result for the pinned `colab exec` path. The earlier disappearing run remains useful evidence about the flaky path, but it is not reproduced here.

No robot test, SSH, deploy, grounded replay, or runtime behavior change was performed.

## Matrix

| test | platform | restore | restore KL | behavior prior | bridge | status | return code | elapsed |
|---|---|---:|---:|---:|---:|---|---:|---:|
| baseline diagnostic | A100/CUDA | no | no | no | smoke diagnostic | `PASS` | 0 | 360.11s smoke stage |
| restore/KL | A100/CUDA | yes | yes | no | disabled | `PASS_SMOKE_RUN` | 0 | 480.03s |
| behavior prior | A100/CUDA | no | no | yes | disabled | `PASS_SMOKE_RUN` | 0 | 480.03s |
| restore/KL + behavior prior | A100/CUDA | yes | yes | yes | disabled | `PASS_SMOKE_RUN` | 0 | 150.01s |
| restore/KL + behavior prior + bridge | A100/CUDA | yes | yes | yes | enabled | `PASS_SMOKE_RUN` | 0 | 480.03s |

## Evidence

Baseline diagnostic:

- artifact: `outputs/analysis/colab_cli/open-duck-a100-startup-training-smoke-diagnostic-20260702T023805Z/open_duck_colab_cli_training-smoke-diagnostic_20260702T023813Z_artifacts.tar.gz`
- sha256: `08d2530b5bd3f41705e2b6932012c56d8e7c3f53203238d9a50e0b150ee013aa`
- JAX: `0.7.2`
- jaxlib: `0.7.2`
- backend: CUDA on A100

Stage timings:

| stage | status | elapsed |
|---|---|---:|
| `00_python_jax_device` | `PASS` | 2.47s |
| `01_import_training_stack` | `PASS` | 37.33s |
| `02_smoke_dry_run` | `PASS` | 0.08s |
| `03_smoke_run` | `PASS` | 360.11s |

Feature probes:

| test | artifact | sha256 | reward line |
|---|---|---|---|
| restore/KL | `outputs/analysis/colab_cli/a100_restore_kl_probe_20260702T024631Z/a100_restore_kl_probe_artifacts.tar.gz` | `1f392491704b6a920974e1bb8d0d5aae380fd7a48f9b490c409059200654ff57` | `STEP: 64 reward: 21.338165283203125 reward_std: 8.167276382446289` |
| behavior prior | `outputs/analysis/colab_cli/a100_behavior_prior_probe_20260702T025500Z/a100_behavior_prior_probe_artifacts.tar.gz` | `8cd6a88d9a1aeb37013efdbc509a3f3386ba9575ae7325bf8e20aa0c7a46f503` | `STEP: 64 reward: 10.971935272216797 reward_std: 4.195501327514648` |
| restore/KL + behavior prior | `outputs/analysis/colab_cli/a100_restore_behavior_probe_20260702T030353Z/a100_restore_behavior_probe_artifacts.tar.gz` | `d7b326e2da7e832d65d8a8f1c027911ef1d5fd95d2903024e43f9e0332bf8baf` | `STEP: 64 reward: 21.361108779907227 reward_std: 8.162484169006348` |
| restore/KL + behavior prior + bridge | `outputs/analysis/colab_cli/a100_restore_behavior_bridge_probe_20260702T030645Z/a100_restore_behavior_bridge_probe_artifacts.tar.gz` | `b2aead1e82bffb30600bd6e3f6c0aa7983630325afb62fe6ff0be090740f94d4` | `STEP: 64 reward: 22.062255859375 reward_std: 8.9228515625` |

## Important Limitation

The bridge-enabled startup probe used the smoke-runner bridge defaults:

- delay ticks: `3-8`
- tau: `0.06-0.14s`
- velocity limit range: `2.5-4.7 rad/s`
- per-joint variation: `0.15`

That is good enough to test A100 startup/runtime survival, but it is not the corrected-bridge candidate gate. Candidate promotion still requires the corrected actuator bridge and per-joint corrected-envelope evaluation.

## Interpretation

The current pinned A100 path is usable for the next bounded Phase 2 training probe:

- use `colab exec`, not the flaky detached console path;
- keep JAX/JAXlib pinned at `0.7.2`;
- collect artifacts immediately after each run;
- avoid interpreting startup smoke passes as candidate quality.

The next training-scale probe should increase only one axis at a time from the passing startup shape: either env count/timesteps or corrected bridge strictness, not both at once.

## Safe Point

After the matrix:

- the A100 session was idle;
- all probe artifacts were downloaded locally;
- no robot, SSH, deploy, grounded replay, or runtime change occurred.

## Gate

`PASS_A100_STARTUP_MATRIX`

Phase 2 remains active. This result restores confidence in the cloud GPU execution path, but does not produce a deployable policy.
