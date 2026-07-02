# Colab Package-Only Manifest

status: `PASS_COLAB_PACKAGE_ONLY_READY`
workflow: `phase2-z0025-boundary`
session: `open-duck-a100-phase2-z00245`

This local check built the upload archives only. It did not upload, train, SSH, deploy, or touch the robot.

## Archives

| archive | size bytes | sha256 | path |
|---|---:|---|---|
| `rdk` | 42003398 | `efacd078280e859f06ef480158c9534406282d7946eea201204af70d99664b33` | `/home/lsd/robots/outputs/colab_cli_uploads/open-duck-mini-rdkx5_cli_20260702T090043Z.tar.gz` |
| `playground` | 1943634 | `3dfbf6a4a420d8e0093b08d2811661f41447dceab2b545f2510e74e5d4aeb5ee` | `/home/lsd/robots/outputs/colab_cli_uploads/Open_Duck_Playground_cli_20260702T090043Z.tar.gz` |

## Source

- `rdk`: branch `codex/live-oracle-dagger-phase-student`, head `995877d03f67f17f2d518188287a0b413e92bbd8`, tracked_dirty `False`, untracked_count `50`
- `playground`: branch `codex/forward-progress-reward`, head `f2294eb514ef31f9ef3cf16fee7ca66d1fce2564`, tracked_dirty `False`, untracked_count `5`
- `jax_pin`: `0.7.2`

## Required RDK Package Paths

- `outputs/analysis/actuator_response_fit_corrected_knee.json`
- `outputs/analysis/phase2_z0025_boundary_next_recipe.json`
- `tools/run_actuator_bridge_training_smoke.py`
- `tools/report_phase2_z005_post_training_gates.py`
- `outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520`
