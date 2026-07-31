# Winner-v13 Stage-1 invalid-decision attribution

- Status: `INVALID_WINNER_V13_STAGE1_DECISION_CONTRACT`
- Decision: `DO_NOT_ADVANCE_REVALIDATE_CORRECTED_CHECKER`
- Training completed: `100` updates; additional training here: `0`
- Stage-2 / locomotion / robot access: `0 / 0 / 0`

The prediction, plant-separation, repeatability, and standard ONNX
checks passed at half and final, but the decision is not promotable.
The action checker ignored the inherited slew projection, the hidden
checker accumulated independent backend state, and the declared learning
rate (`3e-4`) disagreed with the executed frozen constant (`1e-4`).
A corrected zero-cell checker contract and a fresh preregistered run are
required before any support-controller training may be considered.
