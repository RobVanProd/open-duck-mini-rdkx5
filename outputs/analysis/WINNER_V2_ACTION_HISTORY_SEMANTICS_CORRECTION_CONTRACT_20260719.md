# Winner-v2 Action-History Semantics Correction Contract

Status: `PASS_WINNER_V2_ACTION_HISTORY_SEMANTICS_CORRECTED`

| field | corrected control-tick source |
|---|---|
| `obs[41:55]` | final action `t-2` |
| `obs[55:69]` | final action `t-3` |
| `obs[69:83]` | final action `t-4` |
| `previous_action[t]` | final action `t-1` |

Replacement manifest SHA-256: `d771d188218152c782c7d688440e2dd2083b47fd9b883749123f89226c6827c5`.
Selected original ONNX SHA-256: `99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de`.

## Checks

- `preregistration_status_exact`: `PASS`
- `preidentity_source_commit_exact`: `PASS`
- `all_unchanged_package_identities_exact`: `PASS`
- `all_unchanged_external_identities_exact`: `PASS`
- `selected_onnx_byte_identity_exact`: `PASS`
- `package_schema_corrected_to_v1_1`: `PASS`
- `selected_checkpoint_metadata_exact`: `PASS`
- `observation_slice_metadata_exact`: `PASS`
- `readme_history_table_corrected`: `PASS`
- `manifest_hashes_and_sizes_self_consistent`: `PASS`
- `cpu_package_smoke_passes`: `PASS`
- `all_2400_obs_history_ticks_exact`: `PASS`
- `all_2400_previous_action_ticks_exact`: `PASS`
- `zero_behavior_or_simulator_ticks_executed_by_correction`: `PASS`

This is a metadata/hash-chain correction only. It executes no simulator or
behavior ticks and changes no policy, golden trace, P30 fit, reference table,
selection rule, robot authority, Gate 5, COM result, or hardware state.
