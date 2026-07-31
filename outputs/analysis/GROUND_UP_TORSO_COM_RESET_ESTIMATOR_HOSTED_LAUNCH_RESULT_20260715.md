# Ground-Up Torso-COM Reset-Estimator Hosted Launch Result — 2026-07-15

## Decision

`STOP_NO_RETRY_STATUS_RATE_UNAVAILABLE`

The one explicitly authorized `RESET_EST_LATCH_U05` launch reached a fresh T4
session, then failed closed at the post-allocation rate check. The
session-specific `colab status` response contained hardware and idle state but
no compute-unit usage-rate line. The frozen launcher therefore could not prove
the projected 2.0-CU ceiling and returned
`FAIL_HOSTED_LAUNCH_OR_RECOVERY`.

This is a launch-method failure, not a training or behavior result. The frozen
no-retry rule applies. Do not rerun, resume, promote, evaluate, or interpret the
arm from this attempt.

## Exact execution evidence

- Explicit approval: received for one hosted `RESET_EST_LATCH_U05` run.
- Session: `open-duck-reset-estimator-t4`, fresh T4, ready.
- Commands completed before the hold: exactly `colab new`, then
  session-specific `colab status`.
- Uploads: zero.
- Training processes: zero.
- PPO steps: zero.
- Recovered policy artifacts: zero.
- Session wall time: 14.394865006 seconds, below 2,400 seconds.
- Cleanup: named `colab stop` returned 0 in 0.842068944 seconds.
- Independent post-cleanup inventory: no active Colab sessions.
- Compute usage: unknown. The required rate was absent, so this result does not
  estimate or invent consumed compute units.

The raw launch plan is
`ground_up_reset_com_estimator_hosted_run_20260715/launch_plan.json`
(SHA-256 `4fc6fcee515bc99b15322248f57f82bdf042de14aac0ca50d971b9589baefa71`).
The raw launch record is
`ground_up_reset_com_estimator_hosted_run_20260715/recovery/GROUND_UP_RESET_COM_ESTIMATOR_TRAINING_launch.json`
(SHA-256 `823c0875b280c1ebce8b9fa0dfb2acf74248e73cef5f4b17572aa92c15d8ed14`).

## Authority boundary

No retry or session reuse is authorized by the hosted-training or launch
preregistrations. A further Colab allocation would require a separately frozen
launch-method correction that establishes a fail-closed CU-bound check from
currently available CLI evidence. It would then require new explicit run
authorization. No training, behavior evaluation, local GPU/iGPU, RDK-X5,
runtime, or robot action follows from this result.
