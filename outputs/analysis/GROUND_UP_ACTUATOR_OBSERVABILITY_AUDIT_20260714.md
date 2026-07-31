# Ground-Up Actuator-State Observability Audit

status: `PASS_SELECT_APPLIED_TARGET_SLOT`

The exact 115-dimensional reference-residual actor observation is not Markov
for the fitted first-order actuator bridge. The bridge transition depends on
its previous applied target, but that state is absent from both actor and critic
observations.

The audit also rules out unnecessary mechanisms:

- The actor already receives three successive sent-action states. They
  reconstruct the bridge's discrete 2-3 tick delayed-target history within
  `5.14984e-8 rad`; missing delay history is not the problem.
- Observation indices `83:97` contain the absolute sent motor target, while
  indices `41:55` contain `(sent-home)/action_scale`. Those two 14-D fields are
  affine duplicates within `5.14984e-8 rad`; the absolute sent-target slot adds
  no causal information.
- A controlled fork held the complete 115-D actor observation and requested
  action identical while changing only hidden bridge applied target by
  `0.04 rad`. The next physics control differed by `0.0299975 rad`, next qpos by
  `0.0028491 rad`, and next actor observation by `1.95534`. This directly proves
  observation aliasing, not merely correlation.

The evidence-selected mechanism is therefore to replace only the redundant
absolute sent-target observation slot with the deterministic bridge-applied
target. Sent target remains recoverable from `last_act`; the three sent-action
fields continue to cover delay; the applied slot supplies the missing lag state.
Observation size stays 115, so the existing reference-residual architecture and
checkpoint tree remain compatible. True recurrence is not selected by this
audit.

The eventual RDK runtime would need to maintain the same deterministic applied-
target estimator from sent targets. That is a later software-design constraint,
not authorization to touch the RDK or robot now.

Machine-readable evidence:
`outputs/analysis/ground_up_actuator_observability_audit.json`.

This audit authorizes no training or accelerator use. A separate
preregistration and CPU contract must prove exact slot semantics, protected
restore, finite update, and unchanged stateful ONNX interface first.

