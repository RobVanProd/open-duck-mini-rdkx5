# Phase 2 Stage Guard

status: `PASS_PHASE2_COLAB_GPU_SESSION_READY`
current_stage: `stage_z005_support`
current_gate_status: `HOLD_PHASE2_STAGE_Z005_SUPPORT`
next_recipe_status: `PASS_Z005_SUPPORT_RECIPE_READY`
launch_status: `PASS_PHASE2_COLAB_GPU_SESSION_READY`

This is a read-only guard. It did not train, SSH, deploy, or touch the robot.

## Readiness

- colab_status: `PASS_COLAB_SESSION_VISIBLE`
- colab_hardware: `T4`
- git_status: `HOLD_GIT_REMOTE_AUTH_UNAVAILABLE`
- package_preflight: `PASS_PACKAGE_PREFLIGHT`
- package_manifest_status: `PASS_PHASE2_COLAB_PACKAGE_MANIFEST_READY`
- held_gates: `z005_x000_nopush, z005_x008_nopush`
- missing_gates: `none`

## Allowed Now

- Review committed Phase 2 analysis artifacts and guard reports.
- Run read-only report tools: report_phase2_curriculum_gate.py, report_phase2_artifact_manifest.py, and report_phase2_stage_guard.py.
- Run the phase2-z005-support Colab workflow in plan-only mode to verify the package preflight and generated remote driver.
- Run the phase2-z005-support Colab workflow with --package-only to build and hash local upload archives without contacting Colab.
- Prepare or reconnect a Colab GPU session named open-duck-l4; A100/L4 is preferred, T4 is acceptable but slower.
- Run the phase2-z005-support recipe only after the Colab session is active and still using the corrected bridge.
- Run report_phase2_z005_post_training_gates.py on post-training seed-gate output.
- Launch the preferred phase2-z005-support Colab workflow.

## Forbidden

- No robot validation.
- No SSH.
- No deploy.
- No grounded replay.
- No direct BEST_WALK deployment.
- No training from scratch; continue only from the Phase 2 warm-start checkpoint.
- No old/asymmetric actuator bridge.
- No z=0.005 push stage until both z=0.005 no-push gates pass.
- No stronger terrain until z=0.005 support passes and z=0.002 regression stays clear.
- No promotion without PASS_PHASE2_Z005_POST_TRAINING_GATES.

## Required Evidence To Advance

- z=0.005 x=0.08 no-push: 8/8 duration complete, zero falls, no velocity excess, tracking p95 <= 0.20, track ratio >= 0.40.
- z=0.005 x=0.0 no-push: 8/8 duration complete, zero falls, no velocity excess, |mean vx| <= 0.005.
- z=0.002 x=0.08/x=0.0 no-push regression gates remain passing.
- z=0.002 x=0.08/x=0.0 gentle-push regression gates remain passing.
- Post-training decision artifact reports PASS_PHASE2_Z005_POST_TRAINING_GATES.

## Package Preflight

| path | exists | included by tar filter |
|---|---|---|
| `outputs/analysis/actuator_response_fit_corrected_knee.json` | `True` | `True` |
| `outputs/analysis/phase2_z005_support_next_recipe.json` | `True` | `True` |
| `outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520` | `True` | `True` |
| `tools/report_phase2_z005_post_training_gates.py` | `True` | `True` |
| `tools/run_actuator_bridge_training_smoke.py` | `True` | `True` |

## Preferred Command

```bash
python3 \
    tools/run_colab_cli_cuda_workflow.py \
    --workflow \
    phase2-z005-support \
    --session \
    open-duck-l4 \
    --candidate-name \
    phase2_z005_support_baseheight_cuda \
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
- `recipe`: `outputs/analysis/phase2_z005_support_next_recipe.json`
- `manifest`: `outputs/analysis/phase2_artifact_manifest.json`
- `package_manifest`: `outputs/analysis/phase2_colab_package_manifest.json`
