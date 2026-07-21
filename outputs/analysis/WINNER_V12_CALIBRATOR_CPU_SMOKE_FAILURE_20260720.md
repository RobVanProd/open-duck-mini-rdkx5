# Winner-v12 calibrator CPU-smoke failure

- Status: `HOLD_WINNER_V12_CALIBRATOR_CPU_SMOKE_NO_RESULT`
- GitHub run: `29802206612`
- Frozen commit: `0340ee946a8783434c919fea614b88f199b38a3b`
- Stage-1 optimizer count recovered from checkpoint: `1`
- Stage-2 optimizer count recovered from checkpoint: `1`
- Raw result: `NOT_WRITTEN`
- Robot clearance: `false`

The corrected smoke reached both rollouts, both one-step updates, checkpoint
save/restore, and ONNX export. It then stopped in the post-update hidden-plant
canary because `ActuatorBridgeModel.step` was called without its required
`dt_s` argument. The recovered checkpoint contains 40 finite arrays, but the
process never wrote the final result and therefore did not prove the complete
frozen check set.

The exact smoke is not rerun and the recovered checkpoint is not selectable.
Full calibrator training, behavior evaluation, and robot work remain blocked.
The only prospective next step is a separately frozen read-only artifact
recovery verifier with zero new optimizer updates and no new checkpoint.
