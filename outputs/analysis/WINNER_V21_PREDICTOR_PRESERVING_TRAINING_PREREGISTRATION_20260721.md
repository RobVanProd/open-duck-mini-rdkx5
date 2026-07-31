# Winner-v21 predictor-preserving training preregistration

- Status: `PREREGISTERED_WINNER_V21_PREDICTOR_PRESERVING_TRAINING`
- Decision: `AUTHORIZE_ONE_100_UPDATE_PREDICTOR_PRESERVING_ARM_ONLY`
- Source: identical Winner-v13 Stage-1 update-100 snapshot
- Updates / checkpoints: `100 / 50,100`
- Frozen predictor scale evaluations: `0`
- Formal support / locomotion / robot: `0 / 0 / 0`
- Flat-transport equation: `not used`

This is one causal arm. It adds the existing three predictor leaves to
Winner-v20's nine trainable leaves and consumes the frozen explicit
per-leaf gradient sum proven by the two-update CPU contract. No scale
recalculation, sweep, ABI change, support gate, or robot access occurs.
