# Phase 2 Stage Guard

status: `PASS_PHASE2_STAGE_GUARD_READY_FOR_NEXT_ROBUSTNESS_SCREEN`
current_stage: `stage_z005_stronger_push_or_terrain`
current_gate_status: `PASS_PHASE2_CURRICULUM_GATES_READY_TO_ADVANCE`
next_recipe_status: `PASS_Z005_SUPPORT_RECIPE_READY`
launch_status: `HOLD_PHASE2_COLAB_GPU_SESSION_NOT_READY`
preferred_workflow: `phase2-z005-support`

This is a read-only guard. It did not train, SSH, deploy, or touch the robot.

## Stage Strategy

The current promoted parent has cleared z=0.005 no-push and gentle-push support gates plus z=0.0026 regressions. The next work is a one-rung offline robustness screen: stronger z=0.005 push or modestly higher terrain, followed by paired x=0.08/x=0.0 command gates before any training or robot validation.

## Readiness

- colab_status: `HOLD_NO_ACTIVE_COLAB_SESSION`
- colab_hardware: `None`
- git_status: `PASS_GIT_REMOTE_READ_AUTH`
- package_preflight: `PASS_PACKAGE_PREFLIGHT`
- package_manifest_status: `PASS_PHASE2_COLAB_PACKAGE_MANIFEST_READY`
- package_manifest_workflow: `phase2-z005-support`
- package_manifest_matches_workflow: `True`
- local_backend_status: `HOLD_LOCAL_ROCM_GPU_CPU_CORRECTNESS_ONLY`
- local_rocm_gate: `HOLD_PLAYGROUND_GPU_STEP`
- local_rocm_evidence: `outputs/analysis/rocm_mjx_isolation_post_bios/rocm_mjx_runtime_isolation.json`
- post_training_tool: `report_phase2_z005_post_training_gates.py`
- post_training_status: `PASS_PHASE2_Z005_POST_TRAINING_GATES`
- held_gates: `none`
- missing_gates: `none`

## Allowed Now

- Review committed Phase 2 analysis artifacts and guard reports.
- Run read-only report tools: report_phase2_curriculum_gate.py, report_phase2_artifact_manifest.py, and report_phase2_stage_guard.py.
- Run the phase2-z005-support Colab workflow in plan-only mode to verify the package preflight and generated remote driver.
- Run the phase2-z005-support Colab workflow with --package-only to build and hash local upload archives without contacting Colab.
- Prepare or reconnect a Colab GPU session named open-duck-l4; A100/L4 is preferred, T4 is acceptable but slower.
- Run the phase2-z005-support recipe only after the Colab session is active and still using the corrected bridge.
- Run report_phase2_z005_post_training_gates.py on post-training seed-gate output.
- Use local CPU only for reduced-horizon correctness checks; local ROCm GPU is not cleared for Phase 2 training.
- Do not launch training yet from this host; Colab session open-duck-l4 is not active.
- Run a local CPU stronger-push screen from the promoted rate150 parent.
- Run a local CPU modest terrain-escalation screen from the promoted rate150 parent.
- Record a hold if either screen exceeds the corrected actuator envelope, even without falls.

## Forbidden

- No robot validation.
- No SSH.
- No deploy.
- No grounded replay.
- No direct BEST_WALK deployment.
- No training from scratch; continue only from the Phase 2 warm-start checkpoint.
- No old/asymmetric actuator bridge.
- No promotion without PASS_PHASE2_Z005_POST_TRAINING_GATES.
- No robot validation from the rate150 parent just because z=0.005 gentle-push passed.
- No escalation by more than one robustness rung without a paired x=0.08/x=0.0 decision artifact.
- No promotion of stronger-push or stronger-terrain results with any corrected-envelope target-velocity excess.
- No local ROCm Phase 2 training launch while local backend status is HOLD_PLAYGROUND_GPU_STEP.

## Required Evidence To Advance

- Next robustness screen x=0.08: 8/8 duration complete, zero falls, no corrected-envelope velocity excess, tracking p95 <= 0.20, forward motion preserved.
- Companion x=0.0 screen: 8/8 duration complete, zero falls, no corrected-envelope velocity excess, |mean vx| <= 0.005.
- z=0.005 no-push and gentle-push support gates remain passing.
- z=0.0026 no-push and gentle-push regression gates remain passing.
- Decision artifact explicitly records PASS or HOLD before any further escalation.

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
| `outputs/analysis/phase2_z005_support_next_recipe.json` | `True` | `True` |
| `tools/run_actuator_bridge_training_smoke.py` | `True` | `True` |
| `outputs/analysis/phase2_limit198_ppo_loc_warmstart_candidate/candidate_mlp.npz` | `True` | `True` |
| `outputs/analysis/phase2_limit198_ppo_loc_warmstart_candidate/candidate.onnx` | `True` | `True` |
| `outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0.onnx` | `True` | `True` |
| `outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint` | `True` | `True` |
| `tools/report_phase2_z005_post_training_gates.py` | `True` | `True` |

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
    --phase2-restore-checkpoint-path \
    outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint \
    --run
```

## Input Artifacts

- `ledger`: `outputs/analysis/phase2_curriculum_gate_ledger.json`
- `next_plan`: `outputs/analysis/phase2_next_run_plan.json`
- `recipe`: `outputs/analysis/phase2_z005_support_next_recipe.json`
- `manifest`: `outputs/analysis/phase2_artifact_manifest.json`
- `package_manifest`: `outputs/analysis/phase2_colab_package_manifest.json`
- `local_rocm_isolation`: `outputs/analysis/rocm_mjx_isolation_post_bios/rocm_mjx_runtime_isolation.json`
