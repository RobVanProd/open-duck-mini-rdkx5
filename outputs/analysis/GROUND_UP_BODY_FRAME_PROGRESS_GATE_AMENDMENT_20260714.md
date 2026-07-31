# Ground-Up Body-Frame Progress Gate Amendment

status: `CORRECTNESS_REPAIR_BEFORE_CORRECTED_PROBE`

The positive locomotion command is defined in body-local x. Reset yaw is
randomized over approximately `[-pi, pi]`, but the evaluator's displacement
hard check used world x. The first oracle shooting implementation inherited the
same ambiguity in its `dx` objective.

Observed reset yaw made the defect concrete: seed `100` started at `-0.4575`
rad and seed `101` at `+2.5973` rad. Optimizing or gating world x therefore asks
the two seeds to move in different directions relative to their bodies.

The correctness repair is frozen before the corrected probe:

- integrate body-local x velocity over control time as
  `body_forward_progress_m`;
- use that value for positive-command displacement and the oracle `dx` term;
- retain world x/y displacement as diagnostics;
- integrate body-local y velocity for the oracle lateral term;
- penalize yaw change from the rollout's initial heading rather than absolute
  world yaw;
- retain duration, local mean velocity, contacts, saturation, rate, and fall
  gates unchanged;
- do not apply a positive-progress requirement to x=`0` runs.

No optimizer weight, horizon, population, elite count, iteration count,
variance, seed, action constraint, or simulator setting changes. The original
world-frame oracle output is invalid implementation evidence, not a failed
source result.

Local CPU only. No Colab, local GPU, iGPU, onboard GPU, RDK-X5, or robot access
is authorized.
