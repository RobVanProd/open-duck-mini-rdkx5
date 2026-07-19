# Winner-v2 Native-Quantized Eval Contract

status: `PASS_WINNER_V2_NATIVE_QUANTIZED_EVAL_CONTRACT`

Formal behavior cells executed: `0`.

## Checks

- `preregistration_status_exact`: `PASS`
- `all_frozen_hashes_exact`: `PASS`
- `runtime_commit_exists`: `PASS`
- `two_wrappers_present`: `PASS`
- `cpu_provider_only_selected`: `PASS`
- `graph_and_abi_identity`: `PASS`
- `numpy_quantizer_error_at_most_1e7`: `PASS`
- `unchanged_slices_bit_exact`: `PASS`
- `binary_contacts_bit_exact`: `PASS`
- `nonbinary_contact_control_rejected`: `PASS`
- `wrapper_source_semantics_exact`: `PASS`
- `default_off_byte_exact`: `PASS`
- `x0_bit_exact_zero`: `PASS`
- `chained_256_finite_and_stateful`: `PASS`
- `zero_formal_behavior_cells`: `PASS`

## Wrapper readback

| checkpoint | wrapper SHA-256 | prefix nodes | max NumPy error | providers |
|---:|---|---:|---:|---|
| 512000 | `a24b74ffdedd19c818ab5873882d7794c90b5e2349f8d7720175913fad753273` | 21 | 0 | `CPUExecutionProvider` |
| 1024000 | `11c8d5693e020373479e87738146250db0adb2c26f587a423dee6ce98229361a` | 21 | 0 | `CPUExecutionProvider` |

A pass authorizes only the frozen 16-cell CPU behavior matrix. It does not select a checkpoint before those outcomes and does not authorize Gate 5, deployment, RDK-X5/robot access, torque, motors, or robot clearance.
