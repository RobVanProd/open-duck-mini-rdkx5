# Colab Package-Only Manifest

status: `PASS_COLAB_PACKAGE_ONLY_READY`
workflow: `phase2-z002-tracking-margin`
session: `open-duck-l4`

This local check built the upload archives only. It did not upload, train, SSH, deploy, or touch the robot.

## Archives

| archive | size bytes | sha256 | path |
|---|---:|---|---|
| `rdk` | 36386199 | `827d28e58d16caa26cb4bc71fd4c78b80f40971f242d8773fc4d9fa2b7904a25` | `/home/lsd/robots/outputs/colab_cli_uploads/open-duck-mini-rdkx5_cli_20260630T011011Z.tar.gz` |
| `playground` | 1940410 | `32c9a711f1b9322b9da61690ce45180787440ac37172a81404c20ee6159a5812` | `/home/lsd/robots/outputs/colab_cli_uploads/Open_Duck_Playground_cli_20260630T011011Z.tar.gz` |

## Required RDK Package Paths

- `outputs/analysis/actuator_response_fit_corrected_knee.json`
- `outputs/analysis/phase2_z002_tracking_margin_next_recipe.json`
- `tools/run_actuator_bridge_training_smoke.py`
- `tools/report_phase2_z002_tracking_margin_post_training_gates.py`
- `outputs/phase2_domain_randomization/stage_c0_terrain_z002_preserve_from_a2_gpu/smoke_20260628T103743Z_gpu/2026_06_28_064431_245760`
