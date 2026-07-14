# Ground-Up Torso-COM Package and CPU Smoke

status: `PASS_GROUND_UP_TORSO_COM_PACKAGE_AND_CPU_SMOKE`

- cpu_only: `True`
- preregistration_status_exact: `True`
- randomizer_contract_passed: `True`
- checkpoint_remap_passed: `True`
- all_uploaded_asset_hashes_exact: `True`
- source_archive_and_member_exact: `True`
- fresh_composed_sources_match_contract: `True`
- three_arms_and_stage_schedules_exact: `True`
- all_training_commands_preserve_recipe_and_target_only_com: `True`
- hosted_wall_ceiling_fixed: `True`
- step_zero_exactly_matches_protected_source: `True`
- all_checkpoint_leaves_finite: `True`
- at_least_one_policy_leaf_changed: `True`
- all_actor_leaves_changed: `True`
- step_zero_onnx_interface_exact: `True`
- step_zero_onnx_actions_finite: `True`
- step_zero_onnx_conservative_eight_tick_bound_excess_at_most_1e_6: `True`
- step_zero_onnx_state_output_exact: `True`
- final_onnx_interface_exact: `True`
- final_onnx_actions_finite: `True`
- final_onnx_conservative_eight_tick_bound_excess_at_most_1e_6: `True`
- final_onnx_state_output_exact: `True`
- metrics_present: `True`
- all_metrics_finite: `True`
- contains_step_zero_and_1024: `True`
- tail_metric_finite_nonzero_at_zero_and_1024: `True`
- uniform_com_spread_proven_nonzero: `True`

source-to-step-zero max error: `0.0`
changed actor leaves: `10` / `10`
final conservative bound excess: `2.9802322387695312e-08`

Passing authorizes only the frozen sequential hosted search within its 8-compute-unit ceiling. It does not authorize local GPU, later robustness stages, RDK-X5, or robot access.
