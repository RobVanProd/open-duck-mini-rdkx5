# Winner-v24 baseline-anchored support-gate preregistration

- Status: `PREREGISTERED_WINNER_V24_BASELINE_ANCHORED_SUPPORT_GATE`
- Decision: `AUTHORIZE_ONE_FROZEN_WINNER_V24_248_CELL_GATE_ONLY`
- Population: `124` main cells per checkpoint; `248` total
- Repeats: `32` heldout cells per checkpoint; `64` total
- Predictor: normalized-head MSE must beat constant per plant at both checkpoints
- Selection: every check at both checkpoints; no closest result
- Locomotion / robot access: `0 / 0`

This binds only the frozen count-150 and count-200 training artifacts to
the unchanged reviewed support evaluator. It is not robot clearance.
