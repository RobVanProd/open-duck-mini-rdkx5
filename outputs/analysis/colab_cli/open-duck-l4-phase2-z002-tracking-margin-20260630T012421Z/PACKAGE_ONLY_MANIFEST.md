# Colab Package-Only Manifest

status: `PASS_COLAB_PACKAGE_ONLY_READY`
workflow: `phase2-z002-tracking-margin`
session: `open-duck-l4`

This local check built the upload archives only. It did not upload, train, SSH, deploy, or touch the robot.

## Archives

| archive | size bytes | sha256 | path |
|---|---:|---|---|
| `rdk` | 36389512 | `a808d2af55cf60ef4224791e2dab46caffb443c32b073c8c7d8e129727e04079` | `/home/lsd/robots/outputs/colab_cli_uploads/open-duck-mini-rdkx5_cli_20260630T012421Z.tar.gz` |
| `playground` | 1940410 | `55a80acb03da9aadfd26b8e8214b1269a668ab5bb54adce808fa9f16b4644f43` | `/home/lsd/robots/outputs/colab_cli_uploads/Open_Duck_Playground_cli_20260630T012421Z.tar.gz` |

## Source

- `rdk`: branch `codex/live-oracle-dagger-phase-student`, head `11c9e23114e5e88c2fd9f7dbe05dc6a895790377`, tracked_dirty `False`, untracked_count `52`
- `playground`: branch `codex/forward-progress-reward`, head `d969ca8c3760451a39657161cb376c44c5155a6d`, tracked_dirty `False`, untracked_count `0`
- `jax_pin`: `0.7.2`

## Required RDK Package Paths

- `outputs/analysis/actuator_response_fit_corrected_knee.json`
- `outputs/analysis/phase2_z002_tracking_margin_next_recipe.json`
- `tools/run_actuator_bridge_training_smoke.py`
- `tools/report_phase2_z002_tracking_margin_post_training_gates.py`
- `outputs/phase2_domain_randomization/stage_c0_terrain_z002_preserve_from_a2_gpu/smoke_20260628T103743Z_gpu/2026_06_28_064431_245760`
