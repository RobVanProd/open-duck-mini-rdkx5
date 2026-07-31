# Winner-v31 cross-worker replay attribution preregistration

- Status: `PREREGISTERED_WINNER_V31_CROSS_WORKER_REPLAY_ATTRIBUTION`
- Decision: `AUTHORIZE_ONE_SAVED_RESULT_ONLY_REPLAY_ATTRIBUTION`
- Maximum per-loss float32 distance: `8 ULP`
- Minimum update-improvement / replay-delta ratio: `10,000x`
- New simulation / optimizer / support / locomotion / robot: `0 / 0 / 0 / 0 / 0`

Are Winner-v30's two exact-replay holds confined to bounded cross-worker float32 variation while the single update, snapshot, and ONNX contracts pass?

The attribution uses only committed V29/V30 JSON evidence. It does not
rerun or rewrite Winner-v30 and cannot itself authorize training or hardware.
