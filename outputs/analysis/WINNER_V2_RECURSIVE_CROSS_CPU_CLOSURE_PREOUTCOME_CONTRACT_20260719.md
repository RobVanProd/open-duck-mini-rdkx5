# Winner-v2 Recursive Cross-CPU Pre-outcome Contract

Status: `PASS_RECURSIVE_CROSS_CPU_PREOUTCOME_CONTRACT`

Formal runtime result read: `NO`.

Recursive ticks executed: `0`.

The frozen physical-space boundary is half one native STS3215
position count: `0.00076699039394282058 rad`; maximum raw difference is
one count. The existing same-input direct ONNX boundary remains `1e-6`.

## Checks

- `preregistration_status_exact`: `PASS`
- `prior_runtime_report_excluded_from_formal_outcome`: `PASS`
- `package_manifest_exact`: `PASS`
- `selected_onnx_exact`: `PASS`
- `audit_onnx_exact`: `PASS`
- `observer_and_p30_exact`: `PASS`
- `runtime_conversion_sources_exact`: `PASS`
- `soft_offset_snapshot_exact`: `PASS`
- `native_resolution_constants_exact`: `PASS`
- `formal_matrix_exact`: `PASS`
- `history_semantics_exact`: `PASS`
- `all_four_golden_packs_exact_complete_and_finite`: `PASS`
- `selected_and_audit_roles_frozen`: `PASS`
- `formal_runtime_outputs_absent_before_preregistration_commit`: `PASS`
- `authority_remains_offline_only`: `PASS`

The selected 512000 cells are gating; the 1024000 cells are
audit-only. No result may promote the audit sibling, tune a
threshold, change the graph, or expand robot authority.
