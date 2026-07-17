# Winner-v2 Actuator-Fit Provenance Audit

Status: `SELECT_P30_GAIN_SEMANTICS_CROSSFIT_REQUIRED`

## Evidence

- The native runtime's `start()` writes P=30 to all 14 policy joints and then
  writes P=8 only to the four head joints. The command-line entrypoint exposes
  no gain-override argument. Winner-v2 therefore has P30 body-gain semantics.
- The frozen fixed-target A/B replay used the exact same 747-target sequence
  with policy and IMU feedback disabled. Its P30 phase has no overrides, 747
  samples, and zero read, write or transport-reset errors.
- The alternative phase changed only left hip pitch to P31 and left knee to
  P34. It failed the preregistered gain rule and was explicitly closed as
  `REJECT_P31_34_GAIN_ROUTE`; normal P30 gains were restored afterward.
- Raw A/B telemetry SHA-256 is
  `2233821203a6b799ce472dbc4e043fd89f7543b3dc44823e4b930d45f77414ad`.
  Summary SHA-256 is
  `549cafc4cced4e5aa71112888cb219bb66dc58cd9d9b4b2323bbf83a367700ae`.
- The derived P30 fit SHA-256 is
  `908ddb01e5d82e661d77b8f3cb186a84665695660b86b304c6d1ae89c79cdb0b`;
  the P31/34 fit SHA-256 is
  `a39776c06c5e26425e24b50e7dab3f441823e23904cad4977b8c921d9c9ca276`.

## Decision

P30 is the only evidence-supported gain configuration for winner-v2. P31/34
is retained as a measured dynamics bracket, not a deployment gain candidate.

This does **not** yet prove that a P30 forward observer is safe when the plant
response differs from its fitted P30 model. The missing CPU question is the
cross-fit matrix: evaluate each P30/P31-34 plant fit while independently using
each P30/P31-34 model for the policy's applied-target observation. That matrix
must be frozen before evaluator changes or outcomes.

No new hardware capture is selected unless the P30 observer fails the measured
cross-fit bracket. This audit authorizes only that CPU study; it does not select
deployment, Gate 5, RDK-X5 or robot use.
