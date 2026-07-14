# Ground-Up Robustness R2 Evaluator Contract

status: `PASS_ROBUSTNESS_R2_EVALUATOR_CONTRACT`

- preregistration_status_valid: `True`
- exact_20_conditions_320_max_cells: `True`
- all_policy_hashes_exact: `True`
- all_conditions_one_axis_only: `True`
- all_only_intended_model_fields_changed: `True`
- all_readbacks_finite: `True`
- default_off_model_exact: `True`
- default_off_600_tick_behavior_exact: `True`
- joint_offset_reaches_home_support_reset: `True`
- torso_body_name_id_and_mass_exact: `True`
- torso_com_smoke_changes_dynamics: `True`
- cpu_only: `True`

Passing authorizes only the preregistered sequential R2 CPU behavior matrix, stopping at the first failed condition.
No R3+, training, Colab, RDK-X5, or robot access is authorized.
