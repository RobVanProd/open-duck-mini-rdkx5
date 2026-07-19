# Winner-v3 Variable-Configuration Evaluation-Policy Transform Contract

status: `PASS_WINNER_V3_VARIABLE_CONFIGURATION_EVAL_POLICY_TRANSFORM_CONTRACT`

Formal behavior cells executed: `0`.

- `replacement_preregistration_exact`: `PASS`
- `training_artifact_check_passed`: `PASS`
- `archive_hash_exact`: `PASS`
- `two_persistent_sources_exact`: `PASS`
- `source_rate_projection_is_exact_conservative_vector`: `PASS`
- `actual_centered_guard_is_selected_g1`: `PASS`
- `deadband_is_exact_prior_contract`: `PASS`
- `all_source_initializers_preserved`: `PASS`
- `all_source_nodes_preserved`: `PASS`
- `all_append_exactly_13_guard_and_5_deadband_nodes`: `PASS`
- `all_external_abis_exact`: `PASS`
- `all_cpu_inference_contracts_pass`: `PASS`
- `formal_behavior_cells_zero`: `PASS`

## Contracted policies

- step `1003520`: `c8e03dd4afed4e7a96507e5089116944a048ac1d682210408a68cca1b8b6af7c` (source `3d5e6dd447601246f8f5789ce370a1d63648334536359f367f0cb856ab77b04d`)
- step `2007040`: `dfdd01bf4563e3d377ffcbe70515681e75a0d87797f3b6b9e4486d1b40ad569c` (source `fb725c5e8f45866c9b96e56b2429774f2e1ce73261ffb33ff534d977195544f0`)

The learned graph and initializers are unchanged. The frozen G1 guard and prior x=0 deadband are appended before any formal behavior outcome. A pass authorizes only the preregistered 1,024-cell CPU evaluation.

No training, retry, accelerator, hosted allocation, RDK-X5, robot, runtime, Gate 5, motion, or deployment is authorized.
