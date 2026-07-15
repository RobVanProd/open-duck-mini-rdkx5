# Ground-Up Torso-COM Reset-Estimator GPU Expansion Diagnostic Result — 2026-07-15

## Raw result

The wall-only diagnostic recovered the frozen expansion report and stopped
before PPO. Named cleanup passed after 107.753129 seconds and no session
remains. Compute-unit consumption is `UNMEASURED`.

The report contains exactly three z cells. Actor maximum absolute error is
`1.1920928955078125e-07` for z=-1/0/+1; critic error is zero for all three.
Every expansion check except `step_zero_outputs_exact` passes, including zero
inserted rows, bit-exact other values, bit-exact save/restore, exact reference
tail, and finiteness. Maximum other/save error is zero.

The launcher's raw classification is `INVALID_OR_STRUCTURAL_GPU_EXPANSION`
because its validity implementation required source-directory hash
`b37a...b44a` and device text containing `CudaDevice`. The report instead has
source hash `05c0...920e` and device `cuda:0`.

## Method anomaly

Direct CPU extraction of the exact archive with the frozen directory-hash
function yields `05c0c08468f02b96d7e4316fdae6527c6ee223fba507ce3f6a3221b2561a920e`,
exactly matching the T4 report. The session status independently proves the
fresh named hardware was T4/GPU. Thus both invalidating predicates appear to be
classifier-method defects, not evidence of source or device mismatch.

Do not silently overwrite the raw classification. A separately preregistered
CPU-only validity correction must verify the exact archive/report/launch
evidence and then apply the already-frozen result classes without changing
1e-7.

Raw hashes: plan `380fda02...6464bd4`, report `e68e7759...7d9fb97`, launch
record `4f8870b8...8a00bfc`. Training processes/steps and behavior evaluation
remain zero.
