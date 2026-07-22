# Winner-v57 first-tick teacher one-update result

- Status: `PASS_WINNER_V57_FIRST_TICK_TEACHER_ONE_UPDATE_CPU_PROOF`
- Decision: `AUTHORIZE_INTEGRATED_FIRST_TICK_TEACHER_CONTINUATION_PREREGISTRATION_ONLY`
- Result SHA-256:
  `66c075dd291a016f4ed07d6486516faf61bfc44ab2d5caeb1c1480ccb63351d2`.
- Optimizer count: `453 -> 454`
- Loss: `0.004075534176081419 -> 0.0040571861900389194`
- Pitch RMS: `0.0957130640745163 -> 0.09555895626544952`
- Snapshot SHA-256: `e111b81e8e82cae50832d8518b673a78953f74902563bc10a449ee2609e4f3c0`
- ONNX SHA-256: `3fdbac1f1868e157f6e67061ff9e7fea81623ca936a3e1bc5e4a8f4827d64c8e`
- Continuation / support / robot: `0 / 0 / 0`

All 17 frozen checks pass. The proof recomputes the Winner-v56 loss and
gradient exactly, retains the count-453 Adam moments, and changes all 12
trainable leaves in the single update. The source parameters and optimizer
remain unchanged.

Same-batch evidence improves in every required view:

| Metric | Before | After |
| --- | ---: | ---: |
| total reset MSE | 0.004075534176081419 | 0.0040571861900389194 |
| raw reset MSE | 0.0040754894725978374 | 0.004057141020894051 |
| quantized reset MSE | 0.0040755788795650005 | 0.004057232290506363 |
| pitch RMS | 0.0957130640745163 | 0.09555895626544952 |
| non-pitch RMS | 0.01616910845041275 | 0.01585693657398224 |

The new snapshot restores parameters, optimizer moments/count, target mean,
and target standard deviation exactly. The non-selected 54,896-byte graph
contains no teacher or privileged token, preserves the exact stateful
`115+14+64 -> 14+14+64` ABI and previous-action chain, and agrees with JAX
within `8.731149137020111e-11`.

This artifact is an optimizer/mechanics proof, not a candidate selection. It
authorizes only a prospective integrated continuation that combines the
first-tick term with the unchanged PPO, predictor, prefix-anchor, and
full-horizon teacher objectives. It grants no support evaluation or robot
clearance.
