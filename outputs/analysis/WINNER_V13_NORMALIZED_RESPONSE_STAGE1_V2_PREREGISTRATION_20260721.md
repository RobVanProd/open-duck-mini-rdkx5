# Winner-v13 normalized-response Stage-1 v2 preregistration

- Status: `PREREGISTERED_WINNER_V13_NORMALIZED_RESPONSE_STAGE1_V2`
- Decision: `AUTHORIZE_ONE_FRESH_100_UPDATE_STAGE1_V2_RUN_ONLY`
- Training: fresh `100` encoder-only CPU updates at exact `1e-4`
- Heldout gate: half/final x 16 configurations x 2 measured plants
- Repeat: all `64` evaluation cells repeated exactly
- Stage-2 / formal support / locomotion / robot: `0 / 0 / 0 / 0`

Training is unchanged from the invalid first run. Only the declared
learning rate and the pre-proven same-input ONNX checker are corrected.
A pass authorizes only a separate support-controller preregistration.
