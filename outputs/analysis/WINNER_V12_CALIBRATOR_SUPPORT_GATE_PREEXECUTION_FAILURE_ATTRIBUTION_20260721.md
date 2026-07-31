# Winner-v12 support-gate pre-execution failure attribution

- Status: `ATTRIBUTED_WINNER_V12_SUPPORT_GATE_PREEXECUTION_FAILURE`
- Failed run: `29815413956`, attempt `1`
- Failed launch commit: `b2231429cd3d0618cf03c8f68a1414f3cac6f650`
- Completed formal / repeat cells: `0 / 0`
- Locomotion training / robot access: `0 / 0`
- Formal result artifact: `NOT_PRODUCED`

The workflow passed setup, source-manifest, training-artifact, checkpoint, model,
and fit verification. The first Episode constructor then received the full
training plan instead of the separately frozen calibrator design and raised
`KeyError: 'hidden_configuration_domain'` before one cell completed.

The failed workflow is not rerun and supplies no policy result. The only
authorized correction is to load and hash-bind the existing calibrator-design
preregistration, prove that binding in the zero-cell contract again, and then
freeze a fresh formal launch without changing the policy, population, seeds,
duration, simulator, thresholds, or selection rule.
