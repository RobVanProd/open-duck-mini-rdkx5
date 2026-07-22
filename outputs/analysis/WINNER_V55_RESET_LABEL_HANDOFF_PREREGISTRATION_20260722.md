# Winner-v55 reset-label and handoff preregistration

- Status: `PREREGISTERED_WINNER_V55_RESET_LABEL_HANDOFF_DIAGNOSTIC`
- Decision: `AUTHORIZE_ONE_READ_ONLY_RESET_AND_108_CELL_CPU_DIAGNOSTIC_ONLY`
- Preregistration SHA-256:
  `1a37167f0b1867cbad50dff38824ee5104267021b6ab0a81687a58d58ea72d66`.
- Reset rows: `15 configurations x 2 plants = 30`
- Handoff cells: `6 configurations x 2 plants x 9 ticks = 108`
- Optimizer / locomotion / robot: `0 / 0 / 0`

## Frozen question

Winner-v54 proves that the privileged full teacher passes all 12 final
failures while the deployable graph fails all 12. Winner-v23 already proves
that response state is present and used, and Winner-v27 localizes the failure
to early physical-state lock-in. The unresolved possibility is therefore an
input-label conflict at reset rather than missing recurrent transport.

The reset audit hashes the exact float32 policy input—`obs[115]`, zero
`previous_action[14]`, and zero `h_in[64]`—for all 15 V42 teacher-table
configurations under both measured plants. It separately hashes the bounded
first action required by each privileged teacher target. A collision exists
only if one exact input hash maps to multiple exact label hashes; no distance
threshold or rounding is fitted.

The handoff audit runs the six Winner-v54 failure configurations under both
plants at the fixed handoff ticks `0,1,2,4,8,12,16,20,250`. Before the handoff
the unchanged graph controls the plant. At and after the handoff the full V42
teacher replaces all 14 actions before the unchanged graph-authoritative
boundary, while the graph hidden state continues unchanged. Tick `0` must
reproduce Winner-v54's full-teacher endpoint bit-exactly and tick `250` must
reproduce its graph endpoint bit-exactly.

If a reset collision exists and one or more positive handoffs pass all 12
cells, the largest preregistered passing handoff selects only a separate
delayed-teacher mechanism CPU contract. No closest cell, post-hoc handoff,
optimizer update, deployment checkpoint, runtime asset, or robot clearance is
allowed by this diagnostic.

## Authority

This is a read-only CPU observability and feasibility diagnostic. It performs
no policy training, locomotion training, graph export, RDK-X5/robot access,
serial/GPIO/I2C, torque, or motion.
