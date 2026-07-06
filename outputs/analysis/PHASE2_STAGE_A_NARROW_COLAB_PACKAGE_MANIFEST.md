# Phase 2 Colab Package Manifest

status: `PASS_PHASE2_COLAB_PACKAGE_MANIFEST_READY`
workflow: `phase2-stage-a-narrow`

This is a read-only package manifest. It did not train, SSH, deploy, touch the robot, or upload to Colab.

## Required Paths

| path | status | files included | files excluded | size bytes | sha256 |
|---|---|---:|---:|---:|---|
| `outputs/analysis/actuator_response_fit_corrected_knee.json` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 18363 | `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0` |
| `outputs/analysis/phase2_domain_randomization_audit.json` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 5463 | `af13933f9e88fdaaadc80baac98b91c906ae5f54150d5653c37df160b33769f9` |
| `tools/run_actuator_bridge_training_smoke.py` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 65725 | `7a812caca8f7664f62134c4a272a23725ece039730b9430137e200c5e5ed6852` |
| `outputs/analysis/phase2_health_routed_parent_phase_mod_rate150_step0.onnx` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 885758 | `5d41eab6945f7e64e5b3d9c15ab38ba388ba38e616fd5c04bbf46f5b9237d626` |
| `outputs/analysis/phase2_health_routed_parent_phase_mod_rate150_step0_checkpoint` | `PRESENT_DIR_INCLUDED` | 11 | 0 | 1633565 | `b4ff62f38c4a5a73561967fafdd2ac4425386df53f8d2e0fc47405a3e7ae62bf` |
| `outputs/analysis/PHASE2_PHASE_CONTEXT_PPO_WARMSTART_DECISION.md` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 2342 | `1da3afcb97a3968f2f0f0c0d6916d0ee415f02534075163ad9e28d9f3dfd67f3` |
| `outputs/analysis/phase2_phase_context_ppo_warmstart_decision.json` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 2934 | `a456dcf069fbbc2b4c9a9bffa96a8f11b3c9006386d6a60525fba468dd0f43d2` |
| `outputs/analysis/PHASE2_DOMAIN_RANDOMIZATION_AUDIT.md` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 3383 | `502badf37500d0a2813b165df3002a6f320218679a92c3fb4b6d7756b10ca7fa` |
| `tools/report_phase2_z005_post_training_gates.py` | `PRESENT_FILE_INCLUDED` | 1 | 0 | 11560 | `c7094456ff616cf9ee7a7f32fdd650a09038b01f6be6e7533475572c9e51e47e` |

## Tarball Contents

- status: `PASS_TARBALL_CONTENTS`
- member_count: `951`
- missing_archive_entries: `{}`

## Decision

All required `phase2-stage-a-narrow` Colab package inputs are present and included by the upload tar filter.
