# Phase 2 Colab Package Manifest

status: `PASS_PHASE2_COLAB_PACKAGE_MANIFEST_READY`
workflow: `phase2-z005-support`

This is a read-only package manifest. It did not train, SSH, deploy, touch the robot, or upload to Colab.

## Required Paths

| path | status | files included | files excluded | size bytes | sha256 |
|---|---|---:|---:|---:|---|
| `outputs/analysis/actuator_response_fit_corrected_knee.json` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 18363 | `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0` |
| `outputs/analysis/phase2_z005_support_next_recipe.json` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 20500 | `dd5e77a2bd447a287377b802f9ae2a01b97f11cd0020eb54ca9cb9ab02a79465` |
| `outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520` | `PRESENT_DIR_INCLUDED` | 11 | 0 | 1840048 | `b5d985c70a4944d49ff7dd689c75774dd47c026112abc1af8343915d8d027ffa` |
| `tools/report_phase2_z005_post_training_gates.py` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 10476 | `759a838bd3463a2cd1e92d925129b43fdb61dc0ed3f7ed33675739d295f42f6d` |
| `tools/run_actuator_bridge_training_smoke.py` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 53490 | `4afb2eddcb0c52a71d8192407dd8460971f8e9f4297c7ea5013d9bd82eeecb55` |

## Decision

All required z=0.005 Colab package inputs are present and included by the upload tar filter.
