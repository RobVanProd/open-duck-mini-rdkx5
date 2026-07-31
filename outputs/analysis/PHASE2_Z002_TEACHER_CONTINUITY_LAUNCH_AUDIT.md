# Phase 2 z=0.002 Parent-Recovery Launch Audit

status: `PASS_Z002_PARENT_RECOVERY_READY_TO_LAUNCH`
workflow: `phase2-z002-teacher-continuity`

This is a read-only launch audit. It did not train, SSH, deploy, or touch the robot.

## Launch State

- launch_status: `PASS_PHASE2_COLAB_GPU_SESSION_READY`
- colab_status: `PASS_COLAB_SESSION_VISIBLE`
- git_status: `PASS_GIT_REMOTE_READ_AUTH`
- package_manifest: `outputs/analysis/colab_cli/open-duck-l4-phase2-z002-teacher-continuity-20260630T034918Z/PACKAGE_ONLY_MANIFEST.json`
- stage_guard_json: `outputs/analysis/phase2_stage_guard.json`
- artifact_manifest_json: `outputs/analysis/phase2_artifact_manifest.json`
- archive_verification_json: `outputs/analysis/phase2_package_only_archive_verification.json`

## Checks

- `recipe_workflow_matches`: `True`
- `next_run_workflow_matches`: `True`
- `readiness_workflow_matches`: `True`
- `stage_guard_workflow_matches`: `True`
- `stage_guard_post_training_status_matches`: `True`
- `artifact_manifest_stage_matches`: `True`
- `artifact_manifest_promotion_gate_matches`: `True`
- `package_workflow_matches`: `True`
- `required_inputs_exist`: `True`
- `package_only_ready`: `True`
- `package_archives_verified`: `True`
- `package_archive_verification_workflow_matches`: `True`
- `package_archive_verification_manifest_matches`: `True`
- `robot_scope_clean`: `True`

## Required Inputs

| input | exists | kind | path |
|---|---:|---|---|
| `behavior_prior_mlp` | `True` | `file` | `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz` |
| `corrected_bridge` | `True` | `file` | `outputs/analysis/actuator_response_fit_corrected_knee.json` |
| `phase2_candidate` | `True` | `file` | `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx` |
| `recipe` | `True` | `file` | `outputs/analysis/phase2_z002_teacher_continuity_next_recipe.json` |
| `restore_checkpoint` | `True` | `directory` | `outputs/phase2_domain_randomization/stage_c0_terrain_z002_preserve_from_a2_gpu/smoke_20260628T103743Z_gpu/2026_06_28_064431_245760` |

## Recipe Settings

- `workflow`: `phase2-z002-teacher-continuity`
- `terrain_hfield_z_scale`: `0.002`
- `num_timesteps`: `122880`
- `restore_policy_kl_scale`: `7.5`
- `ppo_learning_rate`: `2e-06`
- `target_rate_scale`: `-0.01`
- `command_progress_required_ratio`: `0.55`
- `push_enable`: `False`
- `actuator_bridge_velocity_limit_range_rad_s`: `[2.0, 3.25]`

## Package Archives

| archive | size bytes | sha256 | path |
|---|---:|---|---|
| `playground` | 1940410 | `eae257d576a79dfc0913eaa06748272c5b94fe13bdde247d16d677a341588bc1` | `/home/lsd/robots/outputs/colab_cli_uploads/Open_Duck_Playground_cli_20260630T034918Z.tar.gz` |
| `rdk` | 36398606 | `0bdefd17f6a4da8edd05a50ed050b941a45d8e4da138cf30c06bf4f8903c8908` | `/home/lsd/robots/outputs/colab_cli_uploads/open-duck-mini-rdkx5_cli_20260630T034918Z.tar.gz` |

## Launch Command

```bash
python3 tools/run_colab_cli_cuda_workflow.py --workflow phase2-z002-teacher-continuity --session open-duck-l4 --candidate-name phase2_z002_teacher_continuity_cuda --candidate-checkpoint-sweep --candidate-checkpoint-sweep-commands 0.0,0.08 --candidate-checkpoint-sweep-duration 1.0 --candidate-checkpoint-sweep-jax-platform cpu --candidate-timeout-s 10800 --run
```
