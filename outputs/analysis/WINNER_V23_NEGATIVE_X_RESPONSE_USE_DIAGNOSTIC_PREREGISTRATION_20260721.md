# Winner-v23 negative-X response-use diagnostic preregistration

- Status: `PREREGISTERED_WINNER_V23_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC`
- Decision: `AUTHORIZE_ONE_READ_ONLY_20_PAIR_CELL_DIAGNOSTIC_ONLY`
- Exact X-sign pairs / paired cells / physics rollouts: `5 / 20 / 40`
- Checkpoints / actuator plants: `2 / 2`
- Early window: ticks `0..24`, before the earliest tick-27 failure
- Same-input fork changes only `h_in`; it is never applied to physics
- Optimizer / locomotion / robot: `0 / 0 / 0`
- Manual mass/COM measurements: `not required`

This diagnostic chooses among three predeclared CPU-contract branches.
It cannot train, select a deployment checkpoint, weaken support gates,
access the RDK, or clear a policy for the robot.
