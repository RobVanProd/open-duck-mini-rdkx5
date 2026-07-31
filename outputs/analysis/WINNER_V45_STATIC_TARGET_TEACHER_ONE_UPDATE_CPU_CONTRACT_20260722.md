# Winner-v45 static-target teacher one-update CPU contract

- Status: `PREREGISTERED_WINNER_V45_STATIC_TARGET_TEACHER_ONE_UPDATE_CPU_PROOF`
- Decision: `AUTHORIZE_EXACT_ONE_STATIC_TARGET_TEACHER_OPTIMIZER_UPDATE_ONLY`
- Optimizer count: `251 -> 252`
- Frozen teacher scale: `58.436370849609375`
- Formal support / continuation training / robot: `0 / 0 / 0`

Does exactly one Adam update from Winner-v32 half, using the frozen Winner-v44 training-only teacher gradient and scale, preserve the complete deployable contract while reducing same-batch teacher MSE?

This authorizes one CPU update only. A pass can authorize only a separately
preregistered bounded continuation; it cannot select a checkpoint or grant robot clearance.
