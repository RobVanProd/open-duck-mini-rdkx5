# Ground-Up Torso-COM Reset-Estimator GPU Diagnostic Validity Correction Result — 2026-07-15

## Decision

`PASS_GPU_DIAGNOSTIC_VALIDITY_CORRECTION`

The recovered wall-only diagnostic is valid under the corrected, preregistered
source and device predicates. Its frozen-threshold outcome is
`FINITE_GPU_EQUIVALENCE_EXCEEDS_ORIGINAL_1E7`.

## Evidence

- Direct CPU extraction of the exact protected archive produces source-directory
  SHA-256 `05c0c08468f02b96d7e4316fdae6527c6ee223fba507ce3f6a3221b2561a920e`,
  exactly matching the hosted report.
- The launch record proves the exact named T4/GPU session and the report records
  device `cuda:0`.
- The report marker and hash are exact, cleanup completed inside 300 seconds,
  no training process or PPO step started, and compute usage remains
  `UNMEASURED`.
- Exactly three ordered z cells are present. Actor maximum absolute error is
  `1.1920928955078125e-07` at z=-1/0/+1; critic error is zero in all cells.
- Every structural, inserted-state, reference-tail, finiteness, and save/restore
  check passes. Only `step_zero_outputs_exact` fails.

The maximum error is finite but exceeds the unchanged `1e-7` threshold. The
raw launch classification remains preserved; this result records the corrected
classification separately and does not retroactively relax that threshold.

## Authority boundary

This result selects only `ACTION_DISTRIBUTION_ULP_SENSITIVITY_AUDIT`, a
separately preregistered CPU-only numerical sensitivity study using the measured
error magnitude. It authorizes no tolerance change, training, Colab allocation,
behavior evaluation, local GPU/iGPU, RDK-X5, runtime, or robot action.

