# Phase 2 Artifact Manifest

status: `PASS_PHASE2_ARTIFACT_MANIFEST_READY`
stage: `stage_z005_support`
current_gate_status: `HOLD_PHASE2_STAGE_Z005_SUPPORT`
next_recipe_status: `PASS_Z005_SUPPORT_RECIPE_READY`

This is a read-only hash manifest. It did not train, SSH, deploy, or touch the robot.

## Git

- `branch`: `codex/live-oracle-dagger-phase-student`
- `upstream`: `origin/codex/live-oracle-dagger-phase-student`
- `note`: `This manifest records stable artifact hashes. It intentionally does not record HEAD, because a committed manifest cannot self-reference its containing commit hash.`

## Core Artifacts

| name | status | sha256 | size/files | path |
|---|---|---|---:|---|
| `candidate` | `PRESENT_FILE` | `209b85a75cf9cbbcf10df573c1b530921943a72e81082111889c15f63a9a2c7b` | 1772930 | `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx` |
| `candidate_metadata` | `PRESENT_FILE` | `c1845de2bc1f72e0da8294fecfa84f6f5609fbc5097ef0b5d569f8aaf72dab79` | 18217 | `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate_metadata.json` |
| `corrected_bridge` | `PRESENT_FILE` | `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0` | 18363 | `outputs/analysis/actuator_response_fit_corrected_knee.json` |
| `restore_checkpoint` | `PRESENT_DIR` | `df4a570a232fd82c2f5eeccb109bf4f5d8b64f95b9a3424aa7f175bc971cbbbc` | 11 | `outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520` |

## Gate Artifacts

| name | status | sha256 | size/files | path |
|---|---|---|---:|---|
| `outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z002_nopush_15s_8seed_cpu.json` | `PRESENT_FILE` | `c4c718ba06e1a6f587ef9d4566fce4f95839f3602ca802eaa083504cf156cefb` | 50380 | `outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z002_nopush_15s_8seed_cpu.json` |
| `outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z002_nopush_15s_8seed_cpu.json` | `PRESENT_FILE` | `13faac86e578cb123b1d50b569004c2c9d45eea43eab7a2d3ad2a789aa5390c9` | 49633 | `outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z002_nopush_15s_8seed_cpu.json` |
| `outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z002_gentle_push_15s_8seed_cpu.json` | `PRESENT_FILE` | `4fe43084cf0ae2bc576b7296c751c99e17980f8a0713f856c24612e5f336349f` | 54016 | `outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z002_gentle_push_15s_8seed_cpu.json` |
| `outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z002_gentle_push_15s_8seed_cpu.json` | `PRESENT_FILE` | `6a3955da2666f9250769e5f2ec81c7b9130ad8d4041f29a2a199164197433bfc` | 53206 | `outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z002_gentle_push_15s_8seed_cpu.json` |
| `outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z005_nopush_15s_8seed_cpu.json` | `PRESENT_FILE` | `c33768ebc257de6b18d65eb273c4a16bbbdcd2f39f5b23c60a46536f9a783271` | 50481 | `outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z005_nopush_15s_8seed_cpu.json` |
| `outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z005_nopush_15s_8seed_cpu.json` | `PRESENT_FILE` | `846402c09c8aa966a774d5d6708114a50add2a0add68f357df6df710599ca604` | 48462 | `outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x0_rough_z005_nopush_15s_8seed_cpu.json` |

## Review Artifacts

