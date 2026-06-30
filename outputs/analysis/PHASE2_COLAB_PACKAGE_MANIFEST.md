# Phase 2 Colab Package Manifest

status: `PASS_PHASE2_COLAB_PACKAGE_MANIFEST_READY`
workflow: `phase2-z002-teacher-continuity`

This is a read-only package manifest. It did not train, SSH, deploy, touch the robot, or upload to Colab.

## Required Paths

| path | status | files included | files excluded | size bytes | sha256 |
|---|---|---:|---:|---:|---|
| `outputs/analysis/actuator_response_fit_corrected_knee.json` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 18363 | `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0` |
| `outputs/analysis/phase2_z002_teacher_continuity_next_recipe.json` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 8900 | `ddb49445252b429ef9787a1f22f1f998018104fc3b0e7683c88e600f5a00fd0b` |
| `tools/run_actuator_bridge_training_smoke.py` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 53490 | `4afb2eddcb0c52a71d8192407dd8460971f8e9f4297c7ea5013d9bd82eeecb55` |
| `tools/report_phase2_z002_tracking_margin_post_training_gates.py` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 3444 | `370059acc1e136edea358e1ed8bb60ff2d09cdcd8da34fce9e3fa47de7fa0726` |
| `outputs/phase2_domain_randomization/stage_c0_terrain_z002_preserve_from_a2_gpu/smoke_20260628T103743Z_gpu/2026_06_28_064431_245760` | `PRESENT_DIR_INCLUDED` | 11 | 0 | 1840419 | `fb5a73ee3026e342ea9c639ef2d14a970b0f4027b44a868c0537d6d24c021fd1` |
| `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 876828 | `312f1ef0ba758af5fdeae900ce0a34dab659fe348a9f389988ddaaaa15659497` |

## Tarball Contents

- status: `PASS_TARBALL_CONTENTS`
- member_count: `582`
- missing_archive_entries: `{}`

## Decision

All required `phase2-z002-teacher-continuity` Colab package inputs are present and included by the upload tar filter.
