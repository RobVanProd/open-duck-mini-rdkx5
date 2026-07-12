# Ground-Up Reference Policy Search Preregistration

status: `PREREGISTERED_NO_COMPUTE_SPENT`

## Objective

Train a new closed-loop policy that is more robust than
`policy/BEST_WALK_ONNX_2.onnx` while respecting the measured RDK-X5 actuator
contract. Existing learned policies are comparison controls only; they are not
teachers or warm starts for the new search.

Frozen baseline SHA256:

`3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067`

The polynomial reference remains a tracking target, not an open-loop
controller. Prior evidence shows raw and projected open-loop playback fails to
produce reliable propulsion, while the published closed-loop policy does. The
search must therefore learn feedback corrections around the reference rather
than clone its joint targets directly.

## Canonical sources

- Playground control commit: `b9be205ac64488c23504ca42e5ec790337adeec3`
- reference SHA256: `5850c0610ed89e2860e7047f9ee27d8412462e1199752952c3c2a0efd2cb7a25`
- observation/action contract: `obs[1,101] -> continuous_actions[1,14]`
- control rate: `50 Hz`
- action scale: `0.25 rad`
- calibrated fit: `outputs/analysis/fixed_target_p30_actuator_fit_20260712.json`
- pitch-chain indices: `2,3,4,11,12,13`
- measured limits: `1.50,1.50,1.75,1.25,1.00,1.25 rad/s`

Local Playground modifications are not silently inherited. Search jobs must be
constructed from the pinned control commit plus an explicit, hashed patch.

## Recipe families

The first search compares mechanisms, not tiny reward perturbations:

1. `upstream_control`: canonical reference-imitation PPO.
2. `reference_conditioned_final_action`: actor receives the envelope-projected
   reference action as an explicit policy feature and emits final actions.
3. `phase_moe_final_action`: shared experts with smooth command/phase routing
   emit final actions; no independently trained or hard-switched phase heads.
4. `recurrent_final_action`: small recurrent state for contact/actuator history,
   trained closed-loop rather than by supervised BC, emitting final actions.
5. `imitation_decay`: canonical policy whose imitation weight decays only after
   nominal gait metrics are reached.
6. `symmetric_critic_ablation`: both actor and critic see the canonical
   101-vector. This is compared with the upstream control, which already uses a
   privileged 212-value asymmetric critic; it is not a duplicate family.

Architecture audit amendment before family search: a recurrent finalist uses
policy ABI v2 (`obs,state_in -> action,state_out`) and requires the new RDK
runtime. Stateless finalists retain ABI v1 (`obs -> action`). Reference-
conditioned families must emit final actions. The projected reference is an
input feature under policy ABI v2, not a post-policy action wrapper.

No command-gated wrapper, runtime limiter, existing-policy behavior prior,
DAgger teacher, supervised student, or policy warm start is part of this
search.

## Curriculum shared by every family

1. Nominal flat backlash reference tracking.
2. Measured actuator delay/tau/velocity model.
3. Zero-command and positive-command mixture.
4. Sensor, mass, friction, and initialization variation.
5. Mild pushes.
6. Rough terrain last.

A family advances only if it retains every earlier stage. Later robustness
cannot compensate for losing nominal walking or x=0 semantics.

## Multi-fidelity search

The search uses deterministic asynchronous successive halving. Before setting
timesteps, run one canonical-control accelerator calibration capped at three
Colab compute units. Record environment steps, wall time, accelerator type,
and compute units consumed. Rung sizes are then derived from measured
steps-per-unit; they are not guessed in advance.

Protected rule: `upstream_control` remains through the first medium rung even
if its early learning curve is slower. Other families are ranked only after a
minimum gait-emergence window measured from the control calibration.

The shared PPO recipe is itself searched before policy mechanisms, under
`outputs/analysis/GROUND_UP_PPO_RECIPE_SEARCH_PREREGISTRATION_20260712.md`.
That bounded one-factor screen receives at most 15 of the 35 broad/medium
search units. At most two validated recipes advance to the mechanism-family
comparison. This amendment was made before recipe or family-search compute;
the earlier calibration/probe runs are controls and are not ranked candidates.

Elimination order:

1. NaN, export failure, contract mismatch, or repeated early termination.
2. Standing collapse: insufficient single support and forward progress.
3. x=0 drift or nonzero gait activation.
4. measured velocity-envelope excess.
5. tracking, pitch, height, contact, and fall metrics.
6. robustness score only after all hard gates pass.

Training reward is never an advancement metric.

## Frozen evaluation structure

Discovery seeds, search seeds, and final held-out seeds must be disjoint. Their
exact lists are emitted once by the deterministic search manifest before the
first accelerator job and cannot be changed afterward.

Every evaluated checkpoint includes:

- commands `x=0.00` and `x=0.08`;
- nominal flat backlash;
- calibrated actuator bridge;
- positive-command motion, tracking, pitch, height, support, and velocity
  envelope metrics;
- zero-command drift and gait-activation metrics;
- ONNX/checkpoint numerical equivalence.

Only medium-rung survivors receive push and rough-terrain evaluation. Finalists
are compared with `BEST_WALK_ONNX_2` on the same held-out seeds and conditions.

## Definition of “more robust”

A finalist must first pass every hard safety and behavior gate. It must then:

1. have fewer held-out falls/terminations than `BEST_WALK_ONNX_2` across the
   frozen combined condition suite;
2. retain positive-command motion floors and true x=0 behavior;
3. have zero measured pitch-chain velocity excess;
4. show no statistically or operationally material regression in nominal
   tracking, pitch, height, or bilateral support; and
5. improve at least one preregistered robustness condition rather than merely
   tie the baseline aggregate.

If no candidate meets all five clauses, the search has no winner and nothing
is cleared for robot use.

## Compute budget

Hard ceiling: `94` Colab compute units total.

- calibration: maximum `3` units;
- broad and medium search: maximum `35` units;
- finalist training: maximum `38` units;
- held-out evaluation/export verification: maximum `12` units;
- interruption reserve: `6` units.

Unused units in one category may move forward only; the total may never exceed
94. A job stops before its category cap. Failed setup time counts against the
budget. No second job is launched until the previous job's unit usage and
artifacts are recorded.

## Hardware boundary

This search authorizes local CPU work and budgeted Colab work only after its
contract tooling passes. It does not authorize local GPU/iGPU use, RDK access,
SSH, staging, deployment, or motor tests. A winning policy still requires a
separate formal offline-clearance artifact and a separately designed RDK-X5
runtime contract before hardware work can begin.
