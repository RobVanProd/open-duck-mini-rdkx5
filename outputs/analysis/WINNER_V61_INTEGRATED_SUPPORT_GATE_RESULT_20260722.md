# Winner-v61 integrated support-gate result

- Status: `HOLD_WINNER_V61_INTEGRATED_SUPPORT_GATE`
- Decision: `DO_NOT_SELECT_WINNER_V60_DEPLOYMENT_POLICY`
- Main cells / heldout repeats executed: `248 / 64`
- Half count `504`: `11 / 124` main cells fail
- Final count `554`: `13 / 124` main cells fail
- Failure predicate: exclusively `roll_pitch`
- Action chain / JAX-ONNX / repeats / context / predictor checks: all pass
- Selected checkpoint: none
- Robot clearance: `false`
- Result SHA-256: `a238ea4511c2c507b32d00c4c898953ee5ed5617399079a3993bdf71a5257255`

The gate is evidence-complete, not interrupted. Every failed cell crosses the
unchanged roll/pitch bound while base height, contacts, current, overcurrent
streak, torque, finite-state, action-chain, graph-agreement, repeatability,
context-separation, and predictor checks remain green. The failures occur in
both actuator plants and persist at both checkpoints, including the COM_X_NEG,
COM_CORNER_01, COM_CORNER_03, DISCOVERY_03, HELDOUT_04, and HELDOUT_09 regions;
the final checkpoint additionally fails COM_CORNER_00.

The all-or-nothing persistence rule therefore selects no ONNX. This result
closes Winner-v60 as a deployment candidate and authorizes no robot or RDK
execution. Any next policy mechanism requires a separate evidence-selected
diagnostic and preregistration.
