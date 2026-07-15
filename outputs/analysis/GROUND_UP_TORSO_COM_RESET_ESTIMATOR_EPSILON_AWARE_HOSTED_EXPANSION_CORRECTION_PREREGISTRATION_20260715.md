# Ground-Up Torso-COM Reset-Estimator Epsilon-Aware Hosted Expansion Correction Preregistration — 2026-07-15

## Evidence and scope

The original hosted expansion failed its `1e-7` raw-output gate with actor
error exactly one float32 epsilon at all three latch values. The corrected GPU
diagnostic proves the result is valid, and the preregistered CPU distribution
audit proves the complete 28-parameter measured error box remains below the
existing `1e-6` action-identity boundary after the exact Brax NormalTanh
transform.

This preregisters one launch-method correction around the frozen original
hosted job. It does not alter checkpoint surgery, checkpoint values, model,
training recipe, seed, arm, steps, export schedule, reward, optimizer,
architecture, command support, COM schedule, or future behavior gate.

## Frozen correction

1. Preserve the original hosted source byte-for-byte at SHA-256
   `a3e5fc38994cecd65d89fdc6b9ede23c2433e917b84583dfcced42c161e79d67`.
   A separate wrapper imports it and replaces only the expansion call boundary.
2. Run the original expansion first and preserve its raw JSON unchanged. The
   wrapper may continue only when:
   - the raw report has exactly the sole failed check
     `step_zero_outputs_exact`;
   - all other raw expansion checks pass;
   - z cells are exactly `[-1,0,+1]`, all six errors are finite, all critic
     errors are zero, and maximum actor error is at most
     `np.finfo(np.float32).eps = 1.1920928955078125e-07`;
   - source directory hash is the independently verified
     `05c0c08468f02b96d7e4316fdae6527c6ee223fba507ce3f6a3221b2561a920e`;
   - the live JAX backend contains a GPU and the report device is `cuda:0`;
   - the committed ULP audit status/decision and hashes are exact.
3. Write a separate corrected expansion report containing the untouched raw
   report, the epsilon-aware checks, exact threshold, and decision
   `PASS_HOSTED_CHECKPOINT_EXPANSION_EPSILON_AWARE`. The wrapper must not set
   the raw `step_zero_outputs_exact` field to true or overwrite the raw failure.
4. Only after that corrected report is durably written may the unchanged
   original job continue to its one frozen `RESET_EST_LATCH_U05` PPO process.
   Any other error fails closed before training.

## Frozen package and launch

A CPU-only, zero-session contract must prove wrapper pass/fail fixtures,
raw-report preservation, exact threshold, exact original job/assets/command,
and that no training boundary is reachable on invalid input.

If that contract passes, one fresh named T4 session is authorized under:

- session `open-duck-reset-estimator-epsilon-t4`;
- one process, no resume/reuse/retry;
- exact original 2,000,000-step command and exports 0/1,003,520/2,007,040;
- hard total session wall ceiling 2,400 seconds and 120-second stop reserve;
- compute usage recorded `UNMEASURED`, with no billing-rate or balance input;
- exact hash-locked uploads, atomic manifest/archive recovery, and mandatory
  named-session cleanup in `finally`;
- training reward remains excluded from selection; behavior is unevaluated.

The user's continuing authorization permits completing this evidence goal
without another billing-number or approval prompt once the contract passes.
The launch is single-use: any allocation, upload, correction, training,
recovery, or cleanup failure closes it without retry and requires a new
preregistration.

## Authority boundary

A recovered artifact authorizes only the already-frozen local CPU behavior
evaluation contract for this arm; it is not a behavior pass or robot clearance.
No local GPU/iGPU, RDK-X5, runtime, robot, deployment, torque, or motor action is
authorized. No training variable or threshold other than this exact expansion-
equivalence method boundary may change.

