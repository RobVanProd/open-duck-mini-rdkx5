# Colab Package-Only Manifest

status: `PASS_COLAB_PACKAGE_ONLY_READY`
workflow: `phase2-z0035-motion-floor`
session: `open-duck-l4`

This local check built the upload archives only. It did not upload, train, SSH, deploy, or touch the robot.

## Archives

| archive | size bytes | sha256 | path |
|---|---:|---|---|
| `rdk` | 34539405 | `0cdce2b3fa940441e478ddabd080a577054fbd5027a02d070d8bcd2be42aadf4` | `/home/lsd/robots/outputs/colab_cli_uploads/open-duck-mini-rdkx5_cli_20260629T224636Z.tar.gz` |
| `playground` | 1940410 | `9a2444e690ff064840bb31dfcee31735d2948ecfa6b531a95e1eb1c1361d2a09` | `/home/lsd/robots/outputs/colab_cli_uploads/Open_Duck_Playground_cli_20260629T224636Z.tar.gz` |

## Required RDK Package Paths

- `outputs/analysis/actuator_response_fit_corrected_knee.json`
- `outputs/analysis/phase2_z0035_motion_floor_next_recipe.json`
- `outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520`
- `tools/report_phase2_z005_post_training_gates.py`
- `tools/run_actuator_bridge_training_smoke.py`
