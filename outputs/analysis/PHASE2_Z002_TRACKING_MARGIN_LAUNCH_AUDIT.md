# Phase 2 z=0.002 Tracking-Margin Launch Audit

status: `HOLD_EXTERNAL_LAUNCH_BLOCKERS`
workflow: `phase2-z002-tracking-margin`

This is a read-only launch audit. It did not train, SSH, deploy, or touch the robot.

## Launch State

- launch_status: `HOLD_PHASE2_COLAB_GPU_SESSION_NOT_READY`
- colab_status: `HOLD_NO_ACTIVE_COLAB_SESSION`
- git_status: `HOLD_GIT_REMOTE_AUTH_UNAVAILABLE`
- package_manifest: `outputs/analysis/colab_cli/open-duck-l4-phase2-z002-tracking-margin-20260630T002205Z/PACKAGE_ONLY_MANIFEST.json`

## Checks

- `recipe_workflow_matches`: `True`
- `next_run_workflow_matches`: `True`
- `readiness_workflow_matches`: `True`
- `package_workflow_matches`: `True`
- `required_inputs_exist`: `True`
- `package_only_ready`: `True`
- `robot_scope_clean`: `True`

## Required Inputs

| input | exists | kind | path |
|---|---:|---|---|
| `corrected_bridge` | `True` | `file` | `outputs/analysis/actuator_response_fit_corrected_knee.json` |
| `phase2_candidate` | `True` | `file` | `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx` |
| `recipe` | `True` | `file` | `outputs/analysis/phase2_z002_tracking_margin_next_recipe.json` |
| `restore_checkpoint` | `True` | `directory` | `outputs/phase2_domain_randomization/stage_c0_terrain_z002_preserve_from_a2_gpu/smoke_20260628T103743Z_gpu/2026_06_28_064431_245760` |

## Recipe Settings

- `workflow`: `phase2-z002-tracking-margin`
- `terrain_hfield_z_scale`: `0.002`
- `num_timesteps`: `122880`
- `restore_policy_kl_scale`: `6.0`
- `ppo_learning_rate`: `2e-06`
- `target_rate_scale`: `-0.02`
- `command_progress_required_ratio`: `0.55`
- `push_enable`: `False`
- `actuator_bridge_velocity_limit_range_rad_s`: `[2.0, 3.25]`

## Package Archives

| archive | size bytes | sha256 | path |
|---|---:|---|---|
| `playground` | 1940410 | `c12462d99ce8bdf3c98307b7ce757b5ab78d249bb76044f89bd3ec7e56d88cbd` | `/home/lsd/robots/outputs/colab_cli_uploads/Open_Duck_Playground_cli_20260630T002205Z.tar.gz` |
| `rdk` | 36378220 | `d6debd4abb66566f10ea0c70bce81df1cb654e41f1f7053dcf09cb754d9439d8` | `/home/lsd/robots/outputs/colab_cli_uploads/open-duck-mini-rdkx5_cli_20260630T002205Z.tar.gz` |

## Launch Command

```bash
python3 tools/run_colab_cli_cuda_workflow.py --workflow phase2-z002-tracking-margin --session open-duck-l4 --candidate-name phase2_z002_tracking_margin_cuda --candidate-checkpoint-sweep --candidate-checkpoint-sweep-commands 0.0,0.08 --candidate-checkpoint-sweep-duration 1.0 --candidate-checkpoint-sweep-jax-platform cpu --candidate-timeout-s 10800 --run
```
