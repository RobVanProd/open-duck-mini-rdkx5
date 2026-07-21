# Winner-v13 normalized-response Stage-1 preregistration

- Status: `PREREGISTERED_WINNER_V13_NORMALIZED_RESPONSE_STAGE1`
- Decision: `AUTHORIZE_ONE_100_UPDATE_STAGE1_RUN_ONLY`
- Training: `100` encoder-only CPU updates (`2,000,000` episode slots)
- Heldout gate: half/final x 16 configurations x 2 measured plants
- Repeat: all `64` evaluation cells repeated exactly
- Stage-2 / formal support / locomotion / robot access: `0 / 0 / 0 / 0`

The action head is frozen at exact zero. Both checkpoints must beat the
zero normalized predictor under each actuator plant, separate all hidden
plant pairs, reproduce bit-exactly, and preserve the deployable ONNX ABI.
A pass authorizes only a separate support-controller preregistration.
