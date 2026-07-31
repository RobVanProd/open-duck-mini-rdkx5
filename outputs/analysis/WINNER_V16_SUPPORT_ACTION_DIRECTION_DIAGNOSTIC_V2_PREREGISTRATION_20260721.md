# Winner-v16 support action-direction diagnostic v2 preregistration

- Status: `PREREGISTERED_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC_V2`
- Decision: `AUTHORIZE_ONE_COMPARATOR_CORRECTED_CPU_ONLY_DIRECTION_DIAGNOSTIC`
- Screen: unchanged baseline plus six bilateral interventions
- Population: `168` CPU-only cells
- Optimizer / locomotion / robot: `0 / 0 / 0`

The sole correction is the baseline verifier: policy/observer traces and
gate-setting fields remain exact, while finite derived terminal/episode
doubles have a preregistered `1e-12` absolute tolerance.

The intervention population, offset, checkpoints, configurations, plants,
thresholds, and no-closest-result selection rule are unchanged.