| name | status | sha256 | size/files | path |
|---|---|---|---:|---|
| `docs/PHASE2_DOMAIN_RANDOMIZATION_ROBUSTNESS.md` | `PRESENT_FILE` | `404ed69adc28f7b32fb27621bbe3741a9937f212695b459db29e7931e1e26f36` | 76864 | `docs/PHASE2_DOMAIN_RANDOMIZATION_ROBUSTNESS.md` |
| `outputs/analysis/PHASE2_CURRENT_STATUS.md` | `PRESENT_FILE` | `a44971e3d1d1b5728feb4a8a84fcfc3b44047f82bbbaead6714c8df6dc1cbfe0` | 3641 | `outputs/analysis/PHASE2_CURRENT_STATUS.md` |
| `outputs/analysis/phase2_current_status.json` | `PRESENT_FILE` | `70bef0c3ea0d2556177d032e123fbe56af0aa462b3842f087b31cd5f87460bd8` | 14498 | `outputs/analysis/phase2_current_status.json` |
| `outputs/analysis/PHASE2_CURRICULUM_GATE_LEDGER.md` | `PRESENT_FILE` | `92b91febeec25962414f5e3c2db28b1223ff4f8597793c60bddb098175c6d29d` | 2106 | `outputs/analysis/PHASE2_CURRICULUM_GATE_LEDGER.md` |
| `outputs/analysis/phase2_curriculum_gate_ledger.json` | `PRESENT_FILE` | `0989eacf3c76201147b86d5500924b4e0443f0dd7badad193db8586def365ccb` | 9469 | `outputs/analysis/phase2_curriculum_gate_ledger.json` |
| `outputs/analysis/PHASE2_Z005_SEED5_FAILURE_DIAGNOSTIC.md` | `PRESENT_FILE` | `13154bd2d7a1e241dd58eb34d9ccb95d44239487841a75d6666bd63b46e5fa24` | 1839 | `outputs/analysis/PHASE2_Z005_SEED5_FAILURE_DIAGNOSTIC.md` |
| `outputs/analysis/phase2_z005_seed5_failure_diagnostic.json` | `PRESENT_FILE` | `25223d5907190c5ea5f884053e3b02f080c7c0a7a35c8ac808c08ce26245a3da` | 3703 | `outputs/analysis/phase2_z005_seed5_failure_diagnostic.json` |
| `outputs/analysis/PHASE2_Z005_SUPPORT_NEXT_RECIPE.md` | `PRESENT_FILE` | `296624608b0d3a28e5c222114bf795cdb7f1eefd44a7452ac4c3823f12884f72` | 10143 | `outputs/analysis/PHASE2_Z005_SUPPORT_NEXT_RECIPE.md` |
| `outputs/analysis/phase2_z005_support_next_recipe.json` | `PRESENT_FILE` | `dd5e77a2bd447a287377b802f9ae2a01b97f11cd0020eb54ca9cb9ab02a79465` | 20500 | `outputs/analysis/phase2_z005_support_next_recipe.json` |
| `outputs/analysis/PHASE2_NEXT_RUN_PLAN.md` | `PRESENT_FILE` | `1971b999165584f0b21aa7373561c14ab9e5bdd8aca2386e629e25621c64a60d` | 6531 | `outputs/analysis/PHASE2_NEXT_RUN_PLAN.md` |
| `outputs/analysis/phase2_next_run_plan.json` | `PRESENT_FILE` | `971722859fe48c05ef12929f04c48788e47de02cd245c942c6d1cbe861327ba6` | 14051 | `outputs/analysis/phase2_next_run_plan.json` |
| `outputs/analysis/PHASE2_STAGE_GUARD.md` | `PRESENT_FILE` | `b270b010e3fc37a339d21276d57476fff3c6f42ff9e3ecd67c7e2b8107622628` | 3630 | `outputs/analysis/PHASE2_STAGE_GUARD.md` |
| `outputs/analysis/phase2_stage_guard.json` | `PRESENT_FILE` | `7cf0a502856cd1a4c8cbbf15313a7ee55ea935bd15a0c29e48a0cbda236b2a7d` | 5185 | `outputs/analysis/phase2_stage_guard.json` |
| `outputs/analysis/PHASE2_COLAB_PACKAGE_MANIFEST.md` | `PRESENT_FILE` | `bb2f711369c5b02f33d9f06f827917fe11c511eb40433631260cc1e563481882` | 1486 | `outputs/analysis/PHASE2_COLAB_PACKAGE_MANIFEST.md` |
| `outputs/analysis/phase2_colab_package_manifest.json` | `PRESENT_FILE` | `d4049607a47a2334fded31b4a75abb4832e23c463788b1a58d68242036f59bd0` | 8590 | `outputs/analysis/phase2_colab_package_manifest.json` |
| `tools/plan_phase2_z005_support_recipe.py` | `PRESENT_FILE` | `30d4191a48f58d337a0fc84cde783f277583af3f052722df42c89d5ee9993dbb` | 17157 | `tools/plan_phase2_z005_support_recipe.py` |
| `tools/report_phase2_colab_package_manifest.py` | `PRESENT_FILE` | `35cf503ce24824e83566797aa5b05570f97d4b9b04e71f75a99f7e76775544bd` | 10080 | `tools/report_phase2_colab_package_manifest.py` |
| `tools/report_phase2_z005_post_training_gates.py` | `PRESENT_FILE` | `759a838bd3463a2cd1e92d925129b43fdb61dc0ed3f7ed33675739d295f42f6d` | 10476 | `tools/report_phase2_z005_post_training_gates.py` |
| `tools/report_phase2_stage_guard.py` | `PRESENT_FILE` | `731a29e80c07211fbfee6d034ed1c9a8b5c7974fd77d7df2701167104eec8bd5` | 11337 | `tools/report_phase2_stage_guard.py` |
| `tools/run_colab_cli_cuda_workflow.py` | `PRESENT_FILE` | `ffe169f3eb496dc80e35443f4c87424848a09ae6fa8076ff0d271d9777cc657d` | 114515 | `tools/run_colab_cli_cuda_workflow.py` |

## Promotion Gate

- decision_tool: `tools/report_phase2_z005_post_training_gates.py`
- required_post_training_status: `PASS_PHASE2_Z005_POST_TRAINING_GATES`
- robot_validation_allowed: `False`
