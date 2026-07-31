# Ground-Up Torso-COM Reset-Estimator Rate-Attestation Correction Contract — 2026-07-15

## Result

`PASS_RESET_COM_ESTIMATOR_RATE_ATTESTATION_LAUNCH_CORRECTION_CONTRACT`

All 20 frozen checks pass with zero Colab allocation, zero remote bytes, zero
training processes, and zero PPO steps. Session inventory remained unchanged
at none.

## What the evidence establishes

- Colab CLI 0.6.0 and installed session-source hash
  `59d50c3f...bbe0c1c` are exact. Its `status` and `sessions` implementations
  expose no compute-rate or balance field.
- The captured failed-launch status line passes the corrected named-session,
  idle-T4, GPU-variant identity gate without being parsed for a rate.
- Wrong session, hardware, variant, state, and extra-line controls all fail.
- Rate, available balance, and timezone-aware observation timestamp are now
  mandatory. The operator-attestation source is recorded exactly as
  `COLAB_RESOURCES_UI_OPERATOR_ATTESTATION`.
- Attestation validation occurs before the only call to `launch()` and thus
  before `session_created = True` or `colab new`.
- Rate 1.07 projects to 0.7133333333333334 units over the frozen 2,400-second
  ceiling. Rate 3.0 passes at exactly 2.0 units; 3.000001 fails.
- Balance 2.0, age 600 seconds, and future skew 60 seconds pass at their exact
  boundaries. Values outside those boundaries fail, as do missing, nonfinite,
  zero, negative, or timezone-naive inputs.
- The dry run stages the same 19 regular hash-exact assets. The hosted job,
  package, checkpoint, commands, T4 identity, 2,400-second wall ceiling,
  2.0-CU ceiling, 120-second stop reserve, cleanup, recovery, and no-resume/
  no-retry rules remain unchanged.

The launcher SHA-256 is
`97f2d45f17ec58958e243568ab3b9fca15ad5a95f67d3fd75092abab948c3abe`.
The contract JSON SHA-256 is
`3d00ca87641f68e8362139c2f0b3690bcffb8cfc6623782966f436301f637ff5`.

## Authority boundary

This contract authorizes no allocation. Before one corrected launch can be
considered, the operator must provide a fresh Colab Resources-UI compute rate,
available compute-unit balance, timezone-aware observation timestamp, and new
explicit approval. The launcher will reject an observation older than 600
seconds, more than 60 seconds in the future, a balance below 2.0 units, or a
rate projecting above 2.0 units.

No training reward, behavior result, policy selection, or robot clearance is
created by this contract. No local GPU/iGPU, RDK-X5, runtime, or robot access is
authorized.
