# Phase 2 Package-Only Archive Verification

status: `PASS_PHASE2_PACKAGE_ONLY_ARCHIVE_VERIFICATION`
workflow: `phase2-z002-teacher-continuity`
session: `open-duck-l4`
package_manifest: `outputs/analysis/colab_cli/open-duck-l4-phase2-z002-teacher-continuity-20260630T031335Z/PACKAGE_ONLY_MANIFEST.json`

This is a read-only archive verification. It did not upload, train, SSH, deploy, or touch the robot.

## Archive Hashes

| archive | exists | size matches | sha256 matches | size bytes | sha256 | path |
|---|---:|---:|---:|---:|---|---|
| `rdk` | `True` | `True` | `True` | 36397485 | `d2bca613c23e089cb12b8e5d797f81b86f3b0171326bedf34e75d3c8e3d8a0a7` | `/home/lsd/robots/outputs/colab_cli_uploads/open-duck-mini-rdkx5_cli_20260630T031335Z.tar.gz` |
| `playground` | `True` | `True` | `True` | 1940410 | `97f682a4961da67404fb87faa33f9390be45cc086a6f13841a6441ba985d8a53` | `/home/lsd/robots/outputs/colab_cli_uploads/Open_Duck_Playground_cli_20260630T031335Z.tar.gz` |

## RDK Archive Contents

- status: `PASS_PACKAGE_ONLY_ARCHIVE_VERIFIED`
- member_count: `582`
- missing_entries: `0`
- mismatched_entries: `0`

| required path | expected entries | present entries |
|---|---:|---:|
| `outputs/analysis/actuator_response_fit_corrected_knee.json` | 1 | 1 |
| `outputs/analysis/phase2_z002_teacher_continuity_next_recipe.json` | 1 | 1 |
| `tools/run_actuator_bridge_training_smoke.py` | 1 | 1 |
| `tools/report_phase2_z002_tracking_margin_post_training_gates.py` | 1 | 1 |
| `outputs/phase2_domain_randomization/stage_c0_terrain_z002_preserve_from_a2_gpu/smoke_20260628T103743Z_gpu/2026_06_28_064431_245760` | 11 | 11 |
| `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz` | 1 | 1 |
