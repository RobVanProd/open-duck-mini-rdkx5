# Winner-v60 integrated numeric-guard training preregistration

- Status: `PREREGISTERED_WINNER_V60_INTEGRATED_FIRST_TICK_TEACHER_TRAINING`
- Decision: `AUTHORIZE_ONE_100_UPDATE_INTEGRATED_FIRST_TICK_TEACHER_ARM_ONLY`
- Source / half / final optimizer counts: `454 / 504 / 554`
- Optimizer updates: exact `100`
- Replay guard: `2e-6` (V59 measured `1.125037670135498e-6`)
- Objective and coefficients: exact Winner-v58, unchanged
- Observation/action ABI: unchanged stateful `115+14+64 -> 14+64`
- Attention or flat-transport mechanism: none
- Support cells / robot access authorized now: `0 / 0`

This is a new evidence-selected arm, not a resumption or silent retry of
Winner-v58. It starts from the immutable V57 count-454 snapshot so all 100
metrics, atomic snapshots, and the half/final checkpoints are complete.
