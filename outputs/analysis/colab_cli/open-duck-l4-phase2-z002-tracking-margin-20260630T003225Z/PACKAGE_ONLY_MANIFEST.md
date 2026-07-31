# Colab Package-Only Manifest

status: `PASS_COLAB_PACKAGE_ONLY_READY`
workflow: `phase2-z002-tracking-margin`
session: `open-duck-l4`

This local check built the upload archives only. It did not upload, train, SSH, deploy, or touch the robot.

## Archives

| archive | size bytes | sha256 | path |
|---|---:|---|---|
| `rdk` | 36381856 | `683c7adff13fa34841744141ce024a725735a4c8f9c4e7fdac9ca97758268a61` | `/home/lsd/robots/outputs/colab_cli_uploads/open-duck-mini-rdkx5_cli_20260630T003225Z.tar.gz` |
| `playground` | 1940410 | `77d75a3a3c88ca94b86b370b865bc771aa110398838917759c3d189037190ed4` | `/home/lsd/robots/outputs/colab_cli_uploads/Open_Duck_Playground_cli_20260630T003225Z.tar.gz` |

## Required RDK Package Paths

- `outputs/analysis/actuator_response_fit_corrected_knee.json`
- `outputs/analysis/phase2_z002_tracking_margin_next_recipe.json`
- `tools/run_actuator_bridge_training_smoke.py`
- `tools/report_phase2_z002_tracking_margin_post_training_gates.py`
- `outputs/phase2_domain_randomization/stage_c0_terrain_z002_preserve_from_a2_gpu/smoke_20260628T103743Z_gpu/2026_06_28_064431_245760`
