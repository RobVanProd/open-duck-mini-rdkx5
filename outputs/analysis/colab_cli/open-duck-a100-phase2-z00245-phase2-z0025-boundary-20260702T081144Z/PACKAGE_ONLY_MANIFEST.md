# Colab Package-Only Manifest

status: `PASS_COLAB_PACKAGE_ONLY_READY`
workflow: `phase2-z0025-boundary`
session: `open-duck-a100-phase2-z00245`

This local check built the upload archives only. It did not upload, train, SSH, deploy, or touch the robot.

## Archives

| archive | size bytes | sha256 | path |
|---|---:|---|---|
| `rdk` | 42000983 | `b0aedf08d137566331c5ba8d5776033c93cd06f511142e1e221d4a3d32893d78` | `/home/lsd/robots/outputs/colab_cli_uploads/open-duck-mini-rdkx5_cli_20260702T081144Z.tar.gz` |
| `playground` | 1943634 | `565de8320c0e85e8d522204a15dc609bedccc6db56b5318444c5c997fddb5356` | `/home/lsd/robots/outputs/colab_cli_uploads/Open_Duck_Playground_cli_20260702T081144Z.tar.gz` |

## Source

- `rdk`: branch `codex/live-oracle-dagger-phase-student`, head `d3db38e1c23cc1f5e423073f8b9af0a8dc584b5e`, tracked_dirty `False`, untracked_count `50`
- `playground`: branch `codex/forward-progress-reward`, head `f2294eb514ef31f9ef3cf16fee7ca66d1fce2564`, tracked_dirty `False`, untracked_count `5`
- `jax_pin`: `0.7.2`

## Required RDK Package Paths

- `outputs/analysis/actuator_response_fit_corrected_knee.json`
- `outputs/analysis/phase2_z0025_boundary_next_recipe.json`
- `tools/run_actuator_bridge_training_smoke.py`
- `tools/report_phase2_z005_post_training_gates.py`
- `outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520`
