# Phase 2 z=0.002 Teacher-Continuity Colab Launch Handoff

status: `PASS_PHASE2_Z002_COLAB_HANDOFF_READY_TO_RUN`
workflow: `phase2-z002-teacher-continuity`
session: `open-duck-l4`

This is a read-only handoff. It did not upload, train, SSH, deploy, or touch the robot.

## Current Gate

- launch_status: `PASS_PHASE2_COLAB_GPU_SESSION_READY`
- colab_status: `PASS_COLAB_SESSION_VISIBLE`
- git_status: `PASS_GIT_REMOTE_READ_AUTH`
- external_blockers: `none`

## Stage Strategy

The curriculum ledger is held at stage_z005_support, but the selected launch workflow intentionally backs up to z=0.002 teacher-action continuity. The scalar z=0.002 tracking-margin A100 run preserved motion but held at about 0.216-0.218 rad tracking p95, so the next GPU run must recover tracking margin using a behavior-prior/trust-region mechanism before escalating terrain.

## Preflight

- `package_manifest_ready`: `True`
- `archive_verification_pass`: `True`
- `archive_verification_matches_package`: `True`
- `launch_audit_internal_checks_pass`: `True`
- `launch_command_present`: `True`
- `stage_guard_workflow_matches`: `True`
- `robot_scope_clean`: `True`

## Source Snapshot

- current_rdk_branch: `codex/live-oracle-dagger-phase-student`
- current_rdk_head: `665703f018d4b3322812cf288fa3a55e7f1415b3`
- package_rdk_head: `665703f018d4b3322812cf288fa3a55e7f1415b3`
- package_source_matches_current_head: `True`

## Package Archives

| archive | size bytes | sha256 | path |
|---|---:|---|---|
| `playground` | 1940410 | `eae257d576a79dfc0913eaa06748272c5b94fe13bdde247d16d677a341588bc1` | `/home/lsd/robots/outputs/colab_cli_uploads/Open_Duck_Playground_cli_20260630T034918Z.tar.gz` |
| `rdk` | 36398606 | `0bdefd17f6a4da8edd05a50ed050b941a45d8e4da138cf30c06bf4f8903c8908` | `/home/lsd/robots/outputs/colab_cli_uploads/open-duck-mini-rdkx5_cli_20260630T034918Z.tar.gz` |

## Source

- `rdk`: branch `codex/live-oracle-dagger-phase-student`, head `665703f018d4b3322812cf288fa3a55e7f1415b3`, tracked_dirty `True`, untracked_count `54`
- `playground`: branch `codex/forward-progress-reward`, head `d969ca8c3760451a39657161cb376c44c5155a6d`, tracked_dirty `False`, untracked_count `0`
- `jax_pin`: `0.7.2`

## Commands To Run When Colab Is Visible

Preflight:

```bash
colab sessions
colab status -s open-duck-l4
python3 tools/report_phase2_package_only_archive_verification.py --package-manifest outputs/analysis/colab_cli/open-duck-l4-phase2-z002-teacher-continuity-20260630T034918Z/PACKAGE_ONLY_MANIFEST.json
python3 tools/report_phase2_z002_launch_audit.py --package-manifest outputs/analysis/colab_cli/open-duck-l4-phase2-z002-teacher-continuity-20260630T034918Z/PACKAGE_ONLY_MANIFEST.json
```

Launch:

```bash
python3 \
  tools/run_colab_cli_cuda_workflow.py \
  --workflow \
  phase2-z002-teacher-continuity \
  --session \
  open-duck-l4 \
  --candidate-name \
  phase2_z002_teacher_continuity_cuda \
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

## Required RDK Package Paths

- `outputs/analysis/actuator_response_fit_corrected_knee.json`
- `outputs/analysis/phase2_z002_teacher_continuity_next_recipe.json`
- `tools/run_actuator_bridge_training_smoke.py`
- `tools/report_phase2_z002_tracking_margin_post_training_gates.py`
- `outputs/phase2_domain_randomization/stage_c0_terrain_z002_preserve_from_a2_gpu/smoke_20260628T103743Z_gpu/2026_06_28_064431_245760`
- `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz`

## Scope

- No robot validation.
- No SSH.
- No deploy.
- No grounded replay.
- No training from scratch.
- Use the corrected actuator bridge only.
