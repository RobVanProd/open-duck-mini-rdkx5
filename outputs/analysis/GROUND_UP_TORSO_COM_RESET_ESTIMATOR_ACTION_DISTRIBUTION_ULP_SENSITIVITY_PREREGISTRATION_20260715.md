# Ground-Up Torso-COM Reset-Estimator Action-Distribution ULP Sensitivity Preregistration — 2026-07-15

## Question and scope

The valid hosted T4 diagnostic measured a maximum actor-output difference of
exactly `1.1920928955078125e-07` at z=-1/0/+1, with zero critic error and every
structural/save check passing. This CPU-only read-only audit asks whether an
arbitrary actor-distribution-parameter perturbation inside that measured
coordinatewise envelope can cross an already-established action numerical-
identity boundary.

This is not a post-hoc relaxation of the original `1e-7` expansion gate. That
gate failed and remains recorded as failed. This study may select only a
separately preregistered expansion-method correction.

## Frozen inputs

- protected source archive SHA-256:
  `ae4c631a6ce1c0b36c3231113740acc6c1b8a463c0911ce7cad30b8f8d8ca60f`;
- protected checkpoint:
  `ground_up_tracking_tail_outputs/T2_EQUAL/2026_07_14_190425_1024000`;
- reference-residual actor source SHA-256:
  `546f375fa3c2f34158f49f1ac07cdc5ff6dc41d1a94322f4334bd48835911630`;
- hosted expansion source SHA-256:
  `a3e5fc38994cecd65d89fdc6b9ede23c2433e917b84583dfcced42c161e79d67`;
- corrected diagnostic JSON SHA-256:
  `6f734d595b207c357f6affb201176db38dc5c5911670a02270c80d4f374bb7b0`;
- Brax 0.14.2 distribution source SHA-256:
  `3f9375b179f55ebb76fb337db610fafbf60b53b3d329a2fbbfae365836b1d220`;
- JAX/JAXLIB 0.8.2, CPU backend only.

The actor has 28 outputs for 14 actions. Under the exact frozen Brax
`NormalTanhDistribution`, outputs 0:14 are Gaussian locations, outputs 14:28
become scales through `softplus(x) + 0.001`, and deterministic action is
`tanh(location)`.

## Frozen method

1. Extract only the protected checkpoint and restore it on CPU. Reproduce the
   exact old 115-D deterministic test observation used by the hosted expansion:
   state `linspace(-.25,.25,115)` and privileged state
   `linspace(-.5,.5,226)`. Require finite 28-D actor output and finite critic.
2. Require the diagnostic to be valid, to contain z=-1/0/+1 in order, and to
   report the same actor envelope `epsilon = 2^-23` and zero critic error in
   every cell.
3. Treat every possible hosted actor difference as lying in the closed box
   `|delta_i| <= epsilon`. Enumerate each of the 28 coordinates at both
   `+epsilon` and `-epsilon`, plus simultaneous all-positive and all-negative
   corners. Do not use a recovered or guessed error sign or coordinate.
4. For every enumerated perturbation, compute the exact Brax pre-tanh location
   and scale, deterministic post-tanh mode, physical target displacement at
   the frozen `0.25 rad/action` scale, and diagonal-Gaussian 2-Wasserstein
   distance `sqrt(sum(delta_loc^2 + delta_scale^2))`. Because tanh is
   1-Lipschitz, this is also a rigorous upper bound on post-tanh W2.
5. Also record analytic box bounds: mode L-infinity `<=epsilon`, scale
   L-infinity `<=epsilon`, target L-infinity `<=0.25*epsilon`, and W2
   `<=sqrt(28)*epsilon`. Numerical enumeration must not exceed the analytic
   bounds by more than `1e-12`.

The unchanged comparison boundary is `1e-6` normalized action/distribution
units, already used throughout the ground-up actor reconstruction, ONNX fork,
and hard-vector contracts. The physical target boundary is its exact
`0.25 rad/action` image, `2.5e-7 rad`.

## Frozen decision

- `ULP_ENVELOPE_BELOW_EXISTING_ACTION_IDENTITY_BOUNDARY` only if all source,
  device, shape, finiteness, diagnostic, enumeration, and analytic-bound checks
  pass; maximum deterministic-action L-infinity, scale L-infinity, and W2 are
  each `<=1e-6`; and maximum target displacement is `<=2.5e-7 rad`.
- `ULP_ENVELOPE_MATERIALLY_CROSSES_ACTION_IDENTITY_BOUNDARY` if the audit is
  otherwise valid but any of those four boundaries is exceeded.
- `INVALID_ULP_SENSITIVITY_AUDIT` for any provenance, reconstruction,
  completeness, finiteness, backend, or analytic-bound failure.

A below-boundary result selects only preregistration of an epsilon-aware hosted
checkpoint-expansion correction. It does not itself change the original result,
authorize training, allocate Colab, or select a policy. A material-crossing
result closes this exact checkpoint-surgery route. No behavior evaluation,
local GPU/iGPU, RDK-X5, runtime, robot, torque, or motor action is authorized.

