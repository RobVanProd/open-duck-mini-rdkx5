# Ground-Up Torso-COM Colab Artifact Contract

status: `PASS_TORSO_COM_COLAB_ARTIFACT_CONTRACT`

- cpu_only_local_validation: `True`
- manifest_training_artifact_status_pass: `True`
- archive_sha256_exact: `True`
- archive_bytes_exact: `True`
- archive_members_safe: `True`
- control_commit_exact: `True`
- all_input_hashes_exact: `True`
- hosted_device_contract_exact: `True`
- hosted_wall_ceiling_respected: `True`
- all_arm_stage_exports_exact: `True`
- all_commands_preserve_frozen_recipe: `True`
- curriculum_restore_continuity_exact: `True`
- all_training_logs_nonempty: `True`
- one_event_file_per_stage: `True`
- all_onnx_hashes_match_manifest: `True`
- all_onnx_interfaces_and_bounds_pass: `True`
- behavior_remains_unevaluated: `True`
- training_reward_not_used_for_selection: `True`
- no_local_gpu_rdk_or_robot: `True`

archive SHA-256: `364d889bee76a0dee0e2635f3847a5b63d8d92e37af8aa80070f325a8ecfe592`
archive bytes: `35367830`
hosted seconds: `3272.105431814`
validated ONNX exports: `13`

Passing authorizes only the preregistered local CPU behavior evaluation. It does not make any arm a winner or authorize local GPU, RDK-X5, or robot access.
