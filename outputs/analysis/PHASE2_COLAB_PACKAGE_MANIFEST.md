# Phase 2 Colab Package Manifest

status: `PASS_PHASE2_COLAB_PACKAGE_MANIFEST_READY`
workflow: `phase2-z005-support`

This is a read-only package manifest. It did not train, SSH, deploy, touch the robot, or upload to Colab.

## Required Paths

| path | status | files included | files excluded | size bytes | sha256 |
|---|---|---:|---:|---:|---|
| `outputs/analysis/actuator_response_fit_corrected_knee.json` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 18363 | `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0` |
| `outputs/analysis/phase2_z005_support_next_recipe.json` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 20500 | `dd5e77a2bd447a287377b802f9ae2a01b97f11cd0020eb54ca9cb9ab02a79465` |
| `tools/run_actuator_bridge_training_smoke.py` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 63692 | `b8c8575c7e7be28a8d1880edda569309665b0e51c20dc209bd36307371337664` |
| `outputs/analysis/phase2_limit198_ppo_loc_warmstart_candidate/candidate_mlp.npz` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 876828 | `cfb62315014dfc83ef0c654a8386bc39eb0ec9f7305e10adfa10216827ab0d15` |
| `outputs/analysis/phase2_limit198_ppo_loc_warmstart_candidate/candidate.onnx` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 874724 | `a48c82c0f5719016b3e8bfae7817351b5413fac0e1babcf70de05e1f3652c237` |
| `outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0.onnx` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 883946 | `1dc894eebc144d790f1a6b4be6ada5a05e748f215f2053c72610347955deb3bb` |
| `outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint` | `PRESENT_DIR_INCLUDED` | 11 | 0 | 1823760 | `24879568d60b191b69f3bcb278375d56ece2d937ed72ce4a46dc881b285eb57a` |
| `tools/report_phase2_z005_post_training_gates.py` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 11279 | `d92207771621144619c7a47e890358b51e757a4709a911b253a4b38e85739b9b` |
| `outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520` | `PRESENT_DIR_INCLUDED` | 11 | 0 | 1840048 | `b5d985c70a4944d49ff7dd689c75774dd47c026112abc1af8343915d8d027ffa` |

## Tarball Contents

- status: `PASS_TARBALL_CONTENTS`
- member_count: `731`
- missing_archive_entries: `{}`

## Decision

All required `phase2-z005-support` Colab package inputs are present and included by the upload tar filter.
