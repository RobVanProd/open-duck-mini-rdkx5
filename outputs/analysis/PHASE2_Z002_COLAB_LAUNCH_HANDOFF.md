# Phase 2 z=0.002 Colab Launch Handoff

status: `HOLD_PHASE2_Z002_COLAB_SESSION_NOT_READY`
workflow: `phase2-z002-tracking-margin`
session: `open-duck-l4`

This is a read-only handoff. It did not upload, train, SSH, deploy, or touch the robot.

## Current Gate

- launch_status: `HOLD_PHASE2_COLAB_GPU_SESSION_NOT_READY`
- colab_status: `HOLD_NO_ACTIVE_COLAB_SESSION`
- git_status: `PASS_GIT_REMOTE_READ_AUTH`
- external_blockers: `HOLD_NO_ACTIVE_COLAB_SESSION`

## Stage Strategy

The curriculum ledger is held at stage_z005_support, but the selected launch workflow intentionally backs up to z=0.002 tracking-margin recovery. The z=0.005 gates failed after the z=0.002 parent lost tracking margin, so the next GPU run must recover and re-gate the z=0.002 parent before escalating terrain again.

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
- current_rdk_head: `7b3144f123606960a8fe36f9747a348b6381fe06`
- package_rdk_head: `11c9e23114e5e88c2fd9f7dbe05dc6a895790377`
- package_source_matches_current_head: `False`

## Notes

- The package-only tarballs are a verified immutable snapshot, but their RDK source head differs from the current branch head. The normal --run command rebuilds and uploads a fresh tarball from the current worktree.

## Package Archives

| archive | size bytes | sha256 | path |
|---|---:|---|---|
| `playground` | 1940410 | `55a80acb03da9aadfd26b8e8214b1269a668ab5bb54adce808fa9f16b4644f43` | `/home/lsd/robots/outputs/colab_cli_uploads/Open_Duck_Playground_cli_20260630T012421Z.tar.gz` |
| `rdk` | 36389512 | `a808d2af55cf60ef4224791e2dab46caffb443c32b073c8c7d8e129727e04079` | `/home/lsd/robots/outputs/colab_cli_uploads/open-duck-mini-rdkx5_cli_20260630T012421Z.tar.gz` |

## Source

- `rdk`: branch `codex/live-oracle-dagger-phase-student`, head `11c9e23114e5e88c2fd9f7dbe05dc6a895790377`, tracked_dirty `False`, untracked_count `52`
- `playground`: branch `codex/forward-progress-reward`, head `d969ca8c3760451a39657161cb376c44c5155a6d`, tracked_dirty `False`, untracked_count `0`
- `jax_pin`: `0.7.2`

## Commands To Run When Colab Is Visible

Preflight:

```bash
colab sessions
colab status -s open-duck-l4
python3 tools/report_phase2_package_only_archive_verification.py --package-manifest outputs/analysis/colab_cli/open-duck-l4-phase2-z002-tracking-margin-20260630T012421Z/PACKAGE_ONLY_MANIFEST.json
python3 tools/report_phase2_z002_launch_audit.py --package-manifest outputs/analysis/colab_cli/open-duck-l4-phase2-z002-tracking-margin-20260630T012421Z/PACKAGE_ONLY_MANIFEST.json
```

Launch:

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

## Required RDK Package Paths

- `outputs/analysis/actuator_response_fit_corrected_knee.json`
- `outputs/analysis/phase2_z002_tracking_margin_next_recipe.json`
- `tools/run_actuator_bridge_training_smoke.py`
- `tools/report_phase2_z002_tracking_margin_post_training_gates.py`
- `outputs/phase2_domain_randomization/stage_c0_terrain_z002_preserve_from_a2_gpu/smoke_20260628T103743Z_gpu/2026_06_28_064431_245760`

## Scope

- No robot validation.
- No SSH.
- No deploy.
- No grounded replay.
- No training from scratch.
- Use the corrected actuator bridge only.
