# Colab Package-Only Manifest

status: `PASS_COLAB_PACKAGE_ONLY_READY`
workflow: `phase2-z005-support`
session: `open-duck-l4`

This local check built the upload archives only. It did not upload, train, SSH, deploy, or touch the robot.

## Archives

| archive | size bytes | sha256 | path |
|---|---:|---|---|
| `rdk` | 34526423 | `bcfb856599432dd22faa64da09737dec5db061aa2e3f648444993495517f9f98` | `/home/lsd/robots/outputs/colab_cli_uploads/open-duck-mini-rdkx5_cli_20260629T183512Z.tar.gz` |
| `playground` | 1940410 | `e839a60413244667d96b76781b3438c157e64526a85be2a28a7dd0e9008b8c68` | `/home/lsd/robots/outputs/colab_cli_uploads/Open_Duck_Playground_cli_20260629T183512Z.tar.gz` |

## Required RDK Package Paths

- `outputs/analysis/actuator_response_fit_corrected_knee.json`
- `outputs/analysis/phase2_z005_support_next_recipe.json`
- `outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520`
- `tools/report_phase2_z005_post_training_gates.py`
- `tools/run_actuator_bridge_training_smoke.py`
