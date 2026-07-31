# Ground-Up Reset Feasibility Audit Preregistration

status: `PREREGISTERED_BEFORE_EXECUTION`

## Question

The closed viability/command CEM source found no predicted-feasible horizon at
any seed-101 controller tick. Is the seed-101 reset itself unsupported by the
16-tick fitted-bridge contract, or did the CEM proposal fail to expose an
available short-horizon sequence?

## Frozen read-only audit

Run seeds `100` and `101` from their identical reset state, x=`0.074`, for one
16-tick (`0.32 s`) open-loop prediction. Evaluate:

- hold the reset action;
- zero/home action;
- exact-reference actions;
- the executed prefix from the closed viability controller;
- 1,024 deterministic two-tick-block candidates from each of four families:
  reference-centered Gaussian sigma `0.20`, home-centered Gaussian sigma
  `0.20`, independent uniform, and constant-block uniform.

The bank RNG is frozen to `20260714 + reset seed`. All sequences use the fitted
bridge and measured rate bounding. Predicted feasibility reuses the frozen
source contract: no fall, max absolute roll/pitch `<=0.25 rad`, minimum height
`>=0.12 m`, and max action `<0.999`.

Seed 100 is a positive control. Any feasible seed-101 sequence disproves the
hypothesis that the reset has no short-horizon viable action under this model
and selects insufficient CEM proposal/search support. Finding none only reports
`NO_FEASIBLE_SEQUENCE_FOUND_NOT_PROOF_OF_INFEASIBILITY`; a finite bank cannot
prove that the continuous action space is infeasible.

This audit cannot reopen either closed controller, authorize tuning, or
authorize collection/training. Local CPU only; no Colab, GPU, RDK-X5, or robot.
