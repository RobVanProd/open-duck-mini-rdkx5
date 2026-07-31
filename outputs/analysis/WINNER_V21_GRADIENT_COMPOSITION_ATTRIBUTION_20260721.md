# Winner-v21 gradient-composition attribution

- Status: `PASS_WINNER_V21_GRADIENT_COMPOSITION_ATTRIBUTION`
- Decision: `PREREGISTER_EXPLICITLY_COMPOSED_TWO_UPDATE_CPU_PROOF`
- Frozen predictor scale: `8.393629541414427e-11`
- Absolute / relative gradient difference: `1.430511474609375e-06 / 1.0176642082613167e-07`
- Passing checks: `16 / 17`; optimizer updates: `0`
- Threshold relaxed / source relabelled / rerun: `false / false / false`
- Flat-transport equation: `not selected`

The next proof composes the optimizer gradient tree explicitly from the
two separately verified gradients. It does not change the loss, scale,
population, action boundary, ABI, or authority boundary.
