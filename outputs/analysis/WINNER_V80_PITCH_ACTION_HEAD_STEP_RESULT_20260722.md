# Winner-v80 pitch-action-head step result

- Status: `PASS_WINNER_V80_PITCH_ACTION_HEAD_STEP`
- Source / completed optimizer counts: `655 / 656`
- Accepted fraction: `1.0`
- Pitch-teacher loss: `0.007141354493796825 -> 0.006944072898477316`
- Predictor loss: bit-exact at `0.5236514806747437`
- Mutable parameter elements: `384` pitch action-weight values and `6` pitch action-bias values
- All recurrent, predictor, value, distribution, optimizer, and non-pitch elements: bit-exact preserved
- Snapshot SHA-256: `6d0cbb20c0985ba2926471a6d5902d6f969ce2e82bb04471a3ddc308f183ce71`
- ONNX SHA-256: `38e9dd4886593c4e3a996ec74493748138295e9740098a9594020ed152249210`
- Optimizer / continuation / support / robot: `1 / 0 / 0 / 0`

This proves only the selected pitch-head update mechanism. It does not select
a checkpoint or authorize deployment, Gate 5, RDK-X5 access, torque, motion,
or robot clearance.
