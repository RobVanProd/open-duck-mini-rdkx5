# Phase 2 Stage Guard

status: `HOLD_PHASE2_COLAB_GPU_SESSION_NOT_READY`
current_stage: `stage_z005_support`
current_gate_status: `HOLD_PHASE2_STAGE_Z005_SUPPORT`
next_recipe_status: `PASS_Z002_TRACKING_MARGIN_RECIPE_READY`
launch_status: `HOLD_PHASE2_COLAB_GPU_SESSION_NOT_READY`
preferred_workflow: `phase2-z002-tracking-margin`

This is a read-only guard. It did not train, SSH, deploy, or touch the robot.

## Readiness

- colab_status: `HOLD_NO_ACTIVE_COLAB_SESSION`
- colab_hardware: `None`
- git_status: `HOLD_GIT_REMOTE_AUTH_UNAVAILABLE`
- package_preflight: `PASS_PACKAGE_PREFLIGHT`
- package_manifest_status: `PASS_PHASE2_COLAB_PACKAGE_MANIFEST_READY`
- local_backend_status: `HOLD_LOCAL_ROCM_GPU_CPU_CORRECTNESS_ONLY`
- local_rocm_gate: `HOLD_PLAYGROUND_GPU_STEP`
- local_rocm_evidence: `outputs/analysis/rocm_mjx_isolation_post_bios/rocm_mjx_runtime_isolation.json`
- post_training_tool: `report_phase2_z002_tracking_margin_post_training_gates.py`
- post_training_status: `PASS_PHASE2_Z002_TRACKING_MARGIN_POST_TRAINING_GATES`
- held_gates: `z005_x000_nopush, z005_x008_nopush`
- missing_gates: `none`

## Allowed Now

- Review committed Phase 2 analysis artifacts and guard reports.
- Run read-only report tools: report_phase2_curriculum_gate.py, report_phase2_artifact_manifest.py, and report_phase2_stage_guard.py.
- Run the phase2-z002-tracking-margin Colab workflow in plan-only mode to verify the package preflight and generated remote driver.
- Run the phase2-z002-tracking-margin Colab workflow with --package-only to build and hash local upload archives without contacting Colab.
- Prepare or reconnect a Colab GPU session named open-duck-l4; A100/L4 is preferred, T4 is acceptable but slower.
- Run the phase2-z002-tracking-margin recipe only after the Colab session is active and still using the corrected bridge.
- Run report_phase2_z002_tracking_margin_post_training_gates.py on post-training seed-gate output.
- Use local CPU only for reduced-horizon correctness checks; local ROCm GPU is not cleared for Phase 2 training.
- Do not launch training yet from this host; Colab session open-duck-l4 is not active.

## Forbidden

- No robot validation.
- No SSH.
- No deploy.
- No grounded replay.
- No direct BEST_WALK deployment.
- No training from scratch; continue only from the Phase 2 warm-start checkpoint.
- No old/asymmetric actuator bridge.
- No z=0.005 push stage until the current z=0.002 tracking-margin parent-selection gate passes.
- No stronger terrain until z=0.002 tracking margin is recovered and z=0.002 regression stays clear.
- No promotion without PASS_PHASE2_Z002_TRACKING_MARGIN_POST_TRAINING_GATES.
- No local ROCm Phase 2 training launch while local backend status is HOLD_PLAYGROUND_GPU_STEP.

## Required Evidence To Advance

- z=0.002 x=0.08 no-push: 8/8 duration complete, zero falls, no velocity excess, tracking p95 <= 0.20, track ratio >= 0.25.
- z=0.002 x=0.0 no-push: 8/8 duration complete, zero falls, no velocity excess, |mean vx| <= 0.005.
- z=0.002 x=0.08/x=0.0 no-push regression gates remain passing.
- z=0.002 x=0.08/x=0.0 gentle-push regression gates remain passing.
- Post-training decision artifact reports PASS_PHASE2_Z002_TRACKING_MARGIN_POST_TRAINING_GATES.

## Local Backend

- `launch_class`: `HOLD_LOCAL_ROCM_GPU_CPU_CORRECTNESS_ONLY`
- `gate_result`: `HOLD_PLAYGROUND_GPU_STEP`
- `smallest_failing_subtest`: `default_gpu_playground_direct_mjx_step`
- `smallest_failing_status`: `TIMEOUT`
- `basic_jax_gpu`: `PASS`
- `minimal_mjx_gpu`: `PASS`
- `playground_step_gpu`: `FAIL`
- `closed_loop_gpu`: `FAIL`
- `closed_loop_cpu`: `PASS`
- `path`: `outputs/analysis/rocm_mjx_isolation_post_bios/rocm_mjx_runtime_isolation.json`

## Package Preflight

| path | exists | included by tar filter |
|---|---|---|
| `outputs/analysis/actuator_response_fit_corrected_knee.json` | `True` | `True` |
| `outputs/analysis/phase2_z002_tracking_margin_next_recipe.json` | `True` | `True` |
| `tools/run_actuator_bridge_training_smoke.py` | `True` | `True` |
| `tools/report_phase2_z002_tracking_margin_post_training_gates.py` | `True` | `True` |
| `outputs/phase2_domain_randomization/stage_c0_terrain_z002_preserve_from_a2_gpu/smoke_20260628T103743Z_gpu/2026_06_28_064431_245760` | `True` | `True` |

## Preferred Command

```bash
python3 \
    tools/run_colab_cli_cuda_workflow.py \
    --workflow \
    phase2-z002-tracking-margin \
    --session \
    open-duck-l4 \
    --candidate-name \
    phase2_z002_tracking_margin_cuda \
    --candidate-checkpoint-sweep \
    --candidate-checkpoint-sweep-commands \
    0.0,0.08 \
    --candidate-checkpoint-sweep-duration \
    1.0 \
    --candidate-checkpoint-sweep-jax-platform \
    cpu \
    --candidate-timeout-s \
    10800 \
    --run
```

## Input Artifacts

- `ledger`: `outputs/analysis/phase2_curriculum_gate_ledger.json`
- `next_plan`: `outputs/analysis/phase2_next_run_plan.json`
- `recipe`: `outputs/analysis/phase2_z002_tracking_margin_next_recipe.json`
- `manifest`: `outputs/analysis/phase2_artifact_manifest.json`
- `package_manifest`: `outputs/analysis/phase2_colab_package_manifest.json`
- `local_rocm_isolation`: `outputs/analysis/rocm_mjx_isolation_post_bios/rocm_mjx_runtime_isolation.json`
