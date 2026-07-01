# Phase 2 Artifact Manifest

status: `PASS_PHASE2_ARTIFACT_MANIFEST_READY`
stage: `stage_z002_teacher_continuity`
current_gate_status: `HOLD_PHASE2_STAGE_Z005_SUPPORT`
next_recipe_status: `PASS_Z002_TEACHER_CONTINUITY_RECIPE_READY`

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
| `restore_checkpoint` | `PRESENT_DIR` | `e3ace5aee3b128d3caecd91bead371a5215ea6dc472ab056f942a35486fbe439` | 11 | `outputs/phase2_domain_randomization/stage_c0_terrain_z002_preserve_from_a2_gpu/smoke_20260628T103743Z_gpu/2026_06_28_064431_245760` |

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
| `docs/PHASE2_DOMAIN_RANDOMIZATION_ROBUSTNESS.md` | `PRESENT_FILE` | `7c28e7441cce1a699c19559fbd6f0f5a1bdbbeb1025ab3a7556795ffad947215` | 79995 | `docs/PHASE2_DOMAIN_RANDOMIZATION_ROBUSTNESS.md` |
| `docs/TRAINING_ENV_7900XTX.md` | `PRESENT_FILE` | `1f98919b1d48a16fa9cba74ddf431dc60f56df6ff6d26f99c44709db06f7a326` | 15299 | `docs/TRAINING_ENV_7900XTX.md` |
| `outputs/analysis/PHASE2_CURRENT_STATUS.md` | `PRESENT_FILE` | `b91f778ed9f6d1df04785138294b128613caf56118fa5149a16fc54ac0e7fa77` | 4562 | `outputs/analysis/PHASE2_CURRENT_STATUS.md` |
| `outputs/analysis/phase2_current_status.json` | `PRESENT_FILE` | `a5fad7693f50aaa8c6546bfc37561751158b72c963b23a1aea936b9938874b32` | 16200 | `outputs/analysis/phase2_current_status.json` |
| `outputs/analysis/PHASE2_CURRICULUM_GATE_LEDGER.md` | `PRESENT_FILE` | `92b91febeec25962414f5e3c2db28b1223ff4f8597793c60bddb098175c6d29d` | 2106 | `outputs/analysis/PHASE2_CURRICULUM_GATE_LEDGER.md` |
| `outputs/analysis/phase2_curriculum_gate_ledger.json` | `PRESENT_FILE` | `0989eacf3c76201147b86d5500924b4e0443f0dd7badad193db8586def365ccb` | 9469 | `outputs/analysis/phase2_curriculum_gate_ledger.json` |
| `outputs/analysis/PHASE2_Z005_SEED5_FAILURE_DIAGNOSTIC.md` | `PRESENT_FILE` | `13154bd2d7a1e241dd58eb34d9ccb95d44239487841a75d6666bd63b46e5fa24` | 1839 | `outputs/analysis/PHASE2_Z005_SEED5_FAILURE_DIAGNOSTIC.md` |
| `outputs/analysis/phase2_z005_seed5_failure_diagnostic.json` | `PRESENT_FILE` | `25223d5907190c5ea5f884053e3b02f080c7c0a7a35c8ac808c08ce26245a3da` | 3703 | `outputs/analysis/phase2_z005_seed5_failure_diagnostic.json` |
| `outputs/analysis/PHASE2_Z005_SUPPORT_NEXT_RECIPE.md` | `PRESENT_FILE` | `296624608b0d3a28e5c222114bf795cdb7f1eefd44a7452ac4c3823f12884f72` | 10143 | `outputs/analysis/PHASE2_Z005_SUPPORT_NEXT_RECIPE.md` |
| `outputs/analysis/phase2_z005_support_next_recipe.json` | `PRESENT_FILE` | `dd5e77a2bd447a287377b802f9ae2a01b97f11cd0020eb54ca9cb9ab02a79465` | 20500 | `outputs/analysis/phase2_z005_support_next_recipe.json` |
| `outputs/analysis/PHASE2_Z005_MOTION_FLOOR_NEXT_RECIPE.md` | `PRESENT_FILE` | `cdc6d56f490362bc2949180655fe7139bc3b7e33fd5769890cd9ec33e3449586` | 7010 | `outputs/analysis/PHASE2_Z005_MOTION_FLOOR_NEXT_RECIPE.md` |
| `outputs/analysis/phase2_z005_motion_floor_next_recipe.json` | `PRESENT_FILE` | `4342d4fc817db8b07fe8c8b09bb6da5a2f409bfb594545b63238eb9473c78ac8` | 14001 | `outputs/analysis/phase2_z005_motion_floor_next_recipe.json` |
| `outputs/analysis/PHASE2_Z002_TRACKING_MARGIN_NEXT_RECIPE.md` | `PRESENT_FILE` | `6995050d5c156882df5f65925dfae633948b859460fcca802701b16d81560520` | 3379 | `outputs/analysis/PHASE2_Z002_TRACKING_MARGIN_NEXT_RECIPE.md` |
| `outputs/analysis/phase2_z002_tracking_margin_next_recipe.json` | `PRESENT_FILE` | `036ba3019af67bea0c8baaa6a09a182682f7ded01bdf7473b2f58e1fc953c4f8` | 11873 | `outputs/analysis/phase2_z002_tracking_margin_next_recipe.json` |
| `outputs/analysis/PHASE2_Z002_TRACKING_MARGIN_LAUNCH_AUDIT.md` | `PRESENT_FILE` | `4f405caf45ba088062a06361d49fa33ee36b6a0b983450de9ea5624455018ea0` | 3148 | `outputs/analysis/PHASE2_Z002_TRACKING_MARGIN_LAUNCH_AUDIT.md` |
| `outputs/analysis/phase2_z002_tracking_margin_launch_audit.json` | `PRESENT_FILE` | `fbc7dd1389019307751fcf0cef4ab40a2040861cbded4857c0e67257aa017707` | 4805 | `outputs/analysis/phase2_z002_tracking_margin_launch_audit.json` |
| `outputs/analysis/PHASE2_Z002_COLAB_LAUNCH_HANDOFF.md` | `PRESENT_FILE` | `9d5bc67bbf997ef878266383a3e98b6e55ec9154aee4ba6a8995029d92367378` | 3855 | `outputs/analysis/PHASE2_Z002_COLAB_LAUNCH_HANDOFF.md` |
| `outputs/analysis/phase2_z002_colab_launch_handoff.json` | `PRESENT_FILE` | `b332c5d06be2ae56600aea89d7469dbfcc1819d777893d568d58ecf02980d784` | 6180 | `outputs/analysis/phase2_z002_colab_launch_handoff.json` |
| `outputs/analysis/PHASE2_Z002_TEACHER_CONTINUITY_NEXT_RECIPE.md` | `PRESENT_FILE` | `e1c3e541eec9bd5fcb25b305d886c667ee0e61826bba8515535dfa4ffcdb3021` | 3940 | `outputs/analysis/PHASE2_Z002_TEACHER_CONTINUITY_NEXT_RECIPE.md` |
| `outputs/analysis/phase2_z002_teacher_continuity_next_recipe.json` | `PRESENT_FILE` | `ddb49445252b429ef9787a1f22f1f998018104fc3b0e7683c88e600f5a00fd0b` | 8900 | `outputs/analysis/phase2_z002_teacher_continuity_next_recipe.json` |
| `outputs/analysis/PHASE2_Z002_TEACHER_CONTINUITY_LAUNCH_AUDIT.md` | `PRESENT_FILE` | `543e1f90a1cbc64ddb68f28eb340f89ac757bc73d9088c2f2b3e88bbd9d9b20f` | 3327 | `outputs/analysis/PHASE2_Z002_TEACHER_CONTINUITY_LAUNCH_AUDIT.md` |
| `outputs/analysis/phase2_z002_teacher_continuity_launch_audit.json` | `PRESENT_FILE` | `fa3294991277dcb76728b5055794373d3ca269b9db4bd5e003821bbc89fd8d16` | 5235 | `outputs/analysis/phase2_z002_teacher_continuity_launch_audit.json` |
| `outputs/analysis/PHASE2_Z002_TEACHER_CONTINUITY_COLAB_LAUNCH_HANDOFF.md` | `PRESENT_FILE` | `c45cf90709a60f45c1b76fa88fc895afb81bf27578938968eb5868aebf1f4cf1` | 3811 | `outputs/analysis/PHASE2_Z002_TEACHER_CONTINUITY_COLAB_LAUNCH_HANDOFF.md` |
| `outputs/analysis/phase2_z002_teacher_continuity_colab_launch_handoff.json` | `PRESENT_FILE` | `0ac188ed13ae495487d241def1eac08629fe9ed0af8852541f3a0ba770b5dbfb` | 6585 | `outputs/analysis/phase2_z002_teacher_continuity_colab_launch_handoff.json` |
| `outputs/analysis/PHASE2_Z002_TEACHER_CONTINUITY_A100_RESULT.md` | `PRESENT_FILE` | `c1d3d3cd6ad57beb08103f9d71a1016573f939784b3168c42e1af0d0ad0d07ab` | 2575 | `outputs/analysis/PHASE2_Z002_TEACHER_CONTINUITY_A100_RESULT.md` |
| `outputs/analysis/phase2_z002_teacher_continuity_a100_result.json` | `PRESENT_FILE` | `549d692ee7cc4d8d67b601e6bdc3b3a8c5d0fdbabd9d65b5db48a247d504d4fe` | 2871 | `outputs/analysis/phase2_z002_teacher_continuity_a100_result.json` |
| `outputs/analysis/phase2_z002_teacher_continuity_local_compact_sweep/CANDIDATE_CHECKPOINT_SWEEP.md` | `PRESENT_FILE` | `31341a0ad403cc3d6e7bc027b9282e1996a7b2ecfa6380069ad7f41a6744092b` | 3670 | `outputs/analysis/phase2_z002_teacher_continuity_local_compact_sweep/CANDIDATE_CHECKPOINT_SWEEP.md` |
| `outputs/analysis/phase2_z002_teacher_continuity_local_compact_sweep/candidate_checkpoint_sweep.json` | `PRESENT_FILE` | `72cd83e5385c005005f1911477cd30bfd712479d7835f54d26873b41d5923d0e` | 29335 | `outputs/analysis/phase2_z002_teacher_continuity_local_compact_sweep/candidate_checkpoint_sweep.json` |
| `outputs/analysis/PHASE2_PACKAGE_ONLY_ARCHIVE_VERIFICATION.md` | `PRESENT_FILE` | `721c4f1f7c356aeb329678db97bd656a8c538d579e8b8ae2ac3b6ddcf5e1a583` | 1746 | `outputs/analysis/PHASE2_PACKAGE_ONLY_ARCHIVE_VERIFICATION.md` |
| `outputs/analysis/phase2_package_only_archive_verification.json` | `PRESENT_FILE` | `79c74748ef7e9e5b3f311b81ceb94b4ef33a49236ab23cede1ac59e4b5de3ac0` | 10159 | `outputs/analysis/phase2_package_only_archive_verification.json` |
| `outputs/analysis/PHASE2_LOCAL_FALLBACK_READINESS.md` | `PRESENT_FILE` | `0c63c0894e75810edb5ad59a19b347970c5cf901f5b472678aefea337aee7669` | 2375 | `outputs/analysis/PHASE2_LOCAL_FALLBACK_READINESS.md` |
| `outputs/analysis/phase2_local_fallback_readiness.json` | `PRESENT_FILE` | `61da905854bda8e7dde26727ee44f71c7598e3c1ce05456477813bf160448192` | 35579 | `outputs/analysis/phase2_local_fallback_readiness.json` |
| `outputs/analysis/PHASE2_NEXT_RUN_PLAN.md` | `PRESENT_FILE` | `29dadfa56ab1cfc5a701b71261fc1f384a320eb4f8cb28112d5de6e71ebb4d16` | 6543 | `outputs/analysis/PHASE2_NEXT_RUN_PLAN.md` |
| `outputs/analysis/phase2_next_run_plan.json` | `PRESENT_FILE` | `15f7b9ae17696ea9c1efbc461345e4513578b2c50d9f52a2d105afcc45bd2f01` | 14459 | `outputs/analysis/phase2_next_run_plan.json` |
| `outputs/analysis/PHASE2_STAGE_GUARD.md` | `PRESENT_FILE` | `af0c2f5cf4c680aef3de5a06099740307290e606714adfda83a80123461687fc` | 5172 | `outputs/analysis/PHASE2_STAGE_GUARD.md` |
| `outputs/analysis/phase2_stage_guard.json` | `PRESENT_FILE` | `22e7e22b3cc73fd31915ecbe44ee5ef6fb450101b97cca7dfb12d4afd3d14441` | 6587 | `outputs/analysis/phase2_stage_guard.json` |
| `outputs/analysis/rocm_mjx_isolation_post_bios/ROCM_MJX_RUNTIME_ISOLATION.md` | `PRESENT_FILE` | `d21695c41a633202999e9bd41e5b8fe2ca7a72741ecb2e16fbe8382c405d7fa8` | 25165 | `outputs/analysis/rocm_mjx_isolation_post_bios/ROCM_MJX_RUNTIME_ISOLATION.md` |
| `outputs/analysis/rocm_mjx_isolation_post_bios/rocm_mjx_runtime_isolation.json` | `PRESENT_FILE` | `613ce4f1579e24d578f3846407b0c465fab641c1912e82f0d188f68f5a594bc7` | 321403 | `outputs/analysis/rocm_mjx_isolation_post_bios/rocm_mjx_runtime_isolation.json` |
| `outputs/analysis/PHASE2_COLAB_PACKAGE_MANIFEST.md` | `PRESENT_FILE` | `d580700d06142c00fa94459c6b65a919b5b0690b4bfbad739776df7e3354ed62` | 1500 | `outputs/analysis/PHASE2_COLAB_PACKAGE_MANIFEST.md` |
| `outputs/analysis/phase2_colab_package_manifest.json` | `PRESENT_FILE` | `3703839ac7571fd71b018876a6c80323095e3c896aa6f35f57cd6b21b31ab5d7` | 8590 | `outputs/analysis/phase2_colab_package_manifest.json` |
| `outputs/analysis/PHASE2_COLAB_PACKAGE_ONLY_MANIFEST.md` | `PRESENT_FILE` | `8841e14f1a41b4d26c3f19de37b262267bf2530541107aa6e94fe98d4566d7a1` | 1440 | `outputs/analysis/PHASE2_COLAB_PACKAGE_ONLY_MANIFEST.md` |
| `outputs/analysis/phase2_colab_package_only_manifest.json` | `PRESENT_FILE` | `f4abc631fb2919e4a1c1eb3293e4cd39f93a68d9616d2561a124b6de6a4b4123` | 2444 | `outputs/analysis/phase2_colab_package_only_manifest.json` |
| `outputs/analysis/PHASE2_Z005_T4_RECOVERY_DECISION.md` | `PRESENT_FILE` | `5147719b525994df3cfa0c19e97d2d2dd21dd790e13664e3c3af714eba734a54` | 3834 | `outputs/analysis/PHASE2_Z005_T4_RECOVERY_DECISION.md` |
| `outputs/analysis/phase2_z005_t4_recovery_decision.json` | `PRESENT_FILE` | `8b84d1aad44a9dc37b84077140a539ec10c59bcc43c83c03def56d490bb9a9f7` | 3831 | `outputs/analysis/phase2_z005_t4_recovery_decision.json` |
| `outputs/analysis/PHASE2_Z005_RECOVERY_DAGGER_NEXT_DECISION.md` | `PRESENT_FILE` | `f6798bf4837b9909387068e75e211c7959892118cd7b1a2c59efd4b964292555` | 3736 | `outputs/analysis/PHASE2_Z005_RECOVERY_DAGGER_NEXT_DECISION.md` |
| `outputs/analysis/phase2_z005_recovery_dagger_next_decision.json` | `PRESENT_FILE` | `96e1581266185c2fd3458997e3aeb84278f5210c2e42e65f607fdb4b2ec34dc7` | 2060 | `outputs/analysis/phase2_z005_recovery_dagger_next_decision.json` |
| `outputs/analysis/PHASE2_Z005_RECOVERY_DAGGER_ITER1_SEED5_SHORT_DECISION.md` | `PRESENT_FILE` | `ceb10824e85c4433995238c59f4bce02b3b0208573d454cdf3323b8d812d88da` | 3413 | `outputs/analysis/PHASE2_Z005_RECOVERY_DAGGER_ITER1_SEED5_SHORT_DECISION.md` |
| `outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short_decision.json` | `PRESENT_FILE` | `ca63a37e2326d8a8fa69d020f128d1462dd8f4c41869853fe4f722857ddafcc8` | 2476 | `outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short_decision.json` |
| `outputs/analysis/PHASE2_STAGEA2_GAIN099_SEED5_TERRAIN_BOUNDARY_Z0030_SHORT_DECISION.md` | `PRESENT_FILE` | `35dd8b0b7325cb06e074425a756eab0f6b9469e0b4ce4e5cad1b34acceed849f` | 1985 | `outputs/analysis/PHASE2_STAGEA2_GAIN099_SEED5_TERRAIN_BOUNDARY_Z0030_SHORT_DECISION.md` |
| `outputs/analysis/phase2_stagea2_gain099_seed5_terrain_boundary_z0030_short_decision.json` | `PRESENT_FILE` | `014215ba806058d9c56574ee429100234943b1ddcbe87ae778a6228629ba4f9d` | 1765 | `outputs/analysis/phase2_stagea2_gain099_seed5_terrain_boundary_z0030_short_decision.json` |
| `outputs/analysis/phase2_z005_t4_recovered_latest_local_debug_sweep/CANDIDATE_CHECKPOINT_SWEEP.md` | `PRESENT_FILE` | `f4be4ccb739932393877f05133891f566b039c76dc788b28d141fc75b3aac2db` | 2050 | `outputs/analysis/phase2_z005_t4_recovered_latest_local_debug_sweep/CANDIDATE_CHECKPOINT_SWEEP.md` |
| `outputs/analysis/phase2_z005_t4_recovered_latest_local_debug_sweep/candidate_checkpoint_sweep.json` | `PRESENT_FILE` | `b1d871ac1e43cf70b1ec1e4d8a96057930f2571edd6edb16a8f9447ef82b0359` | 9257 | `outputs/analysis/phase2_z005_t4_recovered_latest_local_debug_sweep/candidate_checkpoint_sweep.json` |
| `tools/plan_phase2_z005_support_recipe.py` | `PRESENT_FILE` | `30d4191a48f58d337a0fc84cde783f277583af3f052722df42c89d5ee9993dbb` | 17157 | `tools/plan_phase2_z005_support_recipe.py` |
| `tools/plan_phase2_z005_motion_floor_recipe.py` | `PRESENT_FILE` | `6e1926cd711ce1d265173a36cdfd19794204004e8c42115798a53c2dc531b344` | 14182 | `tools/plan_phase2_z005_motion_floor_recipe.py` |
| `tools/plan_phase2_z002_tracking_margin_recipe.py` | `PRESENT_FILE` | `771fb9b5a2cd13931da1deb6c472c631f6fa0b3675955df4ac80b5a4b010759a` | 9338 | `tools/plan_phase2_z002_tracking_margin_recipe.py` |
| `tools/plan_phase2_z002_teacher_continuity_recipe.py` | `PRESENT_FILE` | `6652eb4e5b6d7c5a13e4a4e7962ec52643e5941bf2866f07809ced0769cd4027` | 10693 | `tools/plan_phase2_z002_teacher_continuity_recipe.py` |
| `tools/report_phase2_colab_package_manifest.py` | `PRESENT_FILE` | `e84e980a18a66c04054b5903f884d1e0c486ec03ddcb3f6612902982d2671660` | 10168 | `tools/report_phase2_colab_package_manifest.py` |
| `tools/report_phase2_local_fallback_readiness.py` | `PRESENT_FILE` | `e52b0e844c4c63c3bf08b6e794ef1b35ef1218cc9cc38c6d017213c3bb21ec0e` | 15720 | `tools/report_phase2_local_fallback_readiness.py` |
| `tools/report_phase2_z005_post_training_gates.py` | `PRESENT_FILE` | `d92207771621144619c7a47e890358b51e757a4709a911b253a4b38e85739b9b` | 11279 | `tools/report_phase2_z005_post_training_gates.py` |
| `tools/report_phase2_z002_tracking_margin_post_training_gates.py` | `PRESENT_FILE` | `370059acc1e136edea358e1ed8bb60ff2d09cdcd8da34fce9e3fa47de7fa0726` | 3444 | `tools/report_phase2_z002_tracking_margin_post_training_gates.py` |
| `tools/report_phase2_z002_launch_audit.py` | `PRESENT_FILE` | `0287794d2c71fce1bf0fea0a2e73343b40f785cc917091f659af8caa19be9be7` | 10574 | `tools/report_phase2_z002_launch_audit.py` |
| `tools/report_phase2_colab_launch_handoff.py` | `PRESENT_FILE` | `d8f53081d676fe254e6828c3cf98b792399e5dc8382b1519062e84dc8a9bf589` | 11188 | `tools/report_phase2_colab_launch_handoff.py` |
| `tools/report_phase2_package_only_archive_verification.py` | `PRESENT_FILE` | `0a2205b238e16dd3851dc4d44e57929caa8a055098d0300c765ad2443051df90` | 9560 | `tools/report_phase2_package_only_archive_verification.py` |
| `tools/report_phase2_stage_guard.py` | `PRESENT_FILE` | `245a4c23bc264de0b4f603aa1ed0f2194cd367749525976d91961795f20033ac` | 19643 | `tools/report_phase2_stage_guard.py` |
| `tools/run_colab_cli_cuda_workflow.py` | `PRESENT_FILE` | `4d0f72b0cb9509d3da03fa16a76324a43efbaf217cbe7e4538ced49f54889a45` | 147011 | `tools/run_colab_cli_cuda_workflow.py` |

## Promotion Gate

- decision_tool: `tools/report_phase2_z002_tracking_margin_post_training_gates.py`
- required_post_training_status: `PASS_PHASE2_Z002_TRACKING_MARGIN_POST_TRAINING_GATES`
- robot_validation_allowed: `False`
