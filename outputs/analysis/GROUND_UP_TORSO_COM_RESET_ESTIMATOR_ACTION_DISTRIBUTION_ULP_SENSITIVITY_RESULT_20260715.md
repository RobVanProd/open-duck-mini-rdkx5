# Ground-Up Torso-COM Reset-Estimator Action-Distribution ULP Sensitivity Result — 2026-07-15

## Decision

`ULP_ENVELOPE_BELOW_EXISTING_ACTION_IDENTITY_BOUNDARY`

The CPU-only audit passes every frozen provenance, restore, device, shape,
finiteness, diagnostic, enumeration, and analytic-bound check.

## Result

The measured hosted actor-output envelope is exactly one float32 epsilon,
`1.1920928955078125e-07`, coordinatewise. Across all 56 signed single-
coordinate perturbations and both simultaneous 28-coordinate corners:

- maximum deterministic normalized-action difference:
  `1.18212294092368e-07`;
- maximum distribution-scale difference: `5.500092592480854e-08`;
- maximum physical target difference at 0.25 rad/action:
  `2.9553073523092e-08 rad`;
- maximum diagonal-Gaussian W2 and post-tanh upper bound:
  `4.797397699275616e-07`.

All are below the frozen existing `1e-6` action/distribution identity boundary;
the physical difference is below its exact `2.5e-7 rad` image. Enumeration
also stays inside the analytic box bounds, including the conservative
`sqrt(28) * epsilon = 6.307962682401154e-07` W2 ceiling.

## Interpretation and authority

The original hosted expansion still failed its unchanged `1e-7` raw-output
gate. This result does not rewrite or relax that finding. It establishes that
the complete measured error box is below the repository's established action-
identity boundary after the exact Brax distribution transform.

The frozen decision selects only preregistration of an epsilon-aware hosted
checkpoint-expansion correction. No training, Colab allocation, policy
selection, behavior evaluation, local GPU/iGPU, RDK-X5, runtime, or robot action
is authorized by this result.

