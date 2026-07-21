# Winner-v22 normalized-predictor support-gate preregistration

- Status: `PREREGISTERED_WINNER_V22_NORMALIZED_PREDICTOR_SUPPORT_GATE`
- Decision: `AUTHORIZE_ONE_FROZEN_CORRECTED_COORDINATE_248_CELL_GATE_ONLY`
- Population: `124` main cells per checkpoint; `248` total
- Repeats: `32` heldout cells per checkpoint; `64` total
- Predictor: corrected normalized-head MSE must beat constant per plant at both checkpoints
- Selection: every check at both checkpoints; no closest result
- Locomotion / robot access: `0 / 0`

Physical support mechanics remain unchanged. The only scoring correction
is the exact normalized-head-to-raw affine projection proven by unit tests.
