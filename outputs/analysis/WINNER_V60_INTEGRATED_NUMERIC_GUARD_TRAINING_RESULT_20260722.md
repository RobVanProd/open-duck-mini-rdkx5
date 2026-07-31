# Winner-v60 integrated numeric-guard training result

- Status: `PASS_WINNER_V60_INTEGRATED_FIRST_TICK_TEACHER_TRAINING_ARTIFACT`
- Decision: `AUTHORIZE_INTEGRATED_FIRST_TICK_TEACHER_SUPPORT_GATE_PREREGISTRATION_ONLY`
- Source / half / final optimizer counts: `454 / 504 / 554`
- Completed updates / atomic snapshots / scheduled slots: `100 / 100 / 2,000,000`
- Passing result checks: `23 / 23`
- Maximum hidden replay error: `1.6093254089355469e-6` at count `490` (bound `2e-6`)
- First / half / final first-tick loss: `0.0040571862 / 0.0036761079 / 0.0036237685`
- Half snapshot SHA-256: `efbf2ecf5ffa892c3c51251ccd9d87a6f9c70adbbd15c0d913ed9d04e14c06de`
- Half ONNX SHA-256: `37e483f533e606e38257a16efdde341cd8725b798a44d21b8eacc21c57af0a02`
- Final snapshot SHA-256: `c8eb7032dea20c2c197ab03f7544ea9be92d2694a3a3414656941978117d8802`
- Final ONNX SHA-256: `4a6386d8dddfcc441f90bce4f64d7307144446bb3032c171c22cb2e299ac3939`
- Result SHA-256: `50622331dea979369bdea7bb001cd168f94162270a0ea0ec1bdb4d6d9f6b8b57`
- Support cells / robot access: `0 / 0`

All 100 action-boundary, reward, failure-transition, teacher, gradient,
successor-mask, finite-state, snapshot-readback, and replay checks pass. Both
stateful graphs preserve the `115+14+64 -> 14+64` ABI, graph-authoritative
bounds, exact previous-action chain, absence of training-only tensors, and JAX
agreement below `1e-7`.

This is training evidence, not policy selection or robot clearance. It
authorizes only a separately preregistered unchanged half/final offline support
gate. Neither checkpoint is deployable until that persistence gate selects it.
