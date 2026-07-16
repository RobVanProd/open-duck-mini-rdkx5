# Oracle COM Receding-Horizon Result

status: `PASS_PREREGISTERED_STAGES_A_B_COMPLETE`

decision: `HOLD_LOCAL_AUTHORITY_NOT_COMPOSABLE`

The preregistered CPU-only viability-funnel study completed Stage A and Stage
B. Stage C was not run because the frozen Stage-B advancement rule failed.

## Evidence

- All 24 committed failing moving endpoint cells were localized against their
  matched nominal traces.
- 298 exact four-tick cadence states were frozen before sequence optimization;
  49 belonged to the fixed P30/x=.077 two-sign/two-checkpoint design subset.
- X_NEG first meets the three-tick backward-velocity rule at tick 0 in every
  cell. X_POS first meets the runaway rule at ticks 23-26. Contact deviations
  occur later, so neither failure is explained by a contact mismatch alone.
- At horizon 8, 5/49 states have a valid bounded sequence.
- At horizon 16, 4/49 states have a valid bounded sequence.
- At horizon 32, 0/49 states have a valid bounded sequence.
- No horizon works from every state. The earliest state with no valid sequence
  is tick 4 for X_NEG and tick 12 for X_POS.
- Forty of 49 states have no valid sequence at any frozen horizon. No closest
  state, checkpoint, sign, horizon or sequence is promoted.

This distinguishes isolated local corrective authority from a viability
funnel. Small pulses can improve an eight-tick state, but within the frozen
six-joint, +/-0.08 residual limits and nominal velocity/safety envelope that
authority cannot be composed through the pre-failure trajectory. The result
does not establish that every possible nonlinear controller lacks authority;
it closes this exact bounded receding-horizon formulation.

The frozen hard stop therefore prohibits the online planner and 48-cell Stage-C
matrix. No new formal traces were generated. Training, PPO, hosted compute,
GPU/iGPU, RDK-X5, robot access, deployment and policy overwrite remain
unauthorized. Robot clearance remains `NO`.

Final explicit decision token: `HOLD_LOCAL_AUTHORITY_NOT_COMPOSABLE`
