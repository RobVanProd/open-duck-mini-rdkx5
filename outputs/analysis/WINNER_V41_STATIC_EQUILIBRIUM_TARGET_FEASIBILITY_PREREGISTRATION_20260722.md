# Winner-v41 static-equilibrium target feasibility preregistration

- Status: `PREREGISTERED_WINNER_V41_STATIC_EQUILIBRIUM_TARGET_FEASIBILITY`
- Decision: `AUTHORIZE_ONE_CPU_ONLY_FULL_HORIZON_STATIC_TARGET_SCREEN`
- Anchor / plants / duration: `COM_X_NEG / 2 / 250 ticks`
- Grid: `9^3 = 729` fixed bilateral-pitch targets
- Candidate plant cells: `1,458`
- Optimizer / locomotion training / robot: `0 / 0 / 0`

Does one time-invariant target in the reviewed bilateral pitch basis, ramped only by the unchanged graph boundary, hold COM_X_NEG for all 250 ticks under both actuator plants?

This is a full-horizon equilibrium feasibility screen, not receding-horizon
MPC, a runtime wrapper, a checkpoint, or robot clearance.
