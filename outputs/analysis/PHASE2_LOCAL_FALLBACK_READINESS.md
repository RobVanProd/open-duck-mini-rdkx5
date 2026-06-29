# Phase 2 Local Fallback Readiness

status: `WARN_LOCAL_FALLBACK_DEBUG_ONLY`

This is a read-only diagnostic. It did not train, SSH, deploy, or touch the robot.

## Summary

- preferred_path: `A100/L4 Colab via run_colab_cli_cuda_workflow.py`
- local_role: `fallback/debug evidence only unless it clears the same canonical gates`
- env_python: `/home/lsd/robots/envs/open-duck-playground/bin/python`
- playground_root: `/home/lsd/robots/Open_Duck_Playground`
- pinned_colab_jax_version: `0.7.2`
- local_jax_version: `0.8.2`
- local_jax_backend: `gpu`
- local_jax_devices: `['rocm:0']`
- gpu_visible: `True`
- imports_ok: `True`
- training_smoke_help_ok: `True`
- core_artifacts_ok: `True`

## Warnings

- local JAX is 0.8.2, not pinned Colab/CUDA 0.7.2; treat local runs as fallback/debug unless they clear canonical gates

## Core Artifacts

| artifact | exists | path |
|---|---:|---|
| `phase2_candidate` | `True` | `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx` |
| `corrected_bridge` | `True` | `outputs/analysis/actuator_response_fit_corrected_knee.json` |
| `restore_checkpoint` | `True` | `outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520` |
| `z005_recipe` | `True` | `outputs/analysis/phase2_z005_support_next_recipe.json` |

## Command Checks

- colab_sessions: `[colab] No active sessions found on server.`
- colab_status: `[colab] Session 'open-duck-l4' not found.`
- check_training_env: `Failed to import warp: No module named 'warp' Failed to import mujoco_warp: No module named 'warp' # Training Environment Check overall_status: `WARN_ENV_CHECKS` python: `3.12.13 (main, May 10 2026, 19:30:01) [Clang 22.1.3 ]` platform: `Lin`
- training_smoke_help: `usage: run_actuator_bridge_training_smoke.py [-h] [--playground-path PLAYGROUND_PATH] [--env-python ENV_PYTHON] [--output-root OUTPUT_ROOT] [--run] [--platform {cpu,gpu}] [--jax-platforms JAX_PLATFORMS] [--local-rocm-safe-env] [--xla-flags `

## Decision

Local fallback may be used for debug evidence only. Promotion still requires the canonical gates and version-aware review.
